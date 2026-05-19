"""
취업 정보 요약 사이트 — Python 서버 (표준 라이브러리만 사용)
실행: python server.py
접속: http://localhost:3000
"""
import json
import os
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 3000))
API_KEY = ""

# .env 파일에서 API 키 읽기
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("WORK24_API_KEY="):
                API_KEY = line.split("=", 1)[1].strip()
            elif line.startswith("PORT="):
                PORT = int(line.split("=", 1)[1].strip())

USE_MOCK = not API_KEY or API_KEY == "your_api_key_here"

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}


# ── 샘플 데이터 ──────────────────────────────────────────────

def mock_jobs(keyword, region, page, page_size):
    all_items = [
        {"id": "J001", "title": "프론트엔드 개발자 (React)", "company": "카카오", "job": "IT개발·데이터", "region": "경기 성남시", "salary": "연봉 4,000~6,000만원", "career": "경력 3년↑", "education": "대졸↑", "deadline": "2026-06-30", "url": "#"},
        {"id": "J002", "title": "백엔드 서버 개발자", "company": "네이버", "job": "IT개발·데이터", "region": "경기 성남시", "salary": "연봉 5,000~8,000만원", "career": "경력 5년↑", "education": "대졸↑", "deadline": "2026-06-15", "url": "#"},
        {"id": "J003", "title": "마케팅 콘텐츠 기획자", "company": "쿠팡", "job": "마케팅·광고·홍보", "region": "서울 강남구", "salary": "연봉 3,500~5,000만원", "career": "경력 2년↑", "education": "대졸↑", "deadline": "2026-06-20", "url": "#"},
        {"id": "J004", "title": "데이터 분석가 (신입 가능)", "company": "배달의민족", "job": "IT개발·데이터", "region": "서울 송파구", "salary": "연봉 3,000~4,500만원", "career": "신입·경력", "education": "대졸↑", "deadline": "2026-07-10", "url": "#"},
        {"id": "J005", "title": "UX/UI 디자이너", "company": "토스", "job": "디자인", "region": "서울 강남구", "salary": "연봉 4,500~7,000만원", "career": "경력 3년↑", "education": "대졸↑", "deadline": "2026-06-25", "url": "#"},
        {"id": "J006", "title": "영업 관리 담당자", "company": "삼성전자", "job": "영업·고객상담", "region": "경기 수원시", "salary": "연봉 3,800~5,500만원", "career": "경력 1년↑", "education": "대졸↑", "deadline": "2026-07-05", "url": "#"},
        {"id": "J007", "title": "인사·총무 담당자", "company": "LG전자", "job": "인사·교육·훈련", "region": "서울 영등포구", "salary": "연봉 3,500~5,000만원", "career": "경력 2년↑", "education": "대졸↑", "deadline": "2026-06-18", "url": "#"},
        {"id": "J008", "title": "회계·재무 담당자", "company": "SK하이닉스", "job": "회계·세무·재무", "region": "경기 이천시", "salary": "연봉 4,000~6,000만원", "career": "경력 3년↑", "education": "대졸↑", "deadline": "2026-07-20", "url": "#"},
        {"id": "J009", "title": "고객 서비스 매니저", "company": "현대자동차", "job": "영업·고객상담", "region": "서울 서초구", "salary": "연봉 3,200~4,500만원", "career": "신입·경력", "education": "초대졸↑", "deadline": "2026-06-28", "url": "#"},
        {"id": "J010", "title": "AI 머신러닝 엔지니어", "company": "네이버클라우드", "job": "IT개발·데이터", "region": "경기 성남시", "salary": "연봉 6,000~1억원", "career": "경력 5년↑", "education": "석사↑", "deadline": "2026-08-01", "url": "#"},
        {"id": "J011", "title": "모바일 앱 개발자 (iOS)", "company": "카카오페이", "job": "IT개발·데이터", "region": "서울 강남구", "salary": "연봉 5,000~8,000만원", "career": "경력 3년↑", "education": "대졸↑", "deadline": "2026-07-15", "url": "#"},
        {"id": "J012", "title": "공급망 관리(SCM) 담당", "company": "롯데쇼핑", "job": "생산·품질·유통", "region": "서울 송파구", "salary": "연봉 3,500~5,000만원", "career": "경력 2년↑", "education": "대졸↑", "deadline": "2026-06-30", "url": "#"},
    ]
    if keyword:
        all_items = [j for j in all_items if keyword in j["title"] or keyword in j["company"] or keyword in j["job"]]
    if region:
        all_items = [j for j in all_items if region in j["region"]]
    start = (page - 1) * page_size
    return {"total": len(all_items), "page": page, "pageSize": page_size, "items": all_items[start:start + page_size], "isMock": True}


def mock_training(keyword, region, page, page_size):
    all_items = [
        {"id": "T001", "title": "AWS 클라우드 실무 과정", "institution": "한국IT교육원", "region": "서울", "startDate": "2026-06-02", "endDate": "2026-08-29", "cost": "무료 (국비)", "ncs": "정보기술개발", "url": "#"},
        {"id": "T002", "title": "Python 데이터 분석 부트캠프", "institution": "패스트캠퍼스", "region": "서울", "startDate": "2026-06-09", "endDate": "2026-09-26", "cost": "무료 (국비)", "ncs": "빅데이터분석", "url": "#"},
        {"id": "T003", "title": "UI/UX 디자인 실무 과정", "institution": "디자인 아카데미", "region": "경기", "startDate": "2026-06-16", "endDate": "2026-09-12", "cost": "무료 (국비)", "ncs": "디자인", "url": "#"},
        {"id": "T004", "title": "스마트 물류·유통 전문가 양성", "institution": "한국유통교육원", "region": "인천", "startDate": "2026-07-01", "endDate": "2026-10-24", "cost": "무료 (국비)", "ncs": "물류", "url": "#"},
        {"id": "T005", "title": "디지털 마케팅 SNS 전략가 과정", "institution": "마케팅 인사이트", "region": "서울", "startDate": "2026-06-23", "endDate": "2026-08-15", "cost": "무료 (국비)", "ncs": "마케팅", "url": "#"},
        {"id": "T006", "title": "Java 풀스택 개발자 양성", "institution": "코드팩토리", "region": "경기", "startDate": "2026-07-07", "endDate": "2026-12-19", "cost": "무료 (국비)", "ncs": "정보기술개발", "url": "#"},
        {"id": "T007", "title": "바리스타 2급 자격증 취득 과정", "institution": "한국직업능력개발원", "region": "부산", "startDate": "2026-06-10", "endDate": "2026-08-05", "cost": "50,000원", "ncs": "조리·식음료", "url": "#"},
        {"id": "T008", "title": "회계 실무 및 ERP 운용", "institution": "경리나라교육센터", "region": "서울", "startDate": "2026-06-30", "endDate": "2026-09-19", "cost": "무료 (국비)", "ncs": "회계·감사", "url": "#"},
    ]
    if keyword:
        all_items = [t for t in all_items if keyword in t["title"] or keyword in t["institution"]]
    if region:
        all_items = [t for t in all_items if region in t["region"]]
    start = (page - 1) * page_size
    return {"total": len(all_items), "page": page, "pageSize": page_size, "items": all_items[start:start + page_size], "isMock": True}


def mock_companies(keyword, page, page_size):
    all_items = [
        {"id": "C001", "name": "한국항공우주산업(KAI)", "industry": "항공기·우주선 제조업", "region": "경남 사천시", "employees": "4,200명", "sales": "3조 2,000억", "welfare": "의료비 지원, 자녀학자금, 사내어린이집", "url": "#"},
        {"id": "C002", "name": "세메스", "industry": "반도체 장비 제조업", "region": "충남 천안시", "employees": "2,800명", "sales": "1조 8,000억", "welfare": "주택자금 대출, 스톡옵션, 해외연수", "url": "#"},
        {"id": "C003", "name": "오스템임플란트", "industry": "의료기기 제조업", "region": "서울 강서구", "employees": "3,100명", "sales": "8,500억", "welfare": "성과급, 복지포인트, 유연근무제", "url": "#"},
        {"id": "C004", "name": "더존비즈온", "industry": "소프트웨어 개발업", "region": "강원 춘천시", "employees": "2,300명", "sales": "5,000억", "welfare": "원격근무, 리프레시 휴가, 도서비 지원", "url": "#"},
        {"id": "C005", "name": "에코프로비엠", "industry": "2차전지 소재 제조업", "region": "충북 청주시", "employees": "1,900명", "sales": "3조 1,000억", "welfare": "우리사주, 주택자금 지원, 사내대학", "url": "#"},
        {"id": "C006", "name": "한미반도체", "industry": "반도체 장비 제조업", "region": "경기 하남시", "employees": "980명", "sales": "6,500억", "welfare": "성과급, 의료비 지원, 체력단련비", "url": "#"},
        {"id": "C007", "name": "레인보우로보틱스", "industry": "로봇 제조업", "region": "대전 유성구", "employees": "420명", "sales": "500억", "welfare": "스톡옵션, 교육훈련비, 유연근무제", "url": "#"},
        {"id": "C008", "name": "알테오젠", "industry": "바이오의약품 제조업", "region": "대전 유성구", "employees": "510명", "sales": "1,200억", "welfare": "연구개발비 지원, 리프레시 휴가, 건강검진", "url": "#"},
    ]
    if keyword:
        all_items = [c for c in all_items if keyword in c["name"] or keyword in c["industry"]]
    start = (page - 1) * page_size
    return {"total": len(all_items), "page": page, "pageSize": page_size, "items": all_items[start:start + page_size], "isMock": True}


# ── HTTP 핸들러 ──────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, path):
        if not os.path.isfile(path):
            self.send_response(404)
            self.end_headers()
            return
        ext = os.path.splitext(path)[1].lower()
        mime = MIME.get(ext, "application/octet-stream")
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        def qp(key, default=""):
            return qs.get(key, [default])[0]

        keyword = qp("keyword")
        region = qp("region")
        page = int(qp("page", "1"))
        page_size = int(qp("pageSize", "9"))

        if parsed.path == "/api/jobs":
            if USE_MOCK:
                return self.send_json(mock_jobs(keyword, region, page, page_size))
            # 실제 Work24 API
            try:
                params = urllib.parse.urlencode({
                    "authKey": API_KEY, "callTp": "L", "returnType": "JSON",
                    "startPage": page, "display": page_size, "keyword": keyword, "region": region,
                })
                req = urllib.request.urlopen(
                    f"https://openapi.work.go.kr/opi/opi/opia/wantedApi.do?{params}", timeout=8
                )
                data = json.loads(req.read().decode("utf-8"))
                lst = data.get("wanted", {}).get("wantedInfo") or []
                items = [{
                    "id": j.get("wantedAuthNo"), "title": j.get("title"),
                    "company": (j.get("company") or {}).get("comNm"),
                    "job": (j.get("job") or {}).get("jobNm"),
                    "region": (j.get("region") or {}).get("regionNm"),
                    "salary": ((j.get("salTp") or {}).get("salTpNm") or ""),
                    "career": (j.get("career") or {}).get("careerNm"),
                    "education": (j.get("education") or {}).get("eduNm"),
                    "deadline": j.get("closDt"), "url": j.get("wantedInfoUrl"),
                } for j in lst]
                return self.send_json({"total": int(data.get("wanted", {}).get("total", 0)),
                                       "page": page, "pageSize": page_size, "items": items})
            except Exception as e:
                return self.send_json({"error": str(e)}, 500)

        elif parsed.path == "/api/training":
            if USE_MOCK:
                return self.send_json(mock_training(keyword, region, page, page_size))
            return self.send_json({"error": "HRD-Net API 키 설정 필요"}, 500)

        elif parsed.path == "/api/companies":
            if USE_MOCK:
                return self.send_json(mock_companies(keyword, page, page_size))
            return self.send_json({"error": "강소기업 API 키 설정 필요"}, 500)

        else:
            # 정적 파일
            file_path = parsed.path.lstrip("/") or "index.html"
            full_path = os.path.join(PUBLIC_DIR, *file_path.split("/"))
            if os.path.isdir(full_path):
                full_path = os.path.join(full_path, "index.html")
            self.serve_file(full_path)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"✅ 서버 실행 중: http://localhost:{PORT}")
    if USE_MOCK:
        print("⚠️  API 키 미설정 → 샘플 데이터로 동작 중")
        print("   .env 파일에 WORK24_API_KEY를 입력하면 실제 데이터를 불러옵니다.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버 종료")

require('dotenv').config();
const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_DIR = path.join(__dirname, 'data');

app.use(express.static('public'));

function readData(filename) {
  try {
    return JSON.parse(fs.readFileSync(path.join(DATA_DIR, filename), 'utf-8'));
  } catch {
    return [];
  }
}

// 채용공고 - data/jobs.json (Work24 MCP로 수집한 실제 데이터)
app.get('/api/jobs', (req, res) => {
  const { keyword = '', region = '', page = 1, pageSize = 9 } = req.query;
  const pg = Number(page);
  const ps = Number(pageSize);

  let items = readData('jobs.json');

  if (keyword) {
    const kw = keyword.toLowerCase();
    items = items.filter(j =>
      (j.title || '').toLowerCase().includes(kw) ||
      (j.company || '').toLowerCase().includes(kw) ||
      (j.employment_type || '').includes(kw)
    );
  }

  const start = (pg - 1) * ps;
  const paged = items.slice(start, start + ps);

  res.json({
    total: items.length,
    page: pg,
    pageSize: ps,
    updatedAt: getFileDate('jobs.json'),
    items: paged.map(j => ({
      id: j.emp_seqno,
      title: j.title,
      company: j.company,
      companyType: j.company_type,
      employmentType: j.employment_type,
      deadline: j.end_date,
      logoUrl: j.logo_url,
      url: j.detail_url,
    })),
  });
});

// 강소기업 - data/companies.json (Work24 MCP로 수집한 실제 데이터)
app.get('/api/companies', (req, res) => {
  const { keyword = '', page = 1, pageSize = 9 } = req.query;
  const pg = Number(page);
  const ps = Number(pageSize);

  let items = readData('companies.json');

  if (keyword) {
    const kw = keyword.toLowerCase();
    items = items.filter(c =>
      (c.company_name || '').toLowerCase().includes(kw) ||
      (c.summary || '').toLowerCase().includes(kw) ||
      (c.company_type || '').includes(kw)
    );
  }

  const start = (pg - 1) * ps;
  const paged = items.slice(start, start + ps);

  res.json({
    total: items.length,
    page: pg,
    pageSize: ps,
    updatedAt: getFileDate('companies.json'),
    items: paged.map(c => ({
      id: c.company_id,
      name: c.company_name,
      companyType: c.company_type,
      summary: c.summary,
      description: c.description,
      url: c.homepage,
      logoUrl: c.logo_url,
    })),
  });
});

// 훈련과정 - MCP API에 현재 데이터 없음 → 샘플
app.get('/api/training', (req, res) => {
  const { keyword = '', region = '', page = 1, pageSize = 9 } = req.query;
  const pg = Number(page);
  const ps = Number(pageSize);

  let items = [
    { id: 'T001', title: 'AWS 클라우드 실무 과정', institution: '한국IT교육원', region: '서울', startDate: '2026-06-02', endDate: '2026-08-29', cost: '무료 (국비)', ncs: '정보기술개발', url: 'https://www.hrd.go.kr' },
    { id: 'T002', title: 'Python 데이터 분석 부트캠프', institution: '패스트캠퍼스', region: '서울', startDate: '2026-06-09', endDate: '2026-09-26', cost: '무료 (국비)', ncs: '빅데이터분석', url: 'https://www.hrd.go.kr' },
    { id: 'T003', title: 'UI/UX 디자인 실무 과정', institution: '디자인 아카데미', region: '경기', startDate: '2026-06-16', endDate: '2026-09-12', cost: '무료 (국비)', ncs: '디자인', url: 'https://www.hrd.go.kr' },
    { id: 'T004', title: '스마트 물류·유통 전문가 양성', institution: '한국유통교육원', region: '인천', startDate: '2026-07-01', endDate: '2026-10-24', cost: '무료 (국비)', ncs: '물류', url: 'https://www.hrd.go.kr' },
    { id: 'T005', title: '디지털 마케팅 SNS 전략가 과정', institution: '마케팅 인사이트', region: '서울', startDate: '2026-06-23', endDate: '2026-08-15', cost: '무료 (국비)', ncs: '마케팅', url: 'https://www.hrd.go.kr' },
    { id: 'T006', title: 'Java 풀스택 개발자 양성', institution: '코드팩토리', region: '경기', startDate: '2026-07-07', endDate: '2026-12-19', cost: '무료 (국비)', ncs: '정보기술개발', url: 'https://www.hrd.go.kr' },
    { id: 'T007', title: '바리스타 2급 자격증 취득 과정', institution: '한국직업능력개발원', region: '부산', startDate: '2026-06-10', endDate: '2026-08-05', cost: '50,000원', ncs: '조리·식음료', url: 'https://www.hrd.go.kr' },
    { id: 'T008', title: '회계 실무 및 ERP 운용', institution: '경리나라교육센터', region: '서울', startDate: '2026-06-30', endDate: '2026-09-19', cost: '무료 (국비)', ncs: '회계·감사', url: 'https://www.hrd.go.kr' },
  ];

  if (keyword) items = items.filter(t => t.title.includes(keyword) || t.institution.includes(keyword));
  if (region) items = items.filter(t => t.region.includes(region));

  const start = (pg - 1) * ps;
  res.json({
    total: items.length,
    page: pg,
    pageSize: ps,
    isSample: true,
    items: items.slice(start, start + ps),
  });
});

function getFileDate(filename) {
  try {
    return fs.statSync(path.join(DATA_DIR, filename)).mtime.toISOString().slice(0, 10);
  } catch {
    return null;
  }
}

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`✅ 서버 실행 중: http://localhost:${PORT}`);
    console.log(`📂 채용공고: ${readData('jobs.json').length}건 (Work24 실제 데이터)`);
    console.log(`📂 강소기업: ${readData('companies.json').length}건 (Work24 실제 데이터)`);
  });
}

module.exports = app;

# 📚 arXiv LLM Educational Assessment

LLM 기반 **교육 평가 / 자동 채점(Auto-grading)** 관련 arXiv 논문을
매주 자동 수집하여 공개하는 오픈 아카이브입니다.
이 리포지토리는 GitHub Actions를 통해 매주 arXiv API를 호출하고,
최근 7일간 새로 등록된 관련 논문들을 자동으로 업데이트합니다.

📅 매주 일요일 04:00 (UTC) 자동 갱신
🌐 실시간 페이지 보기: [GitHub Pages](https://lovehyun.github.io/arxiv-llmedu/web/)

---

## 🎯 주요 주제

- Automated Essay Scoring (자동 에세이 채점)
- Rubric-based / Chain-of-Thought 평가
- Fairness & Bias in AI Grading
- GPT-4 / LLM 기반 피드백 생성
- AI-Assisted Learning Analytics

---

## ⚙️ 시스템 구성

| 구성 요소 | 설명 |
|------------|------|
| **weekly_arxiv.py** | arXiv API에서 최근 7일 내 논문 수집 |
| **manual_arxiv.py** | 특정 기간의 논문 수동 수집 |
| **fetcher_utils.py** | 검색·Markdown 변환 공통 모듈 |
| **papers.md** | 주간 단위 논문 기록 (접이식 UI로 웹에서 열람 가능) |
| **index.html / script.js / style.css** | GitHub Pages용 웹 인터페이스 |
| **GitHub Actions** | 매주 자동 실행 및 self-commit, Pages 배포 |

---

## 📊 작동 예시 (웹 UI)

- ✅ 주별 접이식(▶) 보기  
- ✅ "📖 전체 펼치기 / 🗂 전체 접기" 버튼 지원  
- ✅ arXiv 링크 클릭 시 논문 원문 바로 이동  
- ✅ `papers.md`를 Markdown 그대로 열람 가능  

---

## 💻 로컬 실행 방법 (GitHub Pages 미리보기)

로컬 환경에서 GitHub Pages와 동일하게 웹페이지를 확인하려면
프로젝트 루트 디렉토리에서 간단한 HTTP 서버를 실행합니다.

### 실행 방법 (프로젝트 루트에서)
```bash
python -m http.server 8000
```
→ 브라우저에서 [http://localhost:8000/web/](http://localhost:8000/web/) 접속

> **⚠️ 중요**: 반드시 **프로젝트 루트 디렉토리**에서 실행해야 합니다.
> `web/` 폴더 안에서 실행하거나 `--directory web` 옵션을 사용하면
> `index.html`이 `../data/papers.md`에 접근할 수 없어 404 오류가 발생합니다.

### 동작 원리
- `index.html`은 `../data/papers.md`를 자동으로 읽어와 최신 논문 목록을 렌더링합니다.
- 웹 서버의 루트가 프로젝트 루트이므로 `web/index.html`에서 상위의 `data/` 폴더에 접근 가능합니다.
- 별도의 서버나 백엔드 없이 정적 HTML로만 동작합니다.

---

## 📁 디렉토리 구조

```
arxiv-llmedu/
├── scripts/
│   ├── weekly_arxiv.py
│   ├── manual_arxiv.py
│   └── fetcher_utils.py
│
├── data/
│   ├── papers_2024.md
│   ├── papers_2025.md
│   └── ...
│
├── web/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── .github/workflows/weekly-update.yml
├── config.yaml
└── README.md
```

---

### 🧾 License

- Code: [MIT License](./LICENSE)  
- Data (papers.md, index.html): [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)  
- Data source: [arXiv API](https://arxiv.org/help/api)

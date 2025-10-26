// --- 전체 펼치기 / 접기 기능 ---
function toggleAll(open) {
    document.querySelectorAll('details').forEach((d) => (d.open = open));
}

// --- 선택한 년도만 펼치기 / 접기 ---
function toggleSelectedYears(open) {
    document.querySelectorAll('.year-checkbox:checked').forEach((checkbox) => {
        const year = checkbox.value;
        // 년도 섹션 펼치기/접기
        const yearDetails = document.getElementById(`year-details-${year}`);
        if (yearDetails) yearDetails.open = open;
        // 해당 년도의 날짜 섹션들 펼치기/접기
        document.querySelectorAll(`details[data-year="${year}"]`).forEach((d) => (d.open = open));
    });
}

// --- 데이터 파일 목록 가져오기 ---
async function getYearFiles() {
    // GitHub Pages 환경에서는 파일 목록을 직접 가져올 수 없으므로
    // 최근 몇 년치를 시도해서 존재하는 파일만 로드
    const currentYear = new Date().getFullYear();
    const years = [];

    for (let year = currentYear; year >= 2020; year--) {
        try {
            const res = await fetch(`../data/papers_${year}.md`, { method: 'HEAD' });
            if (res.ok) {
                years.push(year);
            }
        } catch (err) {
            // 파일이 없으면 무시
            break;
        }
    }

    return years;
}

// --- 논문 로딩 및 렌더링 ---
async function load() {
    try {
        const container = document.getElementById('papers');
        container.innerHTML = '⌛ 불러오는 중...';

        const years = await getYearFiles();

        if (years.length === 0) {
            container.innerHTML = '⚠️ 논문 데이터 파일을 찾을 수 없습니다.';
            return;
        }

        container.innerHTML = '';

        // 년도별로 처리
        for (const year of years) {
            const res = await fetch(`../data/papers_${year}.md`);
            if (!res.ok) continue;

            const md = await res.text();

            // ## 로 시작하는 섹션을 주 단위 구분으로 분리
            const sections = md.split(/^## /m).slice(1);

            // 년도 섹션 생성
            const yearSection = document.createElement('div');
            yearSection.className = 'year-section';

            const yearHeader = document.createElement('div');
            yearHeader.className = 'year-header';

            // 체크박스
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'year-checkbox';
            checkbox.value = year;
            checkbox.id = `year-checkbox-${year}`;

            yearHeader.appendChild(checkbox);

            // 년도 전체를 details로 감싸기
            const yearDetails = document.createElement('details');
            yearDetails.id = `year-details-${year}`;
            yearDetails.open = true; // 기본적으로 펼쳐져 있음

            const yearSummary = document.createElement('summary');

            yearDetails.appendChild(yearSummary);

            // 날짜별 섹션 추가
            const dateContainer = document.createElement('div');
            dateContainer.className = 'date-container';

            let totalPapers = 0; // 전체 논문 개수

            for (const sec of sections) {
                const [header, ...rest] = sec.split('\n');
                const body = rest.join('\n').trim();

                // 각 섹션의 논문 개수 계산 (** 볼드체로 시작하는 논문 제목)
                const paperCount = (body.match(/^\*\*.*\*\*$/gm) || []).length;
                totalPapers += paperCount;

                const det = document.createElement('details');
                det.setAttribute('data-year', year);
                const sum = document.createElement('summary');
                const cleanHeader = header.replace('🗓️ ', '').trim();
                sum.textContent = `${cleanHeader} (${paperCount}건)`;

                const content = document.createElement('div');
                content.innerHTML = marked.parse(body);

                det.appendChild(sum);
                det.appendChild(content);
                dateContainer.appendChild(det);
            }

            // 년도 summary에 전체 논문 개수 표시
            yearSummary.textContent = `${year}년 (${totalPapers}건)`;

            yearDetails.appendChild(dateContainer);
            yearHeader.appendChild(yearDetails);
            yearSection.appendChild(yearHeader);

            container.appendChild(yearSection);
        }
    } catch (err) {
        console.error(err);
        document.getElementById('papers').innerHTML =
            '⚠️ 논문을 불러오는 중 오류가 발생했습니다.';
    }
}

// --- marked.js CDN 로드 후 실행 ---
const script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
script.onload = load;
document.head.appendChild(script);

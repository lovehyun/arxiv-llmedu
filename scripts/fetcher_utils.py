# scripts/fetcher_utils.py
import os
import re
import yaml
import requests
import feedparser
from datetime import datetime, timedelta, timezone
from requests.utils import quote

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
README_MD = os.path.join(os.path.dirname(__file__), "..", "README.md")
USER_AGENT = "GenAILabs-ArxivFetcher/1.1"

def get_papers_file(year=None):
    """Get the papers file path for a specific year. If year is None, use current year."""
    if year is None:
        year = datetime.now(timezone.utc).year
    return os.path.join(DATA_DIR, f"papers_{year}.md")

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def fetch_papers(query, start_date=None, end_date=None, max_results=20):
    """
    범위 기반 검색: start_date, end_date (YYYY-MM-DD)
    """
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start_dt = datetime.now(timezone.utc) - timedelta(days=7)
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end_dt = datetime.now(timezone.utc)

    start_str = start_dt.strftime("%Y%m%d%H%M")
    end_str = end_dt.strftime("%Y%m%d%H%M")

    # arxiv_query = f"all:{topic} AND submittedDate:[{cutoff} TO 30000000000000]"
    # arxiv_query = (
    #     f"(ti:{topic} OR abs:{topic}) AND "
    #     f"submittedDate:[{cutoff} TO 30000000000000]"
    # )

    # 분야	카테고리 코드
    # 인공지능	cs.AI
    # 컴퓨터비전	cs.CV
    # 언어처리	cs.CL
    # 머신러닝	cs.LG
    # 교육기술	cs.CY, cs.HC (HCI 관련)
    # 심리/통계/교육	stat.AP, stat.ML

    arxiv_query = (
        f"(ti:{query} OR abs:{query}) "
        f"AND cat:(cs.AI OR cs.CL OR cs.LG OR stat.ML OR cs.CY OR cs.HC) "
        f"AND submittedDate:[{start_str} TO {end_str}]"
    )

    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query={quote(arxiv_query)}"
        f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )

    headers = {"User-Agent": USER_AGENT}
    res = requests.get(url, headers=headers, timeout=30)
    res.raise_for_status()
    return feedparser.parse(res.text).entries

def write_papers(entries, name, query, year=None, prepend=False, dry_run=False, date_range=None, is_weekly=False):
    """
    Write papers to year-based file.
    If year is None, papers are grouped by their published year.
    date_range: tuple of (start_date, end_date) for manual searches, displayed in section header
    is_weekly: if True, adds "Weekly Digest" to the section header
    """
    if not entries:
        print(f"ℹ️ No results for {name}")
        return

    # Group entries by year if year is None
    if year is None:
        entries_by_year = {}
        for e in entries:
            pub_date = getattr(e, "published", "")[:10]  # YYYY-MM-DD
            if pub_date:
                pub_year = int(pub_date[:4])
            else:
                pub_year = datetime.now(timezone.utc).year

            if pub_year not in entries_by_year:
                entries_by_year[pub_year] = []
            entries_by_year[pub_year].append(e)

        # Recursively call write_papers for each year
        for year_key, year_entries in entries_by_year.items():
            write_papers(year_entries, name, query, year=year_key, prepend=prepend, dry_run=dry_run, date_range=date_range, is_weekly=is_weekly)
        return

    # Single year processing
    output_file = get_papers_file(year)

    # Determine date display
    if date_range:
        date_display = f"{date_range[0]} ~ {date_range[1]}"
    elif is_weekly:
        date_display = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')} Weekly Digest"
    else:
        date_display = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Always print to console
    print(f"\n{'='*80}")
    print(f"📅 {date_display} — {name}")
    print(f"🔍 Query: {query}")
    print(f"📊 Found {len(entries)} papers")
    print(f"{'='*80}\n")

    for i, e in enumerate(entries, 1):
        title = re.sub(r"\s+", " ", e.title).strip()
        authors = ", ".join([a.name for a in e.authors])
        pub = getattr(e, "published", "")[:10]
        link = e.link

        print(f"{i}. {title}")
        print(f"   Authors: {authors}")
        if pub:
            print(f"   Published: {pub}")
        print(f"   Link: {link}")
        print()

    # If dry-run, don't write to file
    if dry_run:
        print(f"🔍 [DRY RUN] Not writing to file\n")
        return

    # Build markdown section
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    section = f"\n## 🗓️ {date_display} — {name}\n<small>{query}</small>\n\n"
    for e in entries:
        title = re.sub(r"\s+", " ", e.title).strip()
        authors = ", ".join([a.name for a in e.authors])
        pub = getattr(e, "published", "")[:10]
        link = e.link
        section += f"**{title}**  \n_Authors:_ {authors}  \n"
        if pub:
            section += f"_Published:_ {pub}  \n"
        section += f"[arXiv Link]({link})\n\n"

    if prepend:
        # Read existing content and prepend new section
        existing_content = ""
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                existing_content = f.read()

        with open(output_file, "w", encoding="utf-8") as f:
            # Parse header and content
            if existing_content and existing_content.startswith("# "):
                # Find first ## (section start) to separate header from content
                first_section_pos = existing_content.find("\n## ")
                if first_section_pos != -1:
                    header = existing_content[:first_section_pos + 1]  # Include the newline
                    rest_content = existing_content[first_section_pos + 1:]
                else:
                    # No sections yet, entire file is header
                    header = existing_content
                    rest_content = ""

                f.write(header)
                f.write(section)
                f.write(rest_content)
            else:
                # No header exists, create one
                f.write("# 📚 LLM 기반 교육 평가 논문 아카이브 (주간 갱신)\n\n")
                f.write(section)
                f.write(existing_content)

        print(f"✅ Prepended {len(entries)} papers → {output_file}\n")
    else:
        # Append mode (default for weekly updates)
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(section)
        print(f"✅ Appended {len(entries)} papers → {output_file}\n")

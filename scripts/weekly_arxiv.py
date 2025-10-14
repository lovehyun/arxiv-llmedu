# scripts/weekly_arxiv.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly arXiv fetcher (fetches last 7 days).
Usage:
  python scripts/weekly_arxiv.py [--dry-run]

Example:
  python scripts/weekly_arxiv.py
  python scripts/weekly_arxiv.py --dry-run
"""
from datetime import datetime, timedelta, timezone
import sys
import os

# 내부 모듈 import
sys.path.append(os.path.dirname(__file__))
from fetcher_utils import load_config, fetch_papers, write_papers

def main():
    dry_run = "--dry-run" in sys.argv
    cfg = load_config()

    for topic in cfg["topics"]:
        name, query = topic["name"], topic["query"]
        print(f"🔍 Searching {name} (last 7 days) ...")
        entries = fetch_papers(query, None, None, cfg.get("max_results", 20))
        # Use current year (None = current year), mark as weekly digest
        write_papers(entries, name, query, year=None, prepend=True, dry_run=dry_run, is_weekly=True)

if __name__ == "__main__":
    main()

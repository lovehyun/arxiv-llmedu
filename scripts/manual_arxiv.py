# scripts/manual_arxiv.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual arXiv fetcher with date range.
Usage:
  python scripts/manual_arxiv.py <start_date> <end_date> <count> [--dry-run]

Example:
  python scripts/manual_arxiv.py 2024-01-01 2024-05-31 100
  python scripts/manual_arxiv.py 2024-01-01 2024-05-31 100 --dry-run
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from fetcher_utils import load_config, fetch_papers, write_papers

def main():
    if len(sys.argv) < 4:
        print("Usage: manual_arxiv.py <start_date> <end_date> <count> [--dry-run]")
        print("\nDate format: YYYY-MM-DD")
        print("\nExample:")
        print("  python scripts/manual_arxiv.py 2024-01-01 2024-05-31 100")
        print("  python scripts/manual_arxiv.py 2024-01-01 2024-05-31 100 --dry-run")
        sys.exit(1)

    start, end, count = sys.argv[1], sys.argv[2], int(sys.argv[3])
    dry_run = "--dry-run" in sys.argv
    cfg = load_config()

    for topic in cfg["topics"]:
        name, query = topic["name"], topic["query"]
        print(f"🔍 Searching {name} ({start}~{end}) ...")
        entries = fetch_papers(query, start, end, count)
        # Pass None for year to auto-group by published year
        # Pass date_range to display search period in section header
        write_papers(entries, name, query, year=None, prepend=False, dry_run=dry_run, date_range=(start, end))

if __name__ == "__main__":
    main()

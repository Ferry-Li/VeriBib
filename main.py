"""Main entry point for Bib Checker."""

import argparse
import time
from config import BIB_FILE, OUTPUT_BIB, SLEEP_TIME
from bib_parser import parse_bib_file
from semantic_scholar import search_ss
from matcher import is_same
from exporter import export_updated_bib, export_md


def process(bib):
    """Process a single BibTeX entry."""
    title = bib.get("title", "").strip()
    if not title:
        return {"status": "❌ Title is empty", "orig": bib, "ss": None}

    data = search_ss(title)
    if not data or "data" not in data or len(data["data"]) == 0:
        return {"status": "❌ Not found in Semantic Scholar", "orig": bib, "ss": None}

    best = None
    for p in data["data"]:
        if is_same(bib, p):
            best = p
            break

    if not best:
        return {"status": "⚠️ Mismatch", "orig": bib, "ss": None}

    return {
        "status": "✅ Up-to-date",
        "orig": bib,
        "ss": best,
        "url": f"https://www.semanticscholar.org/paper/{best['paperId']}"
    }


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="BibTeX Checker - Verify and fix BibTeX entries using Semantic Scholar")
    parser.add_argument("input", nargs="?", default=BIB_FILE, help="Input BibTeX file (default: test.bib)")
    parser.add_argument("-o", "--output", metavar="FILE", help="Output optimized BibTeX file (default: output_updated.bib)")
    parser.add_argument("--no-output", action="store_true", help="Do not output optimized BibTeX file")
    parser.add_argument("-r", "--report", metavar="FILE", help="Output report file (default: bib_report.md)")
    parser.add_argument("--no-report", action="store_true", help="Do not output report file")

    args = parser.parse_args()

    input_file = args.input
    output_file = None if args.no_output else (args.output if args.output else OUTPUT_BIB)
    report_file = None if args.no_report else (args.report if args.report else "bib_report.md")

    entries = parse_bib_file(input_file)
    print(f"Reading {len(entries)} items from {input_file}")

    results = []
    for i, e in enumerate(entries, 1):
        print(f"{i}/{len(entries)}")
        res = process(e)
        results.append(res)
        time.sleep(SLEEP_TIME)

    if report_file:
        export_md(results, report_file)
        print(f"Report: {report_file}")

    if output_file:
        export_updated_bib(results, output_file)
        print(f"Optimized BibTeX: {output_file}")

    print("✅ Done!")


if __name__ == "__main__":
    main()

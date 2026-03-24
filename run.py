#!/usr/bin/env python3
"""Main entry point for BibTeX verification"""
import argparse
import sys

import config
import bib_parser
import scraper
import formatter


def main():
    parser = argparse.ArgumentParser(description="BibTeX Verification via Google Scholar")
    parser.add_argument("files", nargs="+", help="BibTeX files to verify")
    parser.add_argument("--output", "-o", help="Output file (default: verification_report.md)")
    parser.add_argument("--format", "-f", choices=["markdown", "txt", "json"], help="Output format")
    parser.add_argument("--llm", "-l", help="LLM provider (deepseek, openai/gpt, gemini/google, claude/anthropic, qwen/alibaba, kimi/moonshot, minimax, glm/zhipu)")
    parser.add_argument("--detailed", "-d", action="store_true", help="Include detailed version info in output")

    args = parser.parse_args()

    # Override config LLM provider if specified
    if args.llm:
        config.LLM_PROVIDER = args.llm.lower()

    # Check config
    if not config.SCRAPER_API_KEY:
        print("Error: Please set SCRAPER_API_KEY in config.py")
        sys.exit(1)

    # Parse all entries
    all_entries = []
    for filepath in args.files:
        entries = bib_parser.parse_bib_file(filepath)
        print(f"Loaded {len(entries)} entries from {filepath}")
        all_entries.extend(entries)

    if not all_entries:
        print("No entries found")
        sys.exit(1)

    print(f"\nVerifying {len(all_entries)} entries...\n")

    # Verify each entry
    results = []
    for i, entry in enumerate(all_entries, 1):
        print(f"[{i}/{len(all_entries)}] ", end="", flush=True)
        result = scraper.verify_entry(entry)
        results.append(result)

        if 'error' not in result:
            print(f"Found {result.get('num_versions', 0)} versions")
        else:
            print(f"Error: {result.get('error')}")

    # Format output
    output_format = args.format or config.OUTPUT_FORMAT
    output_file = args.output or config.OUTPUT_FILE

    if output_format == "markdown":
        content = formatter.format_markdown(results, all_entries, detailed=args.detailed)
    elif output_format == "txt":
        content = formatter.format_text(results, all_entries, detailed=args.detailed)
    elif output_format == "json":
        content = formatter.format_json(results, all_entries, detailed=args.detailed)
    else:
        content = formatter.format_markdown(results, all_entries, detailed=args.detailed)

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n[OK] Results saved to {output_file}")


if __name__ == "__main__":
    main()

"""Export utilities for BibTeX and Markdown reports."""

from config import (
    OUTPUT_BIB, EXPORT_FIELDS_ARTICLE, EXPORT_FIELDS_INPROCEEDINGS
)
from venue_utils import abbr_venue


def get_entry_type(paper):
    """Determine entry type from Semantic Scholar data.

    Returns 'inproceedings' for conference, 'article' for journal.
    """
    if not paper:
        return None

    # Check venueType from Semantic Scholar
    venue_type = paper.get("venueType", "").lower()
    if venue_type == "conference":
        return "inproceedings"
    elif venue_type == "journal":
        return "article"

    # Fallback: check if venue contains common conference indicators
    venue = paper.get("venue", "").lower()
    conf_indicators = ["conference", "proceedings", "symposium", "workshop"]
    journal_indicators = ["journal", "transactions", " ieee ", " ACM ", "letters"]

    for indicator in conf_indicators:
        if indicator in venue:
            return "inproceedings"
    for indicator in journal_indicators:
        if indicator in venue:
            return "article"

    # Default to article
    return "article"


def export_updated_bib(results, output_path=None):
    """Export optimized BibTeX file."""
    output_path = output_path or OUTPUT_BIB
    lines = []
    for r in results:
        orig = r["orig"]
        paper = r["ss"]
        orig_type = orig["type"]
        key = orig["key"]

        if not paper:
            lines.append(f"@{orig_type}{{{key},")
            for k, v in orig.items():
                if k in ["type", "key"]: continue
                lines.append(f"  {k}={{{v}}},")
            lines.append("}\n")
            continue

        # Determine entry type from Semantic Scholar data
        entry_type = get_entry_type(paper)

        real_title = paper["title"]
        real_year = str(paper["year"])
        real_venue = abbr_venue(paper.get("venue", ""))
        real_doi = paper.get("externalIds", {}).get("DOI", "")
        real_author = " and ".join([a["name"] for a in paper.get("authors", [])])

        fields = EXPORT_FIELDS_ARTICLE if entry_type == "article" else EXPORT_FIELDS_INPROCEEDINGS
        data = {
            "title": real_title, "author": real_author, "year": real_year,
            "booktitle": real_venue, "journal": real_venue, "doi": real_doi
        }

        lines.append(f"@{entry_type}{{{key},")
        for f in fields:
            if f in data and data[f]:
                lines.append(f"  {f}={{{data[f]}}},")
        lines.append("}\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def export_md(results, output_path=None):
    """Export Markdown report with both original and updated info."""
    output_path = output_path or "bib_report.md"

    # Collect all fields from original entries
    orig_keys = set()
    for r in results:
        orig_keys.update(r["orig"].keys())
    orig_keys = sorted([k for k in orig_keys if k not in ["type", "key"]])

    # Updated fields to show
    upd_keys = ["title", "author", "year", "journal", "booktitle", "doi"]

    # Count statuses
    total = len(results)
    up_to_date = sum(1 for r in results if "Up-to-date" in r["status"])
    mismatch = sum(1 for r in results if "Mismatch" in r["status"])
    not_found = sum(1 for r in results if "Not found" in r["status"])

    # Build header
    md = "# BibTeX Verification Report\n\n"
    md += "## Summary\n"
    md += f"- **Total**: {total}\n"
    md += f"- ✅ **Up-to-date**: {up_to_date}\n"
    md += f"- ⚠️ **Mismatch**: {mismatch}\n"
    md += f"- ❌ **Not found**: {not_found}\n\n"

    md += "## Details\n"
    md += "| Status | Key | " + " | ".join([f"Orig {k}" for k in orig_keys]) + " | " + " | ".join([f"New {k}" for k in upd_keys]) + " | SS Link |\n"
    md += "|--------|----|" + "|".join(["---"]*len(orig_keys)) + "|" + "|".join(["---"]*len(upd_keys)) + "|--------|\n"

    for r in results:
        o = r["orig"]
        p = r["ss"]
        status = r["status"]

        row = [status, o.get("key", "")]

        # Original fields
        for k in orig_keys:
            row.append(o.get(k, "-"))

        # Updated fields (only if paper found)
        if p:
            row.append(p.get("title", "-"))
            row.append(" and ".join([a["name"] for a in p.get("authors", [])]) or "-")
            row.append(str(p.get("year", "-")))
            row.append(p.get("venue", "-"))
            row.append(abbr_venue(p.get("venue", "")))
            row.append(p.get("externalIds", {}).get("DOI", "-"))
        else:
            row.extend(["-"] * len(upd_keys))

        row.append(r.get("url", "-"))
        md += "| " + " | ".join(row) + " |\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)

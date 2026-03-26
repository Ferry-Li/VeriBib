# VeriBib - AI Citation Verification Tool

<p align="center">
  <img src="https://img.shields.io/badge/LLM_Support-6%2B-green" alt="LLM Support">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-orange" alt="License">
</p>

> Verify and fix BibTeX citations with Semantic Scholar to detect AI hallucinations and incorrect references.

[English](README.md) | [简体中文](README_CN.md)

## Why VeriBib?

With the widespread adoption of LLMs (like ChatGPT, Claude, and DeepSeek) in academic writing, a critical problem has emerged: **Citation Hallucination**. AI models frequently invent plausible-sounding but entirely fake papers, mix up real authors with incorrect titles, or hallucinate non-existent publication venues.

**VeriBib** is designed to act as an automated fact-checker for your reference list. It helps researchers verify their BibTeX citations by:

- Cross-referencing citations against Semantic Scholar to detect completely fabricated papers.
- Identifying "partial hallucinations" (e.g., real paper title, but hallucinated authors or publication year).
- Using reliable LLMs to analyze and match generated metadata against verified, real-world sources.
- Automatically abbreviating conference and journal names to standard formats (ICML, CVPR, IEEE TPAMI, etc.).
- Ensuring your bibliography is real, accurate, and academically rigorous before submission.

## Features

- 🚨 **Hallucination Detection**: Instantly flags completely fabricated papers or "ghost citations" that do not exist in real academic databases.
- 🔍 **Fact-Checking Search**: Queries Semantic Scholar to verify the actual existence of the paper and retrieves its true metadata.
- 🤖 **LLM-Powered Verification**: Intelligently compares your BibTeX entry against real-world search results to catch subtle AI-generated errors (like mixed-up author lists or hallucinated journals).
- 📊 **Smart Matching**: Detects author name variations, venue differences, and year mismatches caused by AI confusion.
- 🔄 **Auto-Fix**: Automatically fetches correct metadata (title, authors, year, DOI) and standardizes venue abbreviations.
- 📝 **Flexible Output**: Generates Markdown reports and optimized BibTeX files with side-by-side comparison of original and updated entries.
- 🔌 **Multiple LLM Providers**: Support for 6+ LLM APIs to perform the verification analysis.

## Supported LLMs

| Provider | Model | Alias |
|----------|-------|--------|
| DeepSeek | DeepSeek Chat | `deepseek` |
| OpenAI | GPT-4o, GPT-4o-mini | `openai`, `gpt` |
| Google | Gemini | `gemini` |
| Anthropic | Claude | `claude` |
| Alibaba | Qwen | `qwen` |
| Moonshot | Kimi | `kimi` |

## Quick Start

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Configure API Keys

Edit `config.py`:

```python
# Semantic Scholar API Key (free)
SS_API_KEY = "your_semantic_scholar_key"

# LLM API (choose one)
LLM_API_KEY = "your_llm_key"
LLM_PROVIDER = "deepseek"  # deepseek, qwen, kimi, gpt, openai, claude, gemini
LLM_MODEL = "deepseek-chat"
```

> 💡 **Note**: Semantic Scholar provides a free API with 100 requests per second for academic research.

### 3. Run Verification

```bash
# Basic usage
python main.py input.bib

# Custom output files
python main.py input.bib -o fixed.bib -r report.md

# Skip output files
python main.py input.bib --no-output --no-report
```

## Output Example

### Markdown Report
| Status | Key | Orig title | New title | Orig journal | New journal | SS Link |
|--------|-----|------------|-----------|--------------|-------------|---------|
| ✅ Up-to-date | li2024size | Size-invariance matters... | Size-invariance Matters... | arXiv preprint | ICML | [Link] |
| ⚠️ Mismatch | bao2025towards | Towards Size-invariant... | - | IEEE TPAMI | - | - |

### Optimized BibTeX
```bibtex
@article{li2024size,
  title={Size-invariance Matters: Rethinking Metrics and Losses...},
  author={Feiran Li and Qianqian Xu and ...},
  journal={ICML},
  year={2024},
  doi={10.48550/arXiv.2405.09782},
}
```

## CLI Options

| Option | Description |
|--------|-------------|
| `input` | Input BibTeX file (default: test.bib) |
| `-o, --output` | Output optimized BibTeX file (default: output_updated.bib) |
| `--no-output` | Skip BibTeX output |
| `-r, --report` | Output report file (default: bib_report.md) |
| `--no-report` | Skip report output |

## Use Cases

### AI Researchers
- Verify conference papers (NeurIPS, ICML, CVPR, ICCV, ACL, EMNLP, etc.)
- Check arXiv preprints against final publications
- Validate author names and affiliations

### Academic Writers
- Ensure citation accuracy before submission
- Compare BibTeX against published versions
- Generate verification reports for supplementary materials

### Labs & Organizations
- Batch verify entire citation databases
- Export optimized BibTeX for database updates

## Project Structure

```
bib_checker/
├── config.py            # API keys & settings
├── main.py              # CLI entry point
├── bib_parser.py        # BibTeX parsing
├── semantic_scholar.py  # Semantic Scholar API client
├── matcher.py           # LLM paper matching
├── venue_utils.py       # Venue abbreviation
├── exporter.py         # Output generation
├── test.bib            # Sample input
└── README.md
```

## Venue Abbreviation

Built-in dictionary includes 40+ common venues:
- **Conferences**: CVPR, ICCV, ECCV, NeurIPS, ICLR, ICML, IJCAI, MICCAI, AAAI, ACMMM, BMVC, etc.
- **Journals**: IEEE TPAMI, IJCV, TIP, TVCG, TNNLS, TMM, PR, InfFus, etc.

The LLM can also generate abbreviations for unknown venues based on the known patterns.

## License

MIT License

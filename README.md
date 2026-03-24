# ScholarBib - AI Hallucination Citation Verifier

<p align="center">
  <img src="https://img.shields.io/badge/LLM_Support-8%2B-green" alt="LLM Support">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-orange" alt="License">
</p>

> Verify BibTeX citations with Google Scholar to detect AI hallucinations and fake references.

[English](README.md) | [简体中文](README_CN.md)

## Why ScholarBib?

With the widespread adoption of LLMs (like ChatGPT, Claude, and DeepSeek) in academic writing, a critical problem has emerged: **Citation Hallucination**. AI models frequently invent plausible-sounding but entirely fake papers, mix up real authors with incorrect titles, or hallucinate non-existent publication venues. 

**ScholarBib** is designed to act as an automated fact-checker for your reference list. It helps researchers verify their BibTeX citations by:

- Cross-referencing citations against Google Scholar to detect completely fabricated papers.
- Identifying "partial hallucinations" (e.g., real paper title, but hallucinated authors or publication year).
- Using reliable LLMs to analyze and match generated metadata against verified, real-world sources.
- Ensuring your bibliography is real, accurate, and academically rigorous before submission.

## Features

- 🚨 **Hallucination Detection**: Instantly flags completely fabricated papers or "ghost citations" that do not exist in real academic databases.
- 🔍 **Fact-Checking Search**: Scrapes Google Scholar to verify the actual existence of the paper and retrieves its true metadata.
- 🤖 **LLM-Powered Verification**: Intelligently compares your BibTeX entry against real-world search results to catch subtle AI-generated errors (like mixed-up author lists or hallucinated journals).
- 📊 **Smart Matching**: Detects author name variations, venue differences, and year mismatches caused by AI confusion.
- 📝 **Flexible Output**: Generates Markdown, JSON, or plain text reports clearly highlighting verified citations vs. hallucinated ones.
- 🔌 **Multiple LLM Providers**: Support for 10+ LLM APIs to perform the verification analysis.



## Supported LLMs

| Provider | Model | Alias |
|----------|-------|--------|
| DeepSeek | DeepSeek | `deepseek` |
| OpenAI | GPT-4o, GPT-4o-mini | `openai`, `gpt` |
| Google | Gemini Flash/Pro | `gemini`, `google` |
| Anthropic | Claude Sonnet 4.6 | `claude`, `anthropic` |
| Alibaba | Qwen Plus/Turbo | `qwen`, `alibaba` |
| Moonshot | Kimi | `kimi`, `moonshot` |
| MiniMax | Text-01 | `minimax` |
| Zhipu | GLM-4 Flash | `glm`, `zhipu` |

## Quick Start

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Configure API Keys

Edit `config.py`:

```python
# ScraperAPI - Get free 5000 credits at https://scraperapi.com
SCRAPER_API_KEY = "your_scraperapi_key"

# LLM API (choose one)
LLM_API_KEY = "your_openai_key"  # or DeepSeek, Anthropic, etc.
LLM_PROVIDER = "deepseek"  # default
```

> 💡 **Note**: ScraperAPI provides 5000 free API credits for new users. Sufficient for verifying hundreds of papers.

### 3. Run Verification

```bash
# Basic usage
python run.py paper.bib

# With detailed version info
python run.py papers.bib --detailed

# Use specific LLM
python run.py papers.bib --llm openai

# JSON output for automation
python run.py papers.bib -f json -o results.json
```

## Output Example

```
| # | Cite Key | Title | Found | Year | Journal/Conf | Authors |
|---|----------|-------|-------|------|-------------|--------|
| 1 | chen2024transformer | xxx | Found 5 versions | [OK] 2024 | [OK] NeurIPS | [OK] Chen, X |
```

## CLI Options

| Option | Description |
|--------|-------------|
| `--llm, -l` | LLM provider (deepseek/openai/gemini/claude/qwen/kimi/minimax/glm) |
| `--output, -o` | Output file path |
| `--format, -f` | Output format (markdown/txt/json) |
| `--detailed, -d` | Include all paper versions in output |

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
- Integrate into CI/CD pipelines
- Export JSON for database updates

## Project Structure

```
bib_checker/
├── config.py          # API keys & settings
├── run.py            # CLI entry point
├── bib_parser.py     # BibTeX parsing
├── scraper.py        # Google Scholar scraper
├── analyze.py        # LLM analysis
├── llm_adapter.py     # Multi-LLM support
├── formatter.py      # Output formatting
└── README.md
```

## License

MIT License

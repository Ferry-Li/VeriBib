# Bib Checker Configuration

# ScraperAPI configuration
SCRAPER_API_KEY = ""  # Your ScraperAPI key

# LLM configuration
LLM_API_KEY = ""  # Your LLM API key
LLM_PROVIDER = "deepseek"  # Options: deepseek, openai/gpt, gemini/google, claude/anthropic, qwen/alibaba, kimi/moonshot, minimax, glm/zhipu
LLM_MODEL = ""  # Optional: specific model name (auto-selected if empty)

# Search settings
MAX_RETRIES = 3  # Maximum retries for failed requests
RETRY_DELAY = 2  # Delay between retries in seconds

# Output settings
OUTPUT_FORMAT = "markdown"  # Options: markdown, txt, json
OUTPUT_FILE = "verification_report.md"

# Table string length limits (0 = no limit)
TITLE_MAX_LEN = 200
AUTHOR_MAX_LEN = 100
JOURNAL_MAX_LEN = 100

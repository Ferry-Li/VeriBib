# Bib Checker Configuration

# ====================== API Keys ======================
SS_API_KEY = "" # Semantic Scholar API Key
LLM_API_KEY = "" # LLM API Key

# ====================== LLM Settings ======================
LLM_PROVIDER = "deepseek"        # Options: deepseek, qwen, kimi, gpt, openai, claude, gemini
LLM_MODEL = "deepseek-chat"      # Model name (provider-specific)
USE_LLM_FOR_VENUE_ABBR = True   # Use LLM for venue abbreviation

# ====================== Network Settings ======================
MAX_RETRY = 999               # Retry on network error
SLEEP_TIME = 1                # Request interval in seconds

# ====================== Matching Settings ======================
# Maximum word differences to consider for matching (tried in order)
TITLE_MAX_WORD_DIFF = 3  # Try exact, 1-word diff, 2-word diff, 3-word diff

# ====================== File Paths ======================
BIB_FILE = "test.bib" # Input BibTeX file
OUTPUT_BIB = "output_updated.bib" # Output BibTeX file

# ======================== BibTeX Export Fields ========================
# Fields to include in exported BibTeX
EXPORT_FIELDS_ARTICLE = [
    "title", "author", "journal", "year", "volume", "pages", "doi"
]

EXPORT_FIELDS_INPROCEEDINGS = [
    "title", "author", "booktitle", "year", "pages", "doi", "organization"
]

# ======================== Venue Abbreviation Map ========================
VENUE_ABBR_MAP = {
    # Full names to abbreviations
    "IEEE Transactions on Pattern Analysis and Machine Intelligence": "IEEE TPAMI",
    "International Journal of Computer Vision": "IJCV",
    "Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition": "CVPR",
    "Proceedings of the IEEE International Conference on Computer Vision": "ICCV",
    "Proceedings of the European Conference on Computer Vision": "ECCV",
    "Advances in Neural Information Processing Systems": "NeurIPS",
    "International Conference on Learning Representations": "ICLR",
    "International Conference on Machine Learning": "ICML",
    "Proceedings of the International Joint Conference on Artificial Intelligence": "IJCAI",
    "Medical Image Computing and Computer-Assisted Intervention": "MICCAI",
    "Proceedings of the AAAI Conference on Artificial Intelligence": "AAAI",
    "Proceedings of the ACM International Conference on Multimedia": "ACMMM",
    "Proceedings of the International Conference on Artificial Intelligence": "ICAI",
    "Proceedings of the International Conference on Robotics and Automation": "ICRA",
    "Proceedings of the International Conference on Pattern Recognition": "ICPR",
    "Proceedings of the IEEE International Conference on Multimedia and Expo": "ICME",
    "Proceedings of the British Machine Vision Conference": "BMVC",
    "IEEE International Conference on Acoustics, Speech, and Signal Processing": "ICASSP",
    "Proceedings of the IEEE International Conference on Image Processing": "ICIP",
    "Asian Conference on Computer Vision": "ACCV",
    "ACM Transactions on Graphics": "TOG",
    "IEEE Transactions on Image Processing": "TIP",
    "IEEE Transactions on Visualization and Computer Graphics": "TVCG",
    "IEEE Transactions on Neural Networks and Learning Systems": "TNNLS",
    "IEEE Transactions on Multimedia": "TMM",
    "IEEE Transactions on Circuits and Systems for Video Technology": "TCSVT",
    "IEEE Transactions on Intelligent Transportation Systems": "TITS",
    "The Visual Computer": "TVC",
    "IEEE Transactions on Computational Imaging": "TCI",
    "IEEE Transactions on Instrumentation and Measurement": "TIM",
    "Pattern Recognition": "PR",
    "Information Fusion": "InfFus",
    "IEEE/CAA Journal of Automatica Sinica": "JAS",
    "IEEE Signal Processing Letters": "SPL",
    "Vision Research": "VR",
    "Journal of Vision": "JOV",
    "Journal of Computer Science and Technology": "JCST",
    "Computer Graphics Forum": "CGF",
    "Computational Visual Media": "CVM",
    "Applied Intelligence": "Appl. Intell.",
    "Pattern Recognition Letters": "Pattern Recogn. Lett.",
    "Proceedings of the IEEE/CVF International Conference on Computer Vision": "ICCV",
}

# ======================== LLM Provider Configuration ========================
# Auto-configure API URL and headers based on provider
_provider = LLM_PROVIDER.lower()

if _provider == "deepseek":
    LLM_API_URL = "https://api.deepseek.com/v1/chat/completions"
    LLM_API_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
elif _provider == "qwen":
    LLM_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    LLM_API_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
elif _provider == "kimi":
    LLM_API_URL = "https://api.moonshot.cn/v1/chat/completions"
    LLM_API_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
elif _provider in ("gpt", "openai"):
    LLM_API_URL = "https://api.openai.com/v1/chat/completions"
    LLM_API_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
elif _provider == "claude":
    LLM_API_URL = "https://api.anthropic.com/v1/messages"
    LLM_API_HEADERS = {
        "Content-Type": "application/json",
        "x-api-key": LLM_API_KEY,
        "anthropic-version": "2023-06-01"
    }
elif _provider == "gemini":
    LLM_API_URL = f"https://generativelanguage.googleapis.com/v1/models/{LLM_MODEL}:generateContent"
    LLM_API_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
else:
    raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")

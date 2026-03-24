# VeriBib - AI 论文引用核验工具

<p align="center">
  <img src="https://img.shields.io/badge/LLM_Support-8%2B-green" alt="LLM Support">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-orange" alt="License">
</p>

> 通过与谷歌学术（Google Scholar）比对核验 BibTeX 引用，检测 AI 幻觉和虚假参考文献。

[English](README.md) | [简体中文](README_CN.md)

## 为什么选择 VeriBib？

随着大语言模型（如 ChatGPT、Claude 和 DeepSeek）在学术写作中的广泛应用，一个严重的问题浮出水面：**引用幻觉（Citation Hallucination）**。AI 模型经常捏造听起来很合理但完全虚假的论文，将真实的作者与错误的标题混搭，或者幻觉出不存在的出版场所（期刊/会议）。

**VeriBib** 旨在作为参考文献列表的自动化事实核查工具。它通过以下方式帮助研究人员核验其 BibTeX 引用：

- 将引用与谷歌学术进行交叉比对，检测完全捏造的虚假论文。
- 识别“部分幻觉”（例如：论文标题是真实的，但作者或出版年份是 AI 幻觉捏造的）。
- 使用可靠的大语言模型（LLMs）进行分析，将生成的元数据与经过核实的真实来源进行匹配。
- 确保您的参考文献在提交前真实、准确且符合学术严谨性。

## 核心功能

- 🚨 **幻觉检测**：即时标记在真实学术数据库中不存在的完全捏造的论文或“幽灵引用”。
- 🔍 **事实核查搜索**：抓取谷歌学术数据以验证论文的实际存在性，并获取其真实的元数据。
- 🤖 **基于 LLM 的核验**：智能比对您的 BibTeX 条目与真实世界的搜索结果，以捕捉 AI 生成的细微错误（如作者列表混乱或期刊幻觉）。
- 📊 **智能匹配**：检测由 AI 混淆导致的作者姓名变体、出版场所差异和年份不匹配。
- 📝 **灵活输出**：生成 Markdown、JSON 或纯文本报告，清晰高亮已核实的引用与幻觉生成的引用。
- 🔌 **多 LLM 提供商支持**：支持 10+ 种 LLM API 来执行核验分析。

## 支持的大语言模型 (LLMs)

| 提供商 (Provider) | 模型 (Model) | 别名 (Alias) |
| --------- | ------------------- | --------------------- |
| DeepSeek | DeepSeek | `deepseek` |
| OpenAI | GPT-4o, GPT-4o-mini | `openai`, `gpt` |
| Google | Gemini Flash/Pro | `gemini`, `google` |
| Anthropic | Claude Sonnet 4.6 | `claude`, `anthropic` |
| 阿里巴巴 (Alibaba) | Qwen Plus/Turbo | `qwen`, `alibaba` |
| 月之暗面 (Moonshot) | Kimi | `kimi`, `moonshot` |
| 稀宇科技 (MiniMax) | Text-01 | `minimax` |
| 智谱AI (Zhipu) | GLM-4 Flash | `glm`, `zhipu` |

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置 API 密钥

编辑 `config.py` 文件：

```python
# ScraperAPI - 可以在 https://scraperapi.com 获取 5000 免费请求额度
SCRAPER_API_KEY = "your_scraperapi_key"

# LLM API (选择其中一个)
LLM_API_KEY = "your_openai_key"  # 或者是 DeepSeek, Anthropic 等的密钥
LLM_PROVIDER = "deepseek"  # 默认使用 deepseek
```

> 💡 **提示**：ScraperAPI 为新用户提供 5000 免费 API 请求额度，足以核验数百篇论文。

### 3. 运行核验

```bash
# 基础用法
python run.py paper.bib

# 包含详细的论文版本信息
python run.py papers.bib --detailed

# 使用指定的大语言模型
python run.py papers.bib --llm openai

# 输出 JSON 格式以便自动化处理
python run.py papers.bib -f json -o results.json
```

## 输出示例

```text
| # | 引用键 (Cite Key) | 标题 (Title) | 检索结果 (Found) | 年份 (Year) | 期刊/会议 (Journal/Conf) | 作者 (Authors) |
|---|----------|-------|-------|------|-------------|--------|
| 1 | chen2024transformer | xxx | 找到 5 个版本 | [OK] 2024 | [OK] NeurIPS | [OK] Chen, X |
```

## 命令行选项 (CLI Options)

| 选项 | 描述 |
| ---------------- | ------------------------------------------------------------ |
| `--llm, -l` | 指定 LLM 提供商 (deepseek/openai/gemini/claude/qwen/kimi/minimax/glm) |
| `--output, -o` | 指定输出文件路径 |
| `--format, -f` | 指定输出格式 (markdown/txt/json) |
| `--detailed, -d` | 在输出报告中包含所有检索到的论文版本信息 |

## 应用场景

### AI 研究人员

- 核验顶级会议论文（如 NeurIPS, ICML, CVPR, ICCV, ACL, EMNLP 等）
- 将 arXiv 预印本与最终发表的正式版本进行对比核对
- 验证作者姓名和所属机构的准确性

### 学术论文作者

- 在提交论文前确保引用准确无误
- 将生成的 BibTeX 与实际发表的官方版本进行比对
- 生成文献核验报告作为论文的补充材料

### 实验室与研究机构

- 批量核验整个团队的引用数据库
- 集成到 CI/CD 自动化工作流中
- 导出 JSON 格式数据以便更新内部文献数据库

## 项目结构

```text
bib_checker/
├── config.py          # API 密钥与全局设置
├── run.py             # 命令行程序入口
├── bib_parser.py      # BibTeX 文件解析
├── scraper.py         # 谷歌学术数据抓取
├── analyze.py         # LLM 智能分析与比对
├── llm_adapter.py     # 多 LLM 接口适配器
├── formatter.py       # 报告输出格式化
└── README.md
```

## 开源协议

MIT License

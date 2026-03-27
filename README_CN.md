# VeriBib - AI 论文引用校验工具

<p align="center">
  <img src="https://img.shields.io/badge/LLM_Support-6%2B-green" alt="LLM Support">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-orange" alt="License">
</p>

> 使用 Semantic Scholar 校验并修复 BibTeX 引用，检测 AI 幻觉和错误参考文献。

[English](README.md) | [简体中文](README_CN.md)

## 什么是 VeriBib？

随着大语言模型（如 ChatGPT、Claude 和 DeepSeek）在学术写作中的广泛应用，一个严重的问题浮出水面：**引用幻觉（Citation Hallucination）**。AI 模型经常捏造听起来很合理但完全虚假的论文，将真实的作者与错误的标题混搭，或者幻觉出不存在的出版场所（期刊/会议）。

**VeriBib** 旨在作为参考文献列表的自动化事实核查工具。它通过以下方式帮助研究人员校验其 BibTeX 引用：

- 将引用与 Semantic Scholar 进行交叉比对，检测完全捏造的虚假论文。
- 识别"部分幻觉"（例如：论文标题是真实的，但作者或出版年份是 AI 幻觉捏造的）。
- 使用可靠的大语言模型（LLM）进行分析，将生成的元数据与经过核实的真实来源进行匹配。
- 自动将会议和期刊名称缩写为标准格式（ICML、CVPR、IEEE TPAMI 等）。
- 确保您的参考文献在提交前真实、准确且符合学术严谨性。

## 核心功能

- 🚨 **幻觉检测**：即时标记在真实学术数据库中不存在的完全捏造的论文或"幽灵引用"。
- 🔍 **事实核查搜索**：查询 Semantic Scholar 以验证论文的实际存在性，并获取其真实的元数据。
- 🤖 **基于 LLM 的校验**：智能比对您的 BibTeX 条目与真实世界的搜索结果，以捕捉 AI 生成的细微错误（如作者列表混乱或期刊幻觉）。
- 📊 **智能匹配**：检测由 AI 混淆导致的作者姓名变体、出版场所差异和年份不匹配。
- 🔄 **自动修复**：自动获取正确的元数据（标题、作者、年份、DOI）并标准化出版物缩写。
- 📝 **灵活输出**：生成 Markdown 报告和优化后的 BibTeX 文件，并排显示原始条目与更新条目的对比。
- 🔌 **多 LLM 提供商支持**：支持 6+ 种 LLM API 来执行校验分析。

## 支持的大语言模型 (LLMs)

| 提供商 (Provider) | 模型 (Model) | 别名 (Alias) |
| --------- | ------------------- | --------------------- |
| DeepSeek | DeepSeek Chat | `deepseek` |
| OpenAI | GPT-4o, GPT-4o-mini | `openai`, `gpt` |
| Google | Gemini | `gemini` |
| Anthropic | Claude | `claude` |
| 阿里巴巴 | Qwen | `qwen` |
| 月之暗面 | Kimi | `kimi` |

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置 API 密钥

编辑 `config.py` 文件：

```python
# Semantic Scholar API 密钥（免费）
SS_API_KEY = "your_semantic_scholar_key"

# LLM API 密钥（选择其一）
LLM_API_KEY = "your_llm_key"
LLM_PROVIDER = "deepseek"  # deepseek, qwen, kimi, gpt, openai, claude, gemini
LLM_MODEL = "deepseek-chat"
```

> 💡 **提示**：Semantic Scholar 为学术研究提供免费 API，每秒 100 次请求额度。

### 3. 运行校验

```bash
# 基础用法
python main.py input.bib

# 自定义输出文件
python main.py input.bib -o fixed.bib -r report.md

# 跳过输出文件
python main.py input.bib --no-output --no-report
```

## 输出示例

### Markdown 报告
| Status | Key | Orig author | Orig journal | Orig title | Orig year | New title | New author | New year | New journal | New booktitle | New doi | SS Link |
|--------|----|---|---|---|---|---|---|---|---|---|---|--------|
| ⚠️ Mismatch | radford2021learning | Radford, Alec and Kim, Jong Wook and Hallacy, Chris and Ramesh, Aditya and Goh, Gabriel and Agarwal, Sandhini and Sastry, Girish and Askell, Amanda and Mishkin, Pamela and Clark, Jack and others | arXiv preprint arXiv:2103.00020 | Learning Transferable Visual Models From Natural Language Supervision | 2021 | Learning Transferable Visual Models From Natural Language Supervision | Alec Radford and Jong Wook Kim and Chris Hallacy and A. Ramesh and Gabriel Goh and S. Agarwal and G. Sastry and Amanda Askell and Pamela Mishkin and Jack Clark and Gretchen Krueger and I. Sutskever | 2021 | International Conference on Machine Learning | ICML | - | - |

### 优化后的 BibTeX
```bibtex
# 原始 BibTeX
@article{radford2021learning,
  title={Learning Transferable Visual Models From Natural Language Supervision},
  author={Radford, Alec and Kim, Jong Wook and Hallacy, Chris and Ramesh, Aditya and Goh, Gabriel and Agarwal, Sandhini and Sastry, Girish and Askell, Amanda and Mishkin, Pamela and Clark, Jack and others},
  journal={arXiv preprint arXiv:2103.00020},
  year={2021}
}

# 优化后的 BibTex
@inproceedings{radford2021learning,
  title={Learning Transferable Visual Models From Natural Language Supervision},
  author={Alec Radford and Jong Wook Kim and Chris Hallacy and A. Ramesh and Gabriel Goh and S. Agarwal and G. Sastry and Amanda Askell and Pamela Mishkin and Jack Clark and Gretchen Krueger and I. Sutskever},
  booktitle={ICML},
  year={2021},
}
```

## 命令行选项 (CLI Options)

| 选项 | 描述 |
| ---------------- | ------------------------------------------------------------ |
| `input` | 输入 BibTeX 文件（默认: test.bib） |
| `-o, --output` | 输出优化后的 BibTeX 文件（默认: output_updated.bib） |
| `--no-output` | 跳过 BibTeX 输出 |
| `-r, --report` | 输出报告文件（默认: bib_report.md） |
| `--no-report` | 跳过报告输出 |

## 应用场景

### AI 研究人员

- 校验顶级会议论文（如 NeurIPS、ICML、CVPR、ICCV、ACL、EMNLP 等）
- 将 arXiv 预印本与最终发表的正式版本进行对比核对
- 验证作者姓名和所属机构的准确性

### 学术论文作者

- 在提交论文前确保引用准确无误
- 将生成的 BibTeX 与实际发表的官方版本进行比对
- 生成文献校验报告作为论文的补充材料

### 实验室与研究机构

- 批量校验整个团队的引用数据库
- 导出优化后的 BibTeX 以便更新内部文献数据库

## 项目结构

```text
bib_checker/
├── config.py            # API 密钥与全局设置
├── main.py              # 命令行程序入口
├── bib_parser.py        # BibTeX 文件解析
├── semantic_scholar.py  # Semantic Scholar API 客户端
├── matcher.py           # LLM 智能分析与比对
├── venue_utils.py       # 出版物缩写生成
├── exporter.py         # 报告输出格式化
├── test.bib            # 示例输入文件
└── README.md
```

## 出版物缩写

内置字典包含 40+ 常用出版物：
- **会议**: CVPR、ICCV、ECCV、NeurIPS、ICLR、ICML、IJCAI、MICCAI、AAAI、ACMMM、BMVC 等
- **期刊**: IEEE TPAMI、IJCV、TIP、TVCG、TNNLS、TMM、PR、InfFus 等

LLM 还可以根据已知模式为未知出版物生成缩写。

## 开源协议

MIT License

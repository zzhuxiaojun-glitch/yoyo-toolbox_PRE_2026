# YOYO's Toolbox 2026

[简体中文](README.md) | [日本語](README.ja.md) | **English**

YOYO's Toolbox: a curated selection of the apps and tools I built in 2026.

- **Web apps**: open the link and use them right away
- **Desktop tools**: download from [Releases](../../releases/latest)
- **Claude Code skills / scripts**: in this repo's [`skills/`](skills) and [`scripts/`](scripts)

---

## 🌐 Web apps

| App | Description | URL |
|---|---|---|
| **JLPTsimu** | JLPT (Japanese-Language Proficiency Test) mock exams, study-progress tracking, and a knowledge base | https://jlptsimu.manga-re.com |
| **FEsimu** | Question bank and practice exams for Japan's Fundamental / Applied Information Technology Engineer Examinations | https://fe-siken.manga-re.com |

## 🧰 Desktop tools (Windows)

Download them from [Releases](../../releases/latest).

| Tool | Description | File |
|---|---|---|
| **MangaTL** | Semi-automatic Japanese→Chinese manga translation and typesetting: speech-bubble detection (YOLO), manga-ocr text recognition, sentence-by-sentence translation with a per-series glossary, and a typesetting editor. Exports Chinese EPUB, LabelPlus, and proofreading drafts | `MangaTL-Setup-0.1.0.exe` |
| **BatchRename** | GUI tool for batch-renaming files and extensions; when you change extensions to zip, it can batch-extract them too | `BatchRenameGUI.exe` |
| **TranEPUB** | Batch-converts image folders or ZIPs into EPUB, via a web UI or the command line ([source](https://github.com/zzhuxiaojun-glitch/TranEPUB_DeskTopAPP)) | `TranEPUB_DeskTopAPP_v1.0.zip` |

<details>
<summary>Installation</summary>

- **MangaTL**: double-click to install. Models and fonts download automatically on first launch.
- **BatchRename**: no installation needed; double-click to run.
- **TranEPUB**: unzip and double-click `TranEPUB.bat`. Requires Python 3.10+; if you don't have it, run `setup_python.bat` first.

> These programs are not code-signed, so Windows SmartScreen may warn you on first launch. Click "More info → Run anyway".

</details>

## 📦 Other projects

| Project | Description | Repository |
|---|---|---|
| **Nihongo Kaiwa** | Japanese conversation-practice web app: AI dialogue, speech recognition, and speech synthesis (Vue 3 + Go) | Source not yet public |
| **jmdict-cn** | Chinese version of the JMdict Japanese dictionary, with added Japanese–Chinese example sentences | [jmdict-cn](https://github.com/zzhuxiaojun-glitch/jmdict-cn) |

## 🤖 Claude Code skills and scripts

Copy the whole `skills/<name>/` folder into `~/.claude/skills/` to use it.

| Name | Purpose |
|---|---|
| [manga-img-to-epub](skills/manga-img-to-epub) | Converts image folders into standard EPUB3, with batch mode; defaults to right-to-left page order like Japanese manga |
| [playwright-mcp-uitest](skills/playwright-mcp-uitest) | Walks through UI flows in a real browser via Playwright MCP to verify frontend changes |
| [dispatch-board](skills/dispatch-board) | Splits large batches of similar work into task tickets that several Claude Code sessions can claim and work on in parallel, with an auto-generated progress dashboard |
| [project-db-query-audit](skills/project-db-query-audit) | End-to-end database query optimization: static audit (N+1 and more) → EXPLAIN ANALYZE baseline → one fix at a time → errata review |
| [themed-mascot-designer](skills/themed-mascot-designer) | Designs a themed mascot set for a project: personality profiles → clearly distinct designs → an image-generation prompt document |
| [yoyo_dev](skills/yoyo_dev) | My own cross-project dev habits: TDD, PR writing, avoiding git conflicts across parallel sessions, resumable batch jobs, and more |
| [statusline.py](scripts/statusline.py) | Three-row status line for Claude Code: collapses to 1–3 rows depending on terminal width and shows model, branch, context usage, and more. Setup instructions are in the comment at the top of the file |

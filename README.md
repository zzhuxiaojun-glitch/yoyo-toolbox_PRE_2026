# YOYO's Toolbox 2026

**简体中文** | [日本語](README.ja.md) | [English](README.en.md)

YOYO 的工具箱：我 2026 年做的应用和工具精选。

- **在线应用**：点开就能用
- **桌面工具**：在 [Releases](../../releases/latest) 下载
- **Claude Code skills / 脚本**：在本仓库的 [`skills/`](skills) 和 [`scripts/`](scripts)

---

## 🌐 在线应用

| 应用 | 简介 | 地址 |
|---|---|---|
| **JLPTsimu** | JLPT 日语能力考模拟考试 + 学习进度追踪 + 知识库 | https://jlptsimu.manga-re.com |
| **FEsimu** | 基本情報 / 応用情報技術者試験的题库与模拟练习 | https://fe-siken.manga-re.com |

## 🧰 桌面工具（Windows）

在 [Releases](../../releases/latest) 下载。

| 工具 | 简介 | 下载文件 |
|---|---|---|
| **MangaTL** | 日语漫画半自动翻译 + 中文嵌字：气泡检测（YOLO）、manga-ocr 识别、带术语库的逐句翻译、嵌字编辑器，可导出中文 EPUB / LabelPlus / 审校稿 | `MangaTL-Setup-0.1.0.exe` |
| **BatchRename** | 批量改文件名 / 后缀名的图形界面工具；改成 zip 时可以接着批量解压 | `BatchRenameGUI.exe` |
| **TranEPUB** | 把图片文件夹或 ZIP 批量打包成 EPUB，有网页界面和命令行两种用法（[源码](https://github.com/zzhuxiaojun-glitch/TranEPUB_DeskTopAPP)） | `TranEPUB_DeskTopAPP_v1.0.zip` |

<details>
<summary>安装说明</summary>

- **MangaTL**：双击安装。第一次启动会自动下载模型和字体。
- **BatchRename**：免安装，双击运行。
- **TranEPUB**：解压后双击 `TranEPUB.bat`。需要 Python 3.10+，没有的话先运行 `setup_python.bat`。

> 这些程序没有代码签名，第一次运行时 Windows SmartScreen 可能会提示风险，点「详细信息 → 仍要运行」即可。

</details>

## 📦 其他项目

| 项目 | 简介 | 仓库 |
|---|---|---|
| **Nihongo Kaiwa** | 日语会话练习 Web 应用：AI 对话、语音识别、语音合成（Vue 3 + Go） | 源码暂未公开 |
| **jmdict-cn** | JMdict 日语词典的中文版，添加了中日对译例句 | [jmdict-cn](https://github.com/zzhuxiaojun-glitch/jmdict-cn) |

## 🤖 Claude Code skills 与脚本

把 `skills/<名字>/` 整个文件夹复制到 `~/.claude/skills/` 下就能用。

| 名称 | 用途 |
|---|---|
| [manga-img-to-epub](skills/manga-img-to-epub) | 把图片文件夹转成标准 EPUB3，支持批量，默认按日漫的右→左翻页 |
| [playwright-mcp-uitest](skills/playwright-mcp-uitest) | 用 Playwright MCP 在真浏览器里走一遍 UI 流程，验证前端改动 |
| [dispatch-board](skills/dispatch-board) | 把大批量同类任务拆成多个任务单，让多个 Claude Code 会话并行认领推进，并自动汇总进度面板 |
| [project-db-query-audit](skills/project-db-query-audit) | 数据库查询优化的完整流程：静态审计（N+1 等）→ EXPLAIN ANALYZE 基线 → 逐条修复 → 勘误复核 |
| [themed-mascot-designer](skills/themed-mascot-designer) | 为项目设计一整套主题吉祥物：性格档案 → 区分明显的造型 → 生图提示词文档 |
| [yoyo_dev](skills/yoyo_dev) | 我自己的跨项目开发习惯：TDD、PR 写法、多会话 git 防冲突、批量任务断点续跑等 |
| [statusline.py](scripts/statusline.py) | Claude Code 三行状态栏：根据终端宽度自动变成 1～3 行，显示模型、分支、上下文用量等。安装方法见文件开头的注释 |

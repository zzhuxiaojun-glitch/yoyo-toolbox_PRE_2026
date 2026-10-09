# manga-img-to-epub

> Convert a folder of manga/comic images (jpg/png/webp) into a standards-compliant…

## 这是啥

这是一个 Claude Code Skill，使用时由 Claude 自动调用（基于触发关键词匹配）。完整的工作流定义、约束、示例都写在 [SKILL.md](SKILL.md) 里——下面"## 详细规范"段就是 SKILL.md 的原文，把它当成 AI + 人类共用的说明书读。

本文档（USAGE.md）是给**人**看的入口：列触发方式、依赖、文件位置和卸载方法。技术细节直接看 SKILL.md 正文。

## 怎么用

### 触发方式

在 Claude Code 会话里说下面这些关键词会触发本 skill：

- （从 SKILL.md description 自动提取失败，请直接看下方完整规范）

完整触发条件参见下方"## 详细规范"。

### 完整规范

skill 的所有行为约束、流程步骤、参数说明、示例、模板，全部在 SKILL.md 里有。下面段就是 SKILL.md 的内容，**改 skill 行为只改 SKILL.md，本文档自动派生**。

## 文件位置

| 路径 | 内容 |
|---|---|
| `~/.claude/skills/manga-img-to-epub/SKILL.md` | AI 触发规则 + 完整工作流（人类也读这个） |
| `~/.claude/skills/manga-img-to-epub/USAGE.md` | 本文档（人类入口 / 简介 / 卸载） |
| `~/.claude/skills/manga-img-to-epub/scripts/__pycache__/img2epub.cpython-312.pyc` |  |
| `~/.claude/skills/manga-img-to-epub/scripts/img2epub.py` | 脚本 |


## 已知坑 / 局限

> 截至 2026-05-04 暂无已记录的踩坑。使用中遇到反直觉行为或外部依赖陷阱，追加到这里。

（建议关注的常见坑：外部 CLI 版本不兼容 / API 限额 / Supabase RLS / 路径硬编码 / 系统包缺失等）

## 卸载 / 关闭

```bash
# 完全删除：
rm -rf ~/.claude/skills/manga-img-to-epub/

# 临时禁用（不再被 AI 触发，但保留代码）：
# 编辑 ~/.claude/skills/manga-img-to-epub/SKILL.md，把 description 字段改成空或加 "（已禁用）" 前缀
```

---

## 详细规范（SKILL.md 原文）

> 以下内容来自 [SKILL.md](SKILL.md)，是给 AI 看的工作流定义；人类读这段就是详细操作手册。

# 漫画图片 → EPUB 转换

把一个装满漫画页图片的文件夹打包成一个 EPUB3 文件。支持批量：把一个父目录下的每个子目录（每话）分别打成一个 EPUB。

## 何时使用
- 用户有图片文件夹（000.jpg、001.jpg…）想生成 .epub
- 用户说「把每话做成一个 epub」「打包成 epub」「图片转 epub」「做成电子书」
- 下载到的漫画是散图，需要做成阅读器友好的电子书

## 不适用
- EPUB → 分析/摘要 → 用 `manga-epub-analysis`
- 从网站下载漫画 → 用 `manga-dl` 或 `manga-resource-workflow`

## 用法

单本模式：
```bash
python3 scripts/img2epub.py "<图片文件夹>" [-o <输出.epub>] [--title "标题"] [--author "作者"] [--ltr]
```

批量模式（每个子目录一本 epub）：
```bash
python3 scripts/img2epub.py "<父目录>" --batch [--out-dir <输出目录>] [--author "作者"] [--ltr]
```

参数：
- `--ltr`：左→右（欧美漫画/普通书）。缺省是右→左（日系漫画）。
- `--title`：不指定时用目录名。
- `-o`：单本输出路径，不指定时放在图片目录旁边。
- `--out-dir`：批量输出目录，不指定时放回父目录本身。

## 输出特点
- EPUB3，`rendition:layout=pre-paginated`，阅读器会把每张图当一页完整显示
- `page-progression-direction` 默认 `rtl`（日漫）
- 首图自动标记为 `cover-image`
- 图片自然排序（000.jpg < 001.jpg < 002.jpg）
- 需要 Python3 + Pillow（读取首图尺寸用；没有 Pillow 时用 1200×1800 占位）

## 典型工作流

```bash
# 把 [Q]青春爆走！_jpg/23-44/ 下 22 个「第XX話」子目录各做一本 epub
python3 scripts/img2epub.py "/path/to/23-44/" --batch --author "青春爆走！"
# → /path/to/23-44/第23話 バカだなあ.epub ...（共 22 本）
```

---

*USAGE.md 由 `~/.claude/auto-resume/gen_usage.py` 派生自 SKILL.md。改 SKILL.md 后重跑该脚本同步。*

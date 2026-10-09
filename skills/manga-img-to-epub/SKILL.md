---
name: manga-img-to-epub
description: Convert a folder of manga/comic images (jpg/png/webp) into a standards-compliant EPUB3 file, or batch-convert every subfolder of a parent directory into individual EPUB files. Use when the user wants to package image pages into .epub, turn a chapter folder into an ebook, or make manga epubs for reading apps. Defaults to right-to-left page progression (Japanese manga).
---

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
python3 scripts/img2epub.py "<父目录>" --batch [--out-dir <输出目录>] [--author "作者"] [--ltr] [--merge-parts]
```

参数：
- `--ltr`：左→右（欧美漫画/普通书）。缺省是右→左（日系漫画）。
- `--title`：不指定时用目录名。
- `-o`：单本输出路径，不指定时放在图片目录旁边。
- `--out-dir`：批量输出目录，不指定时放回父目录本身。如果它是父目录的下级，会自动从扫描列表里排除自己（不会把输出目录当作话来处理）。
- `--merge-parts`（仅批量）：把同一话的「前編/後編」「上/中/下」「Part 1/Part 2」等多个文件夹合并成一本 epub。

### `--merge-parts` 配对规则
- 识别这些标记（必须用 `(…)` / `（…）` 包裹，或者 `Part N` / `Pt.N` 独立词）：
  - 前 / 前篇 / 前編 / 上 / 上篇 / 上編 → 排第 1
  - 中 / 中篇 / 中編ち → 排第 2
  - 後 / 後篇 / 後編 / 下 / 下篇 / 下編 → 排第 3
  - `Part 1` / `Pt.1` / `Part 2` … → 按数字排
- 同一「话」的判定 = 去掉标记后的目录名一致。例：
  - `第47話(前編) 心強い協力者` + `第47話(後編) 心強い協力者` → 合成 `第47話 心強い協力者.epub`
- 只找到一半（比如有 後編 没前編）时不合并，按原文件名单独成本，标记保留以提示遗漏。

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

# 前後編が混在する場合: 第47話(前編)+第47話(後編) → 第47話.epub 1 本にマージ
python3 scripts/img2epub.py "/path/to/[S]獣王と薬草（日本語）/" --batch --merge-parts \
    --out-dir "/path/to/[S]獣王と薬草（日本語）/【epub】" \
    --author "獣王と薬草"
# → 22 個のサブフォルダ → 16 epub（6 組が前後編マージ、10 本が単独）
```

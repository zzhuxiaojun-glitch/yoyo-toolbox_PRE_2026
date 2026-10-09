#!/usr/bin/env python3
"""
Image folder → manga EPUB3 converter.

Usage:
    img2epub.py <image_folder> [-o OUTPUT] [--title TITLE] [--author AUTHOR] [--ltr]
    img2epub.py --batch <parent_folder> [--out-dir DIR] [--author AUTHOR] [--ltr] [--merge-parts]

Defaults to right-to-left page progression (Japanese manga).
Batch mode: treats each subfolder as one chapter, emits one .epub per subfolder.
With --merge-parts: 前編/後編 (上/中/下, Part 1/Part 2, etc.) sibling folders are
merged into a single .epub per chapter.
"""

import argparse
import mimetypes
import re
import sys
import uuid
import zipfile
from pathlib import Path

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def natural_key(p):
    name = p.name if isinstance(p, Path) else str(p)
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def collect_images(folder: Path):
    return sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMG_EXTS],
        key=natural_key,
    )


def mime_of(p: Path) -> str:
    ext = p.suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(ext, mimetypes.guess_type(p.name)[0] or "application/octet-stream")


def xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


CONTAINER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def build_content_opf(title, author, uid, images, direction):
    manifest = []
    spine = []
    for i, (img, ext) in enumerate(images, start=1):
        img_id = f"img{i:04d}"
        xhtml_id = f"p{i:04d}"
        manifest.append(
            f'    <item id="{img_id}" href="images/{xhtml_id}{ext}" media-type="{mime_of(img)}"/>'
        )
        manifest.append(
            f'    <item id="{xhtml_id}" href="xhtml/{xhtml_id}.xhtml" media-type="application/xhtml+xml"/>'
        )
        spine.append(f'    <itemref idref="{xhtml_id}"/>')

    cover_props = ' properties="cover-image"' if images else ""
    if images:
        manifest[0] = manifest[0].replace('media-type="', f'{cover_props} media-type="', 1)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="BookId" prefix="rendition: http://www.idpf.org/vocab/rendition/#">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="BookId">urn:uuid:{uid}</dc:identifier>
    <dc:title>{xml_escape(title)}</dc:title>
    <dc:creator>{xml_escape(author)}</dc:creator>
    <dc:language>ja</dc:language>
    <meta property="dcterms:modified">2024-01-01T00:00:00Z</meta>
    <meta property="rendition:layout">pre-paginated</meta>
    <meta property="rendition:orientation">portrait</meta>
    <meta property="rendition:spread">landscape</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
{chr(10).join(manifest)}
  </manifest>
  <spine toc="ncx" page-progression-direction="{direction}">
{chr(10).join(spine)}
  </spine>
</package>
"""


def build_nav_xhtml(title, images):
    items = "\n".join(
        f'      <li><a href="xhtml/p{i:04d}.xhtml">Page {i}</a></li>'
        for i in range(1, len(images) + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>{xml_escape(title)}</title></head>
<body>
  <nav epub:type="toc" id="toc"><h1>Contents</h1><ol>
{items}
  </ol></nav>
</body>
</html>
"""


def build_ncx(title, uid, images):
    points = "\n".join(
        f'    <navPoint id="p{i:04d}" playOrder="{i}"><navLabel><text>Page {i}</text></navLabel><content src="xhtml/p{i:04d}.xhtml"/></navPoint>'
        for i in range(1, len(images) + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:{uid}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{xml_escape(title)}</text></docTitle>
  <navMap>
{points}
  </navMap>
</ncx>
"""


def build_page_xhtml(page_num, filename, width=1200, height=1800):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>Page {page_num}</title>
  <meta name="viewport" content="width={width}, height={height}"/>
  <style>
    html, body {{ margin:0; padding:0; height:100%; }}
    body {{ display:flex; align-items:center; justify-content:center; background:#000; }}
    img {{ max-width:100%; max-height:100%; display:block; }}
  </style>
</head>
<body>
  <img src="../images/{filename}" alt="Page {page_num}"/>
</body>
</html>
"""


def get_image_size(path: Path):
    try:
        from PIL import Image  # type: ignore

        with Image.open(path) as im:
            return im.size
    except Exception:
        return (1200, 1800)


def make_epub(folders, out_path: Path, title: str, author: str, direction: str):
    """folders: a Path or a list[Path]. Multiple folders are concatenated in order."""
    if isinstance(folders, Path):
        folders = [folders]

    images = []
    for f in folders:
        images.extend(collect_images(f))
    if not images:
        names = ", ".join(f.name for f in folders)
        print(f"  [skip] no images in {names}", file=sys.stderr)
        return False

    uid = str(uuid.uuid4())
    indexed = [(p, p.suffix.lower()) for p in images]
    first_w, first_h = get_image_size(images[0])

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zi = zipfile.ZipInfo("mimetype")
        zi.compress_type = zipfile.ZIP_STORED
        zf.writestr(zi, "application/epub+zip")

        zf.writestr("META-INF/container.xml", CONTAINER_XML)
        zf.writestr("OEBPS/content.opf", build_content_opf(title, author, uid, indexed, direction))
        zf.writestr("OEBPS/toc.ncx", build_ncx(title, uid, indexed))
        zf.writestr("OEBPS/nav.xhtml", build_nav_xhtml(title, indexed))

        for i, (img, ext) in enumerate(indexed, start=1):
            xhtml_id = f"p{i:04d}"
            zf.write(img, f"OEBPS/images/{xhtml_id}{ext}")
            w, h = get_image_size(img) if i == 1 else (first_w, first_h)
            zf.writestr(
                f"OEBPS/xhtml/{xhtml_id}.xhtml",
                build_page_xhtml(i, f"{xhtml_id}{ext}", w, h),
            )

    suffix = f" from {len(folders)} folder(s)" if len(folders) > 1 else ""
    print(f"  [ok] {out_path.name} ({len(images)} pages{suffix})")
    return True


# ---- 前後編/上中下/Part マージ用 ----

# (marker_regex_fragment, sort_order). Try longer markers first so "前篇" doesn't
# get partially matched by "前".
PART_MARKERS = [
    (r"前編", 1), (r"前篇", 1), (r"上篇", 1), (r"上編", 1),
    (r"中編", 2), (r"中篇", 2),
    (r"後編", 3), (r"後篇", 3), (r"下篇", 3), (r"下編", 3),
    (r"前", 1), (r"上", 1),
    (r"中", 2),
    (r"後", 3), (r"下", 3),
]


def detect_part(name: str):
    """If `name` contains a part marker (in parens, or Part N), return (base_name, order).
    Otherwise return (None, None)."""
    # Parenthesized marker — half-width () or full-width （）
    for marker, order in PART_MARKERS:
        for left, right in ((r"\(", r"\)"), ("（", "）")):
            pat = rf"\s*{left}\s*{marker}\s*{right}\s*"
            m = re.search(pat, name)
            if m:
                base = (name[: m.start()] + " " + name[m.end() :]).strip()
                base = re.sub(r"\s+", " ", base)
                return base, order
    # Part 1 / Part2 / Pt.1 (no parens required)
    m = re.search(r"\b(?:Part|Pt\.?)\s*(\d+)\b", name, re.IGNORECASE)
    if m:
        base = (name[: m.start()] + " " + name[m.end() :]).strip()
        base = re.sub(r"\s+", " ", base)
        return base, int(m.group(1))
    return None, None


def plan_batch(subs, merge_parts: bool):
    """Return [(display_title, [folder, ...]), ...] for batch emission.
    If merge_parts: group folders by base name (sans part marker) and sort by part order.
    A group of size 1 keeps its original folder name (so a lone 前編 stays labeled)."""
    items: list[tuple[str, list[Path]]] = []
    if not merge_parts:
        for s in subs:
            items.append((s.name, [s]))
        return items

    groups: dict[str, list[tuple[int, Path]]] = {}
    no_marker: list[Path] = []
    for s in subs:
        base, order = detect_part(s.name)
        if base is None:
            no_marker.append(s)
        else:
            groups.setdefault(base, []).append((order, s))

    for base, parts in groups.items():
        parts.sort(key=lambda x: x[0])
        if len(parts) >= 2:
            items.append((base, [p for _, p in parts]))
        else:
            f = parts[0][1]
            items.append((f.name, [f]))
    for s in no_marker:
        items.append((s.name, [s]))

    items.sort(key=lambda x: natural_key(x[0]))
    return items


def main():
    ap = argparse.ArgumentParser(description="Convert image folder(s) to manga EPUB3.")
    ap.add_argument("folder", type=Path, help="image folder, or parent folder in --batch mode")
    ap.add_argument("-o", "--output", type=Path, help="output .epub path (single mode)")
    ap.add_argument("--out-dir", type=Path, help="output directory (batch mode, default: same as parent)")
    ap.add_argument("--title", type=str, help="book title (default: folder name)")
    ap.add_argument("--author", type=str, default="", help="author/creator")
    ap.add_argument("--ltr", action="store_true", help="left-to-right (default: right-to-left)")
    ap.add_argument("--batch", action="store_true", help="treat subfolders as chapters")
    ap.add_argument(
        "--merge-parts",
        action="store_true",
        help="batch mode: merge sibling folders that share a base name and differ only by "
             "前編/後編 (or 上/中/下, Part 1/Part 2, etc.) into a single .epub per chapter",
    )
    args = ap.parse_args()

    direction = "ltr" if args.ltr else "rtl"

    if args.batch:
        parent = args.folder
        if not parent.is_dir():
            print(f"not a directory: {parent}", file=sys.stderr)
            sys.exit(1)
        out_dir = args.out_dir or parent
        # Exclude out_dir if it's a sibling under parent (avoid re-reading our own output).
        try:
            out_resolved = out_dir.resolve()
        except OSError:
            out_resolved = None
        subs = sorted(
            [
                p for p in parent.iterdir()
                if p.is_dir() and (out_resolved is None or p.resolve() != out_resolved)
            ],
            key=natural_key,
        )
        if not subs:
            print(f"no subfolders in {parent}", file=sys.stderr)
            sys.exit(1)

        plan = plan_batch(subs, args.merge_parts)
        print(f"Batch: {len(plan)} epub(s) from {len(subs)} folder(s) → {out_dir}")
        ok = 0
        for display, folders in plan:
            title = args.title or display
            out = out_dir / f"{display}.epub"
            if make_epub(folders, out, title, args.author, direction):
                ok += 1
        print(f"Done: {ok}/{len(plan)} epubs written.")
    else:
        folder = args.folder
        if not folder.is_dir():
            print(f"not a directory: {folder}", file=sys.stderr)
            sys.exit(1)
        title = args.title or folder.name
        out = args.output or folder.with_suffix(".epub")
        make_epub(folder, out, title, args.author, direction)


if __name__ == "__main__":
    main()

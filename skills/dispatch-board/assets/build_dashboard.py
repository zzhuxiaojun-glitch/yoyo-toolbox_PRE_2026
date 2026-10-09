#!/usr/bin/env python3
"""Generic dispatch-board dashboard generator.

读 dispatches/*/manifest.json + status/*.json → 重生 MASTER_PROGRESS.md + .html

v2 — 自动发现 categories（不再硬编码）：从每个 manifest.json 读 `category` / `label` / `order`。

Usage（在 dispatch-board root 目录下）：
    python3 build_dashboard.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DISPATCH_DIR = ROOT / "dispatches"
STATUS_DIR = ROOT / "status"
MD_OUT = ROOT / "MASTER_PROGRESS.md"
HTML_OUT = ROOT / "MASTER_PROGRESS.html"

PROJECT_NAME = ROOT.parent.name + " · dispatch board"  # 可改


def load_categories() -> list[dict]:
    """扫 dispatches/*/manifest.json，返回排序好的 category 列表。"""
    cats = []
    if not DISPATCH_DIR.exists():
        return cats
    for d in sorted(DISPATCH_DIR.iterdir()):
        if not d.is_dir():
            continue
        f = d / "manifest.json"
        if not f.exists():
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  warn: cannot parse {f}: {e}")
            continue
        cats.append({
            "key": data.get("category") or d.name,
            "label": data.get("label") or d.name,
            "order": data.get("order", 9999),
            "skill": data.get("skill", ""),
            "doc": data.get("doc", ""),
            "depends_on": data.get("depends_on", []),
            "entries": data.get("entries", []),
        })
    cats.sort(key=lambda c: (c["order"], c["key"]))
    return cats


def load_status() -> dict[str, dict]:
    """读 status/*.json，按 task_id 索引（slash 与 underscore 都支持）。"""
    out: dict[str, dict] = {}
    if not STATUS_DIR.exists():
        return out
    for f in sorted(STATUS_DIR.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  warn: skip {f.name}: {e}")
            continue
        tid = d.get("task_id")
        if not tid and "_" in f.stem:
            cat, _, _id = f.stem.partition("_")
            tid = f"{cat}/{_id}"
        if tid:
            out[tid] = d
    return out


def status_of(entry_id: str, cat_key: str, status_idx: dict) -> str:
    rec = status_idx.get(f"{cat_key}/{entry_id}") or status_idx.get(f"{cat_key}_{entry_id}")
    return (rec or {}).get("status", "pending") if rec else "pending"


def emoji(s: str) -> str:
    return {"done": "✅", "in_progress": "🟡", "blocked": "🚫", "pending": "⬜"}.get(s, "⬜")


def build_md(cats: list[dict], si: dict) -> str:
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    out = [
        f"# {PROJECT_NAME}",
        "",
        f"> 自动生成 — {now}（**手动改动会被 build_dashboard.py 覆盖**）",
        "",
        "## 一览",
        "",
        "| 类别 | 完成 | 进行中 | 阻塞 | 待办 | 总数 | 进度 |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    grand = {"done": 0, "in_progress": 0, "blocked": 0, "pending": 0, "total": 0}
    for c in cats:
        if not c["entries"]:
            continue
        cnt = {"done": 0, "in_progress": 0, "blocked": 0, "pending": 0}
        for e in c["entries"]:
            cnt[status_of(e["id"], c["key"], si)] += 1
        total = len(c["entries"])
        for k in cnt:
            grand[k] += cnt[k]
        grand["total"] += total
        pct = (cnt["done"] / total * 100) if total else 0
        bar = "█" * int(pct // 5) + "░" * (20 - int(pct // 5))
        out.append(
            f"| {c['label']} | {cnt['done']} | {cnt['in_progress']} | "
            f"{cnt['blocked']} | {cnt['pending']} | {total} | `{bar}` {pct:.0f}% |"
        )
    pct = (grand["done"] / grand["total"] * 100) if grand["total"] else 0
    bar = "█" * int(pct // 5) + "░" * (20 - int(pct // 5))
    out.append(
        f"| **合计** | **{grand['done']}** | **{grand['in_progress']}** | "
        f"**{grand['blocked']}** | **{grand['pending']}** | **{grand['total']}** | "
        f"`{bar}` **{pct:.0f}%** |"
    )
    out.append("")

    out += ["## 详细任务", ""]
    for c in cats:
        if not c["entries"]:
            continue
        out += [f"### {c['label']} ({c['key']})", ""]
        if c.get("doc"):
            out += [f"_{c['doc']}_", ""]
        if c.get("depends_on"):
            out += [f"依赖：{', '.join(c['depends_on'])}", ""]
        out += ["| ID | 状态 | 摘要 | 输出 / 备注 |", "|---|---|---|---|"]
        for e in c["entries"]:
            rec = si.get(f"{c['key']}/{e['id']}") or si.get(f"{c['key']}_{e['id']}") or {}
            st = rec.get("status", "pending")
            summary = e.get("summary", "")
            note = rec.get("notes", "")
            outs = rec.get("outputs", [])
            out_str = ", ".join(outs[:2]) + (f" (+{len(outs) - 2})" if len(outs) > 2 else "")
            extra = f" — {note}" if note else ""
            out.append(
                f"| `{c['key']}/{e['id']}` | {emoji(st)} {st} | {summary} | {out_str}{extra} |"
            )
        out.append("")

    out += [
        "## 多会话调用",
        "",
        "在新会话里说 **「执行 dispatch <category>/<id>」** 即可（如 `<example_cat>/003`）。",
        "agent 会读对应 TEMPLATE.md + manifest 自动跑流程。",
        "",
        "## 当前可立刻并行启动的任务",
        "",
    ]
    for c in cats:
        pending = sum(1 for e in c["entries"] if status_of(e["id"], c["key"], si) == "pending")
        if pending > 0:
            out.append(f"- {c['label']}（{c['key']}）：剩 {pending} 个 entry 待办")
    out += [
        "",
        "踩坑积累 → [pitfalls.md](pitfalls.md) · 用法 → [README.md](README.md)",
    ]
    return "\n".join(out) + "\n"


HTML_HEAD = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{title}</title>
<style>
  body { font: 14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif; background:#0d1117; color:#c9d1d9; margin:0; padding:20px; }
  h1 { color:#58a6ff; margin-top:0; }
  h2 { color:#7ee787; border-bottom:1px solid #30363d; padding-bottom:6px; margin-top:32px; }
  h3 { color:#d2a8ff; margin-top:24px; }
  .meta { color:#8b949e; font-size:12px; margin-bottom:24px; }
  .doc { color:#8b949e; font-style:italic; font-size:13px; margin:4px 0 8px; }
  .deps { color:#f0883e; font-size:12px; margin:4px 0 8px; }
  table { border-collapse:collapse; width:100%; margin:8px 0 16px; font-size:13px; }
  th,td { border:1px solid #30363d; padding:6px 10px; text-align:left; vertical-align:top; }
  th { background:#161b22; color:#79c0ff; }
  tr:nth-child(even) td { background:#161b22; }
  .bar { display:inline-block; height:14px; background:#30363d; border-radius:3px; vertical-align:middle; min-width:120px; position:relative; overflow:hidden; }
  .bar > i { position:absolute; left:0; top:0; bottom:0; background:linear-gradient(90deg,#3fb950,#56d364); }
  .pct { color:#7ee787; font-variant-numeric:tabular-nums; margin-left:6px; }
  .st-done { color:#3fb950; font-weight:600; }
  .st-in_progress { color:#d29922; font-weight:600; }
  .st-blocked { color:#f85149; font-weight:600; }
  .st-pending { color:#8b949e; }
  code { background:#161b22; padding:1px 4px; border-radius:3px; font-size:12px; }
  .grand td { background:#1f2937 !important; font-weight:700; color:#fff; }
  .legend { font-size:12px; color:#8b949e; margin:4px 0 12px; }
</style></head><body>
"""


def build_html(cats: list[dict], si: dict) -> str:
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    parts = [HTML_HEAD.replace("{title}", PROJECT_NAME),
             f"<h1>{PROJECT_NAME}</h1>",
             f'<div class="meta">自动生成 · {now}</div>',
             '<div class="legend">✅ done · 🟡 in_progress · 🚫 blocked · ⬜ pending</div>',
             '<h2>一览</h2>',
             '<table><thead><tr><th>类别</th><th>完成</th><th>进行中</th><th>阻塞</th><th>待办</th><th>总数</th><th>进度</th></tr></thead><tbody>']
    grand = {"done": 0, "in_progress": 0, "blocked": 0, "pending": 0, "total": 0}
    for c in cats:
        if not c["entries"]:
            continue
        cnt = {"done": 0, "in_progress": 0, "blocked": 0, "pending": 0}
        for e in c["entries"]:
            cnt[status_of(e["id"], c["key"], si)] += 1
        total = len(c["entries"])
        for k in cnt:
            grand[k] += cnt[k]
        grand["total"] += total
        pct = (cnt["done"] / total * 100) if total else 0
        parts.append(
            f"<tr><td>{c['label']}</td>"
            f"<td>{cnt['done']}</td><td>{cnt['in_progress']}</td>"
            f"<td>{cnt['blocked']}</td><td>{cnt['pending']}</td><td>{total}</td>"
            f'<td><span class="bar"><i style="width:{pct:.1f}%"></i></span><span class="pct">{pct:.0f}%</span></td></tr>'
        )
    pct = (grand["done"] / grand["total"] * 100) if grand["total"] else 0
    parts.append(
        f'<tr class="grand"><td>合计</td>'
        f"<td>{grand['done']}</td><td>{grand['in_progress']}</td>"
        f"<td>{grand['blocked']}</td><td>{grand['pending']}</td><td>{grand['total']}</td>"
        f'<td><span class="bar"><i style="width:{pct:.1f}%"></i></span><span class="pct">{pct:.0f}%</span></td></tr>'
    )
    parts.append("</tbody></table>")

    parts.append("<h2>详细任务</h2>")
    for c in cats:
        if not c["entries"]:
            continue
        parts.append(f"<h3>{c['label']} <code>({c['key']})</code></h3>")
        if c.get("doc"):
            parts.append(f'<div class="doc">{c["doc"]}</div>')
        if c.get("depends_on"):
            parts.append(f'<div class="deps">依赖：{", ".join(c["depends_on"])}</div>')
        parts.append('<table><thead><tr><th>ID</th><th>状态</th><th>摘要</th><th>输出 / 备注</th></tr></thead><tbody>')
        for e in c["entries"]:
            rec = si.get(f"{c['key']}/{e['id']}") or si.get(f"{c['key']}_{e['id']}") or {}
            st = rec.get("status", "pending")
            summary = e.get("summary", "")
            note = rec.get("notes", "")
            outs = rec.get("outputs", [])
            out_str = ", ".join(outs[:2]) + (f" (+{len(outs) - 2})" if len(outs) > 2 else "")
            cell_extra = f" — {note}" if note else ""
            parts.append(
                f'<tr><td><code>{c["key"]}/{e["id"]}</code></td>'
                f'<td class="st-{st}">{emoji(st)} {st}</td>'
                f'<td>{summary}</td><td>{out_str}{cell_extra}</td></tr>'
            )
        parts.append("</tbody></table>")

    parts.append("<h2>多会话调用</h2>")
    parts.append('<p>在新会话里说 <code>执行 dispatch &lt;category&gt;/&lt;id&gt;</code> 即可。</p>')
    parts.append('<p>用法 → <a href="README.md">README.md</a> · 踩坑 → <a href="pitfalls.md">pitfalls.md</a></p>')
    parts.append("</body></html>\n")
    return "".join(parts)


def main() -> None:
    cats = load_categories()
    si = load_status()
    md = build_md(cats, si)
    html = build_html(cats, si)
    MD_OUT.write_text(md, encoding="utf-8")
    HTML_OUT.write_text(html, encoding="utf-8")
    n_done = sum(
        1 for c in cats for e in c["entries"]
        if status_of(e["id"], c["key"], si) == "done"
    )
    n_total = sum(len(c["entries"]) for c in cats)
    print(f"wrote MASTER_PROGRESS.md  ({len(md)} chars)")
    print(f"wrote MASTER_PROGRESS.html  ({len(html)} chars)")
    print(f"  {len(cats)} categories · {n_total} entries · {n_done} done")


if __name__ == "__main__":
    main()

---
name: dispatch-board
description: Bootstrap a multi-session parallel task coordination board for any project — splits big homogeneous work into N atomic dispatches, lets M parallel Claude Code sessions claim/work/complete each independently, auto-aggregates progress into MASTER_PROGRESS.md + .html dashboard, captures shared pitfalls. Use when user says 「搭一个任务板」「做个 dispatch board」「弄个进度面板让多会话推进」「把这个大任务切成多个分派书让多会话同时推」「task dashboard」「fanout 任务」「一键多会话」「dispatch board 复用」or similar. Solves the gap GSD has for ≥10 homogeneous independent units (data extraction batches, batch translation, batch PR reviews, batch OCR jobs) where each unit needs full session context. **Reference live instance**: JLPTsimu project (JLPTsimu v1 — 11 categories × 167 entries, in active production).
---

# Dispatch Board — 多会话并行任务协调系统

把**大批同质独立任务**（数据提取、批量翻译、N 个 PR review、N 个 OCR、教材分批抽取等）切成 N 个原子 dispatch，让 M 个 Claude Code 会话各自独立跑，进度自动汇总到 dashboard。

源于 JLPTsimu 的 N2/N3 真题 + 红蓝宝书 + 解析增强工程（2026-05-08 启用，11 类 × 167 entries 实测稳定）。

---

## 何时该用 dispatch-board（vs GSD / vs subagent）

| 场景 | 推荐 |
|---|---|
| 1-3 个独立任务，每个要规划 | GSD `gsd-plan-phase` + 普通执行 |
| 10+ 个**同质独立**任务（每个跑同一套 recipe，参数不同） | **dispatch-board** ← 本 skill |
| 10+ 个小任务，每个能 summary 回收（≤30k token） | `dispatching-parallel-agents` skill 的 subagent 波次 |
| 10+ 个**大**任务（PDF / 图片 / 需迭代调试） | **dispatch-board**（每会话独立 100k+ context） |
| 一次性 spike / 验证 | `gsd-spike` 或直接干 |

**经验法则**：每任务预计耗 ≥ 30k token 或需要看图迭代 → 用 dispatch-board。否则 subagent 波次足够。

---

## 与 GSD 整合（不改 GSD 本体，只约定用法）

| 整合点 | 做法 |
|---|---|
| **A. GSD phase 内嵌 dispatch-board** | 当 phase 含 ≥10 个同质单元，PLAN.md 只列 1 个 task：「在 `.planning/<phase-slug>/dispatch-board/` 建板 + 跑完所有 dispatch」；phase 的 verification 检查 `status/*.json` 数 = manifest.entries 数 |
| **B. fanout 模式选择** | gsd-execute-phase 的 subagent 波次适合短任务；dispatch-board 适合长任务（每会话独立完整 context） |
| **C. pitfalls 提升** | dispatch-board 跑完后，把 pitfalls.md 里反复触发的坑手动 promote 到 GSD `.planning/intel/` 给项目全局用 |

可以并存：项目用 GSD 管 phase 主线，遇到 fanout 工作就嵌入一块 dispatch-board。

---

## 文件结构（任何新项目都长这样）

```
<project>/<root>/                 ← 默认 root = "tasks/" 或 ".tasks/"，可改
├── README.md                     用户使用指南（用 assets 模板）
├── MASTER_PROGRESS.md            ⭐ 总览（dashboard.py 重生）
├── MASTER_PROGRESS.html          ⭐ 可视化（浏览器打开）
├── build_dashboard.py            扫 dispatches + status → 重生 MD/HTML
├── pitfalls.md                   踩坑积累（多会话 append-only）
├── status/                       每完成一个 dispatch 写一个 .json
│   └── .gitkeep
└── dispatches/
    ├── <category-1>/
    │   ├── TEMPLATE.md           该类别的标准操作
    │   └── manifest.json         该类别下所有原子 entry
    ├── <category-2>/
    │   ├── TEMPLATE.md
    │   └── manifest.json
    └── ...
```

---

## Bootstrap 一个新 dispatch-board（5 步）

### 1. 用 setup.sh 铺骨架

```bash
cd <project_root>
bash ~/.claude/skills/dispatch-board/assets/setup.sh tasks
# 第一个参数是 root 目录名（默认 tasks）
# 产出：tasks/{README.md, build_dashboard.py, pitfalls.md, status/.gitkeep, MASTER_PROGRESS.md}
```

### 2. 加 dispatch 类别

每个类别一个目录 + TEMPLATE.md + manifest.json：

```bash
mkdir -p tasks/dispatches/<category>
cp ~/.claude/skills/dispatch-board/assets/dispatch_TEMPLATE.md.template tasks/dispatches/<category>/TEMPLATE.md
cp ~/.claude/skills/dispatch-board/assets/manifest.json.template tasks/dispatches/<category>/manifest.json
# 编辑 TEMPLATE.md 填入该类别专属步骤
# 编辑 manifest.json 填 entries 列表
```

### 3. 跑首版 dashboard

```bash
cd tasks && python3 build_dashboard.py
# wrote MASTER_PROGRESS.md  (~10k chars)
# wrote MASTER_PROGRESS.html (~25k chars)
```

### 4. 用户在 N 个新会话里调用

每会话独立说：「执行 dispatch <category>/<id>」 → 触发对应 skill / 流程。

### 5. dispatch worker 完成后

每会话完成自己的 dispatch 后，写 `status/{category}_{id}.json` + 在**当前项目的 board root** 重跑 `build_dashboard.py` + `git pull --rebase && git push`。

执行前先 `pwd` 确认路径是本次任务的 `.../doc_jlptsimu/tasks/` 或用户指定 board root；frontmatter 里的 Reference live instance 只供参考，**不能**当作当前同步目标。

---

## manifest.json schema

```json
{
  "category": "<unique key, eg. 'n2_real'>",
  "label": "<display name, eg. '🔵 N2 真题'>",
  "order": 1,
  "skill": "<routing target skill name>",
  "doc": "<one-line purpose>",
  "depends_on": ["<category-X>", ...],
  "entries": [
    {
      "id": "001",
      "kind": "<spike|batch|single|listen_only|...>",
      "summary": "<short description for dashboard>",
      "<custom_fields_per_skill>": "..."
    }
  ]
}
```

`category` / `label` / `order` 是 dashboard 必需字段；其它由领域 skill 自定义。

---

## status/{task_id}.json schema

```json
{
  "task_id": "<category>/<id>",
  "status": "done | in_progress | blocked | pending",
  "completed_at": "<ISO 8601 with TZ>",
  "agent_session": "<conversation hint or empty>",
  "commit_sha": "<short hash>",
  "outputs": ["<path1>", "<path2>", ...],
  "stats": { "<custom>": "..." },
  "notes": "<exception, blockage reason, etc>",
  "pitfalls_added": ["pf-YYYY-MM-DD-N", ...]
}
```

dashboard 按 `task_id` 索引（也支持 `{category}_{id}.json` 文件名 fallback）。

---

## 多会话并行约定（**铁律**）

| 风险 | 解决 |
|---|---|
| `/tmp` 撞车 | 每会话用 `/tmp/<project>-{task_id}/`（如 `/tmp/jlpt-n2real-003`），**不要**用全局公用名 |
| `git push` race | push 前**永远** `git pull --rebase origin main`；冲突仅可能在 `MASTER_PROGRESS.*` → 重跑 `build_dashboard.py` 再 push |
| `status/` 撞车 | 文件名 `{category}_{id}.json` 唯一；**绝不**在同一台机器同 task_id 起两个会话 |
| 共享状态文件（如 `_progress.json`）撞车 | **不写**这种共享文件；每批写 `status/{...}.json`，dashboard 聚合 |
| 依赖未就绪就启 | manifest 顶层写 `depends_on`；worker 启动先 check `status/<dep>_*.json` 数量 |

---

## 三种常见 dispatch 模式（manifest entries 设计）

### 模式 A — chunked-data（同质批跑）

```
N2 真题 11 套 → 11 个 entry（id 001-011），每个 entry 跑同一套 recipe，参数 = 年/月/PDF 路径
```

**特征**：参数化好；entries 一次性写齐；可全 parallel。

### 模式 B — spike-then-batches（先探后批）

```
红宝书 N2 → entry 001 = spike（探明 content 页范围 + schema），entries 002+ = 按 spike 结果 update 起止页的批次
```

**特征**：001 完成前 002+ pending；spike worker 完成后 update manifest 自动激活后续。

### 模式 C — dump-then-fanout（先 dump 后 N 批）

```
N2 解析增强 → entry 001 = dump（产出 _input/batch_NNN.jsonl 列表）+ update manifest 追加 002+；entries 002+ = 每批 50 题写解析
```

**特征**：001 跑完 manifest 自动膨胀；002+ 全 parallel。

---

## 触发词

- 「搭一个任务板」/「做个 dispatch board」/「弄个进度面板」
- 「把这个大任务切成多个分派书让多会话同时推」
- 「dispatch board 复用」/「任务分派系统」
- 「fanout 任务」/「一键多会话」
- 现成 dispatch-board 项目里说「执行 dispatch X/Y」也走对应底层 skill（不是本 skill）

---

## 不适用

- 单个任务（直接干）
- 任务间有强顺序依赖（用 GSD phase）
- 一次性 spike（用 `gsd-spike`）
- 任务太小可 summary（用 `dispatching-parallel-agents` 的 subagent 波次）

---

## 已知坑（v1 → v2 演进总结）

1. **dashboard.py 不要硬编码 category 列表**：v1 在 JLPTsimu 用 `CATEGORY_ORDER + LABEL` dict，加新类别要改 Python。本 skill assets 的 v2 改自动扫 manifest 的 `category/label/order` 字段。
2. **manifest entries 必须有稳定 `id`**：不要用数组 index 当 id，新增 entry 不能改原 entry 的 id（status 文件名靠它）。
3. **dashboard 不能 commit 编辑过的 MD/HTML**：只由 build_dashboard.py 重生，否则多会话 race 时 merge 不掉。
4. **status JSON 不要写共享 `_progress.json`**：每会话自己一个文件。
5. **pitfalls.md append-only**：多会话 race 时 append 顺序可能乱，但内容都在；不要 Edit 已有条目。
6. **不要把参考实现路径当当前 board**：skill 里的 JLPTsimu v1 路径只是 sample；每次完成 dispatch 都要在当前 repo 的 board root 跑 `build_dashboard.py`，并用 `MASTER_PROGRESS.md/.html` 时间戳 + 类别计数核对浏览器打开的是同一份。

---

## Bootstrap 资产（assets/）

- `build_dashboard.py` — 通用 dashboard 生成器（自动发现 categories）
- `README.md.template` — 项目根 README 模板
- `pitfalls.md.template` — 踩坑文件模板
- `dispatch_TEMPLATE.md.template` — 单类 dispatch TEMPLATE.md 模板
- `manifest.json.template` — manifest schema 模板
- `setup.sh` — 一键铺骨架脚本

---

## 参考实现（已在生产）

- **JLPTsimu v1**：`<your-project>/doc/tasks/`
  - 11 categories × 167 entries
  - Skills routed: `jlpt-extractor` / `jlpt-book-extractor` / `jlpt-task-dispatcher`
  - 启用日：2026-05-08
  - 验证：多会话已发现 8+ 新坑写入 pitfalls.md，证明并发写不撞

未来项目（MangaRe 资源批跑、bilibili 课程批转录、批量 PR review 等）首选用本 skill bootstrap。

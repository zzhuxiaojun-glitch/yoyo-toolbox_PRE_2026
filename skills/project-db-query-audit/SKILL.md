---
name: project-db-query-audit
description: End-to-end project database query optimization workflow — from static audit → dispatch board → EXPLAIN ANALYZE baseline → atomic fixes → audit errata. Use when user says 「数据库查询优化」「db perf audit」「数据库审计」「DB 查询效率检查」「查 N+1」「优化 Supabase 查询」 or asks to systematically improve database performance in an existing project. Provides a 7-step SOP, dispatch-board entry templates, the 5 most common static-audit-vs-reality mismatches, and concrete refactor patterns (count strategies, RPC for aggregation, PostgREST embed joins, client-side LRU). Complements `supabase-postgres-best-practices` (general PG rules) with project-level **process**.
license: MIT
metadata:
  author: zzhuxiaojun (derived from JLPTsimu db_optim 9-entry sweep, 2026-05-24)
  version: "1.0.0"
  related_skills:
    - supabase-postgres-best-practices
    - dispatch-board
    - verification-before-completion
---

# Project DB Query Audit — Workflow Skill

> When to apply: a working project has N+ files touching the DB and the user wants a *systematic* perf pass (not a one-off fix).
> Lineage: this skill captures the live workflow used on JLPTsimu (Next.js 16 + Supabase) for 9 atomic perf fixes + 1 spike, delivered in a single session.

---

## 0. Triggers

Activate when user says any of:
- 数据库查询优化 / db perf audit / 数据库审计 / DB 查询效率检查
- 查 N+1 / 优化 Supabase 查询 / Postgres 慢查询排查
- 「检查项目有没有数据库查询臃肿、缓慢、不合理的地方」
- 「帮我做一次 DB 性能审计」

Skip when:
- Single isolated query fix → just fix it (no workflow overhead)
- Schema design from scratch → use general PG best practices instead
- ORM-specific deep tuning (Prisma / Drizzle / TypeORM) → use ORM-specific skill if exists

---

## 1. The 7-Step SOP

```
1. AUDIT  →  Static scan, classify findings 🔴/🟠/🟡, list "ignored looks-like-problems"
              → audit.md (TOP 5 priorities + "DON'T TOUCH" list)
2. PLAN   →  Slice into independent atomic entries (1 PR / 1 commit each)
              → dispatch board: TEMPLATE.md + manifest.json
3. SPIKE  →  Run EXPLAIN ANALYZE BUFFERS for all 🔴/🟠 paths BEFORE coding
              → baseline.md (plan + ms + buffers per query)
              → EXPECT to find audit mistakes here
4. FIX    →  Apply each entry: tsc + lint per commit
              → DON'T scope creep (new findings → follow-up entry, not this entry)
5. MIGRATION → If RPC/index: explicit "must apply before merge" warning
              → Stage migrations separately so deploy team can apply first
6. ERRATA →  Update audit.md with reality-corrections from §3
              → Capture mismatches in pitfalls.md or this skill's references/
7. PR     →  One PR per branch, bundle status JSONs, Chinese title/body if project uses CN
```

Each step has a section below.

---

## 2. Step 1 — Static Audit (~1-2 hour)

### 2.1 Scan patterns
Use `grep` from project root:
```bash
# Over-fetching
grep -rn "select('\\*')\\|select(\"\\*\")" src --include="*.ts" --include="*.tsx"

# Exact count (potentially slow on big tables)
grep -rn "count: 'exact'\\|count: \"exact\"" src --include="*.ts" --include="*.tsx"

# Suspicious sequential awaits
grep -rn "await.*supabase" src --include="*.ts" -A 3 | grep -B 1 "await.*supabase"

# Pagination loops
grep -rn "\\.range(0," src --include="*.ts"

# N+1 candidates (loop + await inside)
grep -rEn "for \\([^)]*\\) \\{$" src --include="*.ts" -A 5 | grep "await"

# All DB queries (to count touch points)
find src -type f \\( -name "*.ts" -o -name "*.tsx" \\) -exec grep -l "from('" {} +
```

### 2.2 Existing index map
```bash
# Catalog every CREATE INDEX in migrations
grep -rEn "^create index|^create unique index|unique \\(" supabase/migrations/*.sql > /tmp/index-map.txt
```
Walk through code WHERE clauses, mark which already hit an index, which don't.

### 2.3 audit.md structure (mandatory sections)
```markdown
# Audit Report — YYYY-MM-DD

## TOP 5 priority list (cost/benefit ranked)
## §0 Background assumptions (table sizes, user count, growth model)
## §1 Existing indexes (verbatim from migrations)
## §2 🔴 Severe (audit thinks will hit hard)
## §3 🟠 Moderate (worth fixing but not on fire)
## §4 🟡 Minor / observational
## §5 Excluded: "looks like a problem but isn't" (PREVENTS RE-FILING)
## §6 Recommended follow-ups by category
```

**Critical: §5 must exist.** It prevents the next reviewer from "discovering" things you intentionally chose not to fix.

---

## 3. Step 2 — Dispatch Board (entries)

If project already has `tasks/dispatches/` (via `dispatch-board` skill): add a new category like `db_optim/`.
If not: scaffold a minimal one (see `references/dispatch-template.md`).

### 3.1 Entry sizing rule
**One entry = one commit = one logical fix.** If you can't summarize the change in 1 sentence, split.

Examples of well-sized entries:
- ✅ "`admin/page.tsx` 3 counts: exact → estimated"
- ✅ "`weakness.ts` aggregation pushed to SQL RPC"
- ❌ "rewrite all admin queries" (split into per-page entries)
- ❌ "add caching everywhere" (split into LRU + memoization + ISR per route)

### 3.2 Each entry needs
- `severity` 🔴/🟠/🟡
- `scope` bullet list (what files change, what behavior preserved)
- `outputs` (file paths created/modified)
- `audit_section` cross-reference back to audit.md
- `depends_on` (most entries should be `[]` — independence is the point)

### 3.3 manifest.json template
See `references/manifest-template.json`.

---

## 4. Step 3 — EXPLAIN ANALYZE Spike (CRITICAL, don't skip)

This is the step most teams skip — **it's where audit gets corrected**.

### 4.1 Connect to dev DB
```bash
# Find connection string in env files
grep "SUPABASE_DB_URL\\|DATABASE_URL\\|POSTGRES_URL" .env.local | sed 's/=.*/=<...>/'

# Verify psql installed
which psql && psql --version
```

**Always ask user for explicit permission** before connecting (even dev DB has real test-user data).

### 4.2 First: table sizes
```sql
select c.relname, pg_size_pretty(pg_total_relation_size(c.oid)),
       c.reltuples::bigint as est_rows
from pg_class c join pg_namespace n on n.oid = c.relnamespace
where n.nspname='public' and c.relkind='r'
order by pg_total_relation_size(c.oid) desc;
```

**Watch for `reltuples = -1`** — table has never been ANALYZE'd. `count: 'estimated'` will return 0. Recommend `VACUUM ANALYZE` as zero-code follow-up.

### 4.3 Find worst-case test user
```sql
select user_id, count(*) as data_rows
from <fact_table> group by user_id order by 2 desc limit 5;
```

### 4.4 Run EXPLAIN ANALYZE BUFFERS for every 🔴/🟠 path
```sql
\\timing on
explain (analyze, buffers, timing) <query>;
```

For each, record:
- Total execution time (ms)
- Plan node types (Seq Scan / Index Scan / Index Only Scan / Nested Loop / Hash Join)
- **`Heap Fetches: N`** on Index Only Scan — if > 50% of rows, VACUUM is overdue
- `Buffers: shared hit=N read=N` — high `read` = cold cache, results vary across runs
- Rows estimated vs actual (>10x off = stats outdated)

### 4.5 Write baseline.md
Sections:
- §0 Snapshot (sizes, dev vs prod scale gap)
- §1 Per-query plan + timing
- §2 TOP 3 actual slowest vs audit predictions (this is where mismatches are exposed)
- §3 Follow-ups audit didn't catch
- §4 Re-run commands (for after-fix verification)

---

## 5. Step 4-5 — Fix + Migration

### 5.1 Per-entry commit message
```
perf(db)[+migration]: <one-line what> (db_optim/NNN)

<why, 2-3 lines>

See: doc_jlptsimu/audit.md §<ref>
```

### 5.2 Migration commits MUST include deployment warning
```
⚠️ DEPLOYMENT: must apply migration before merging to develop;
otherwise <user-facing breakage> when <feature> loads.
```

### 5.3 status JSON per entry
```json
{
  "task_id": "db_optim/NNN",
  "status": "done",
  "before": { "metric": "...", "value": ..., "evidence": "..." },
  "after":  { "metric": "...", "value": ..., "improvement_pct": ... },
  "verification": { "tsc": {...}, "lint": {...}, "manual": "..." },
  "notes": "deviations from manifest scope; audit errata; follow-ups"
}
```

### 5.4 Forbidden: scope creep
If you find a new issue while fixing entry N:
- Append to `pitfalls.md` (cross-session memory)
- Add a new manifest entry (`NNN+1`)
- **Don't** silently expand current entry — keeps PR review surface small

---

## 6. Step 6 — Audit Errata (DON'T SKIP)

Static audit predictions are wrong ~20-30% of the time. After spike, go back to audit.md and add an `Errata` section:
- Reality of TOP 3 (was X, audit said Y)
- Add/remove from §5 excluded list based on findings
- Adjust priorities for follow-ups

This makes the audit a living artifact, not a snapshot.

---

## 7. The 5 Most Common Audit-vs-Reality Mismatches

From the JLPTsimu sweep + general experience. Watch for these explicitly during spike:

### 7.1 "small table won't be slow" → wrong if VACUUM is overdue
Symptom: Index Only Scan with `Heap Fetches: <high>%`. Visibility map is stale, so PG can't trust the index alone and falls back to heap.
Fix: `VACUUM ANALYZE public.<table>` — instant. Then re-EXPLAIN; usually drops 10-100x.

### 7.2 `select('*')` is not always wasteful
Decision tree:
1. `grep -rn "<returnType>" src/` — find callsite
2. Look at the JSX / consumer code
3. **Type-declared but unread** = safe to narrow (e.g. RecommendationRecord doesn't even declare `prompt_input` → narrowing is pure win)
4. **Type-declared AND rendered** (e.g. EntryCard reads `details.{pitch, examples, ...}`) = leave alone

### 7.3 `count: 'exact'` is fine on small tables, but watch for hidden costs
- `<5K row tables` with simple WHERE: fine, < 1ms
- BUT: `count` with `ilike` chain (multi-field text search) re-scans the filter — can be 100ms+ even on small tables
- BUT: `count` on table with stale visibility map (see 7.1) — 500ms+ regardless of size
- Rule of thumb: in admin pages whose primary purpose is showing the number → estimated. In paginated user lists → exact.

### 7.4 The "missing index" already exists (you just didn't grep hard enough)
Symptom: audit says "needs index on (A, B, C)". Reality: `recommendations_signature_lookup_idx (user_id, weakness_signature, expires_at)` already covers it; you missed it because the index name didn't match the column names obviously.
Fix: before suggesting new indexes, `grep -rEn "create.*index" supabase/migrations/*.sql | grep <table_name>` and EXPLAIN to verify usage.

### 7.5 PostgREST JS client has fewer abilities than SQL
The audit might say "merge step 1 and 3 with `.in(comparison_id, subquery)`". **PostgREST's `in()` does NOT accept subqueries.** Real merge options:
- Embedded `!inner` join with filter: `.from('A').select('*, B!inner(...)').eq('B.x', val)`
- Custom PG RPC (write SQL, expose as function)
Never assume PostgREST supports a SQL feature without checking docs.

---

## 8. Concrete Refactor Pattern Library

### 8.1 N round-trips → 1 RPC (count aggregations)
```sql
-- Bad: 5 supabase JS calls
-- Good: single RPC using count(*) filter
create or replace function public.get_user_stats(p_user_id uuid)
returns table (added int, due int, learning int, known int)
language sql stable security invoker
set search_path = public
as $$
  select
    count(*)::int as added,
    count(*) filter (where status = 'learning' and next_review_at <= now())::int as due,
    count(*) filter (where status = 'learning')::int as learning,
    count(*) filter (where status = 'known')::int as known
  from public.<table> where user_id = p_user_id;
$$;
grant execute on function public.get_user_stats(uuid) to authenticated;
```

### 8.2 JS group-by → SQL group-by with `dim_kind` discriminator
```sql
-- Multi-dimension aggregation in one RPC via union all
returns table (dim_kind text, dim_key text, attempts int, ...)
...
  select 'total'::text, null::text, count(*)::int, ... from raw
  union all select 'section'::text, section, count(*)::int, ... from raw group by section
  union all select 'tag'::text, tag, ... from raw, unnest(tags) as tag group by tag;
```
JS side: switch on `dim_kind`, build separate lists.

### 8.3 PostgREST embed `!inner` join (merge 2 queries → 1)
```ts
// Old: query A, then query B by A's ids
// New: query A with inner-joined B as filter
.from('grammar_comparisons')
.select('*, comparison_entry_links!inner(entry_id)')
.eq('comparison_entry_links.entry_id', entryId)
```
**Caveat**: same row in A may duplicate due to multiple B rows matching. Dedupe in JS:
```ts
Array.from(new Map(rows.map(r => [r.id, r])).values())
```

### 8.4 Client-side LRU cache for hot read APIs
```ts
// src/lib/<feature>/lookup-cache.ts
const MAX = 100;
const TTL_MS = 30 * 60 * 1000;
const cache = new Map<string, { result: unknown; expiresAt: number }>();

export function getCached<T>(key: string): T | null {
  const e = cache.get(key);
  if (!e || Date.now() > e.expiresAt) { cache.delete(key); return null; }
  cache.delete(key); cache.set(key, e); // LRU touch
  return e.result as T;
}
export function setCached<T>(key: string, result: T): void {
  if (cache.size >= MAX) {
    const k = cache.keys().next().value;
    if (k !== undefined) cache.delete(k);
  }
  cache.set(key, { result, expiresAt: Date.now() + TTL_MS });
}
```
**React caveat**: querying cache + setting state inside `useEffect` triggers lint warning ("effect 内同步 setState 触发级联渲染"). Move to `useState`'s lazy initializer instead. Parent must use `key={…}` to remount per input change.

### 8.5 `Promise.all` for independent queries (the trivial win)
Look for sequences of `await supabase.from(...)` where the second doesn't depend on the first's result. Often 5-minute change, -1 RTT each.

Wrap in `.catch(() => fallback)` inline to preserve "this query failure doesn't block the page" semantics when needed.

---

## 9. Anti-Patterns to Reject

- Adding a comment "TODO: optimize later" — either fix now or open follow-up entry
- "Refactor while we're here" — keep entries surgical, file other observations
- Skipping the spike because "the audit looks right" — audit is wrong 20-30% of the time
- Bundling migration with code in one branch without DEPLOYMENT note — will break first deploy
- Manual count synchronization (denormalized counter columns) — use estimated count or counter triggers, not handwritten
- Adding `select('estimated_count_view')` table — Postgres already has reltuples

---

## 10. Output Artifacts Checklist

When the workflow concludes, you should have:
- [ ] `audit.md` (with Errata section)
- [ ] `dispatches/db_optim/` with TEMPLATE.md + manifest.json + status/*.json
- [ ] `baseline.md` (entry_NNN_baseline.md)
- [ ] N atomic commits on a single feature branch
- [ ] 1 PR with bundled summary + per-migration deploy notes
- [ ] Updated `pitfalls.md` with any cross-session lessons
- [ ] Optional: a learning/onboarding md doc (for future devs)

---

## 11. References

- `references/manifest-template.json` — bootstrap a new db_optim category
- `references/audit-checklist.md` — printable scan checklist for §2
- `references/explain-query-cookbook.md` — psql commands for §4 spike
- Related skill: **`supabase-postgres-best-practices`** — Supabase official 30 rules (general PG advice; use alongside this workflow)
- Related skill: **`dispatch-board`** — how to scaffold the tasks/ board if project doesn't have one
- Related skill: **`verification-before-completion`** — never claim "done" without tsc + lint output

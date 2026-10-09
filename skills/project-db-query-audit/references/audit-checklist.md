# Static Audit Scan Checklist

Print this. Tick each box. Then write `audit.md`.

## A. Inventory
- [ ] `find src -type f \( -name "*.ts" -o -name "*.tsx" \) | xargs grep -l "from('" | wc -l` → count DB-touching files
- [ ] `grep -rEn "^create index|^create unique index|unique \(" supabase/migrations/*.sql > /tmp/index-map.txt`
- [ ] List every public table; for each, list every column referenced in a WHERE clause across `src/`

## B. Over-fetch
- [ ] `grep -rn "select('\*')" src/` — for each: find callsite, list fields actually read in JSX/JS
- [ ] Look for tables with large JSONB / text columns (`grep -i "jsonb\|text" supabase/migrations/*.sql | grep -v "^#"`); cross-ref with select '*'

## C. Counts
- [ ] `grep -rn "count: 'exact'" src/` — classify each:
  - `head: true` + no WHERE → likely candidate for `estimated`
  - With WHERE on user_id → fine (single-user scope)
  - For pagination total → keep `exact` (precision required)

## D. Sequential awaits
- [ ] Open every `route.ts` / `page.tsx` server component / server action
- [ ] Trace: if 2+ `await supabase.from(...)` chained AND second doesn't reference first's data → mark for `Promise.all`

## E. Loops with awaits (N+1 candidates)
- [ ] `for ... { await ... }` patterns
- [ ] `map(async)` returning supabase calls without batching
- [ ] `Promise.all(arr.map(id => supabase.from(...).eq('id', id)))` → check if `.in('id', arr)` works instead

## F. Missing indexes (heuristic)
- [ ] For each WHERE clause: trace columns; does an index covering leftmost prefix exist?
- [ ] Composite filter (`.eq().eq().eq()`): index should match column order
- [ ] `.overlaps('arr', [...])` or `.contains('json', ...)`: needs GIN index
- [ ] `.order(... desc).limit(N)`: index should be DESC on order column, or composite ending in `created_at DESC`

## G. RLS audit
- [ ] Every public table has `enable row level security`?
- [ ] Every table has at least one `policy ... for select` (or `for all`)?
- [ ] Explicit `eq('user_id', ...)` in code on RLS-protected tables → RLS wins anyway, but keep for index efficiency (note in §5 of audit.md)

## H. Range/pagination smells
- [ ] `.range(0, 9999)` or `.range(0, large)` — fake pagination
- [ ] `.range(0, PAGE - 1)` in a `for` loop — defensive pagination, usually fine but call out
- [ ] No `.limit()` on list selects → unbounded fetch

## I. PostgREST `select` smells
- [ ] `select('*, related_table(*)')` — nested * on related table is double trouble
- [ ] Deep nesting (`a(b(c(*)))`) — usually means a single RPC would be cleaner

## J. Done?
- [ ] TOP 5 priorities ranked
- [ ] §5 "looks like a problem but isn't" populated (prevents re-filing)
- [ ] Each finding has location (`file:line`), symptom, impact, suggested direction

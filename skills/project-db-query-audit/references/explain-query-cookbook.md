# EXPLAIN ANALYZE Cookbook (Supabase / Postgres)

Paste-and-go templates for §4 spike step.

## Setup

```bash
DB_URL=$(grep "^SUPABASE_DB_URL=" .env.local | sed 's/SUPABASE_DB_URL=//;s/^"//;s/"$//')
psql "$DB_URL"
```

```sql
\timing on
\pset format wrapped
```

## Recon — table sizes + index health

```sql
-- Sizes & estimated rows (look for reltuples = -1 → never ANALYZE'd)
select c.relname, pg_size_pretty(pg_total_relation_size(c.oid)),
       c.reltuples::bigint as est_rows
from pg_class c join pg_namespace n on n.oid=c.relnamespace
where n.nspname='public' and c.relkind='r'
order by pg_total_relation_size(c.oid) desc;

-- Indexes per table
select schemaname, tablename, indexname, indexdef
from pg_indexes where schemaname='public'
order by tablename, indexname;

-- Index usage stats (idx_scan = 0 → unused → consider dropping)
select relname as table, indexrelname as index, idx_scan, idx_tup_read, idx_tup_fetch
from pg_stat_user_indexes order by idx_scan;
```

## Find a high-volume test user

```sql
select user_id, count(*) as rows
from <fact_table> a [join <user_link_table> u on u.id=a.session_id]
group by user_id order by 2 desc limit 5;
```

## EXPLAIN query patterns

### Count queries
```sql
explain (analyze, buffers, timing) select count(*) from <table>;
explain (analyze, buffers, timing) select count(*) from <table> where <filter>;
```

Watch for:
- `Heap Fetches: N` on Index Only Scan — N > 30% of rows = VACUUM overdue
- Buffer hits vs reads — high reads = cold cache, run twice to compare

### Join with filter on far side
```sql
explain (analyze, buffers, timing)
select a.*, q.*
from public.<facts> a
inner join public.<sessions> s on s.id = a.session_id
inner join public.<dim> q on q.id = a.dim_id
where s.user_id = '<uuid>' and a.<filter>;
```

Watch for:
- `Memoize` on dim_id lookups — good, PG is reusing results
- `Nested Loop` with high outer rows + index scan inside — OK only if outer rows are small
- `Seq Scan on <large_table>` with high cost — missing index or query plan misjudgment

### List queries with text search
```sql
explain (analyze, buffers, timing)
select id, title from public.<table>
where (title ilike '%X%' or summary ilike '%X%')
order by created_at desc limit 30;
```

Watch for:
- Sequential Scan when you have trgm indexes — usually because the query has `or` chain with one field missing the trgm index
- `Rows Removed by Filter` — large number = index was wrong, filter did the real work

### RPC (post-migration)
```sql
explain (analyze, buffers, timing)
select * from public.<rpc_name>('<arg1>'::uuid, 'arg2');
```

## Before/After comparison protocol

1. Run query → save plan in `entry_NNN_explain_before.txt`
2. Apply migration / code fix
3. Re-run identical query → save plan in `entry_NNN_explain_after.txt`
4. `diff` the two; capture key delta in status JSON `before/after`:
   - Execution Time (ms)
   - Plan node summary (top 2-3 nodes)
   - Buffers shared hit/read

## Common red flags reference

| Symptom | Likely cause | Fix |
|---|---|---|
| `Seq Scan` on > 10K row table | Missing index for filter | Add index matching WHERE columns |
| `Index Only Scan` + `Heap Fetches: <high>` | Visibility map stale | `VACUUM ANALYZE <table>` |
| Estimated rows >> actual (or vice versa) | Stats outdated | `ANALYZE <table>` |
| `Sort` node before Limit, no Index Scan above | Order column not indexed | Add `(filter_cols, order_col DESC)` composite |
| `Filter: ...` removing many rows after Index Scan | Index covers only part of WHERE | Extend composite OR add covering index |
| `Hash Join` with very large `Hash`  | Join order suboptimal | Often: reorder WHERE / use CTE / write RPC |
| `BitmapOr` with multiple indexes | OR query splitting | Sometimes a partial / expression index helps |

## When EXPLAIN says "fine" but app is slow

The query may not be the bottleneck. Check:
- Connection pool exhaustion (Supabase: pooler vs direct)
- N+1 at app layer (PG sees N fast queries, app sees N latencies)
- JSON serialization cost (large `select *` with big JSONB)
- Network RTT (especially edge functions hitting far-away DB)

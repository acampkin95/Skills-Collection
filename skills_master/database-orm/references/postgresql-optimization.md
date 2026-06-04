# PostgreSQL Optimization

## Reading EXPLAIN ANALYZE

### Running EXPLAIN

```sql
-- Always use ANALYZE + BUFFERS for real execution data
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.name, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON p.author_id = u.id
WHERE u.active = true
GROUP BY u.id
ORDER BY post_count DESC
LIMIT 10;
```

### Understanding Output

```
Limit  (cost=150.23..150.25 rows=10 width=40) (actual time=2.345..2.350 rows=10 loops=1)
  ->  Sort  (cost=150.23..152.73 rows=1000 width=40) (actual time=2.340..2.345 rows=10 loops=1)
        Sort Key: (count(p.id)) DESC
        Sort Method: top-N heapsort  Memory: 25kB
        ->  HashAggregate  (cost=120.00..130.00 rows=1000 width=40) (actual time=1.800..2.100 rows=1000 loops=1)
              ->  Hash Left Join  (cost=30.00..95.00 rows=5000 width=36) (actual time=0.500..1.200 rows=5000 loops=1)
                    Hash Cond: (u.id = p.author_id)
                    ->  Seq Scan on users u  (cost=0.00..25.00 rows=1000 width=36) (actual time=0.010..0.200 rows=1000 loops=1)
                          Filter: (active = true)
                          Rows Removed by Filter: 200
                    ->  Hash  (cost=20.00..20.00 rows=5000 width=16) (actual time=0.400..0.400 rows=5000 loops=1)
                          Buckets: 8192  Batches: 1  Memory Usage: 300kB
                          ->  Seq Scan on posts p  (cost=0.00..20.00 rows=5000 width=16) (actual time=0.005..0.200 rows=5000 loops=1)
Planning Time: 0.150 ms
Execution Time: 2.500 ms
```

### Key Metrics

| Metric | Meaning | Watch For |
|--------|---------|-----------|
| `cost` | Estimated startup..total cost | High total cost |
| `actual time` | Real startup..total time (ms) | Large gap from estimate |
| `rows` | Estimated vs actual | estimate >> actual = stale stats |
| `loops` | Times node executed | High loops in nested loops |
| `Buffers: shared hit` | Cache hits | Good - data in memory |
| `Buffers: shared read` | Disk reads | Bad if high - need more RAM |

### Red Flags

| Pattern | Problem | Fix |
|---------|---------|-----|
| `Seq Scan` on large table | Missing index | Add appropriate index |
| `Nested Loop` with high rows | Cartesian-like join | Check join conditions, add indexes |
| `Sort` with `external merge Disk` | Sort spills to disk | Increase `work_mem` or add index |
| `Hash` with many batches | Hash doesn't fit memory | Increase `work_mem` |
| Estimated rows far from actual | Stale statistics | Run `ANALYZE table_name` |
| `Filter: Rows Removed` is high | Scanning too many rows | Add partial index or refine query |

---

## Index Types

### B-tree (Default)

Best for: equality (`=`), range (`<`, `>`, `BETWEEN`), sorting, `LIKE 'prefix%'`

```sql
-- Simple
CREATE INDEX idx_users_email ON users (email);

-- Composite (leftmost prefix rule applies)
CREATE INDEX idx_orders_user_date ON orders (user_id, created_at DESC);
-- Supports: WHERE user_id = X
-- Supports: WHERE user_id = X AND created_at > Y
-- Does NOT support: WHERE created_at > Y (without user_id)

-- Covering index (index-only scans)
CREATE INDEX idx_users_email_name ON users (email) INCLUDE (name);
```

### GIN (Generalized Inverted Index)

Best for: JSONB containment, array overlap, full-text search

```sql
-- JSONB
CREATE INDEX idx_products_metadata ON products USING GIN (metadata);
-- Supports: WHERE metadata @> '{"color": "red"}'
-- Supports: WHERE metadata ? 'color'
-- Supports: WHERE metadata ?& array['color', 'size']

-- Array
CREATE INDEX idx_posts_tags ON posts USING GIN (tags);
-- Supports: WHERE tags @> ARRAY['typescript']
-- Supports: WHERE tags && ARRAY['typescript', 'react']

-- Full-text search
CREATE INDEX idx_posts_search ON posts USING GIN (to_tsvector('english', title || ' ' || content));
-- Supports: WHERE to_tsvector('english', title || ' ' || content) @@ to_tsquery('typescript & react')
```

### GiST (Generalized Search Tree)

Best for: geometric data, range types, full-text (alternative to GIN)

```sql
-- Range types (scheduling, availability)
CREATE INDEX idx_events_during ON events USING GIST (during);
-- Supports: WHERE during && '[2025-01-01, 2025-02-01)'

-- PostGIS geography
CREATE INDEX idx_locations_coords ON locations USING GIST (coordinates);
```

### BRIN (Block Range Index)

Best for: naturally ordered data (timestamps), very large tables

```sql
-- Excellent for time-series data (orders by date, logs)
CREATE INDEX idx_logs_timestamp ON logs USING BRIN (created_at);
-- Much smaller than B-tree, ideal for append-only tables
```

### Partial Indexes

Index only the rows you actually query:

```sql
-- Only index active users (saves space and write overhead)
CREATE INDEX idx_active_users ON users (email) WHERE deleted_at IS NULL;

-- Only index unpaid orders
CREATE INDEX idx_unpaid_orders ON orders (user_id, created_at)
WHERE status = 'pending' AND paid_at IS NULL;

-- Only index published posts
CREATE UNIQUE INDEX idx_published_slugs ON posts (slug) WHERE published = true;
```

### Index Guidelines

| Rule | Explanation |
|------|-------------|
| Index all foreign keys | PostgreSQL does NOT auto-index FKs |
| Composite index column order | Most selective column first, or match query WHERE order |
| Don't over-index | Each index slows INSERT/UPDATE/DELETE |
| Use partial indexes | When queries consistently filter on a condition |
| Monitor unused indexes | `pg_stat_user_indexes` shows usage |
| INCLUDE for covering | Avoids table lookups for common SELECT columns |

---

## Query Optimization Patterns

### Pagination

```sql
-- BAD: OFFSET-based (scans all skipped rows)
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 10000;

-- GOOD: Cursor-based (keyset pagination)
SELECT * FROM posts
WHERE created_at < $1  -- cursor from previous page
ORDER BY created_at DESC
LIMIT 20;

-- With composite cursor for stable ordering
SELECT * FROM posts
WHERE (created_at, id) < ($1, $2)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

### Avoiding SELECT *

```sql
-- BAD: fetches all columns including large text/jsonb
SELECT * FROM posts;

-- GOOD: fetch only needed columns
SELECT id, title, slug, created_at FROM posts;
```

### EXISTS vs IN

```sql
-- Prefer EXISTS for correlated subqueries (short-circuits)
SELECT * FROM users u
WHERE EXISTS (
  SELECT 1 FROM posts p WHERE p.author_id = u.id AND p.published = true
);

-- IN is fine for small value lists
SELECT * FROM users WHERE id IN ('uuid1', 'uuid2', 'uuid3');
```

### Batch Operations

```sql
-- BAD: individual inserts in a loop
INSERT INTO logs (message) VALUES ('log 1');
INSERT INTO logs (message) VALUES ('log 2');

-- GOOD: batch insert
INSERT INTO logs (message) VALUES ('log 1'), ('log 2'), ('log 3');

-- GOOD: COPY for bulk loading
COPY logs (message) FROM STDIN WITH (FORMAT csv);
```

---

## Maintenance

### VACUUM and ANALYZE

```sql
-- Update statistics for query planner
ANALYZE users;
ANALYZE posts;

-- Reclaim dead tuple space
VACUUM users;

-- Full vacuum (locks table, reclaims disk space)
VACUUM FULL users;  -- Use sparingly in production

-- Check dead tuples
SELECT relname, n_dead_tup, n_live_tup,
       round(n_dead_tup::numeric / NULLIF(n_live_tup, 0) * 100, 2) as dead_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

### Autovacuum Tuning

```sql
-- For high-write tables, make autovacuum more aggressive
ALTER TABLE orders SET (
  autovacuum_vacuum_scale_factor = 0.05,    -- default 0.2
  autovacuum_analyze_scale_factor = 0.02,   -- default 0.1
  autovacuum_vacuum_cost_delay = 10         -- default 2ms
);
```

### pg_stat_statements

```sql
-- Enable in postgresql.conf
-- shared_preload_libraries = 'pg_stat_statements'

-- Find slowest queries
SELECT query,
       calls,
       round(total_exec_time::numeric, 2) as total_ms,
       round(mean_exec_time::numeric, 2) as avg_ms,
       rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Find most called queries
SELECT query, calls, round(mean_exec_time::numeric, 2) as avg_ms
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 20;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

### Monitoring Index Usage

```sql
-- Find unused indexes (candidates for removal)
SELECT schemaname, relname, indexrelname, idx_scan, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Find missing indexes (sequential scans on large tables)
SELECT relname, seq_scan, seq_tup_read, idx_scan,
       round(seq_scan::numeric / NULLIF(seq_scan + idx_scan, 0) * 100, 2) as seq_pct
FROM pg_stat_user_tables
WHERE seq_scan > 100
ORDER BY seq_tup_read DESC;
```

---

## Connection Pooling Configuration

### PgBouncer

```ini
; pgbouncer.ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

; Pool settings
pool_mode = transaction          ; transaction | session | statement
default_pool_size = 20
max_client_conn = 200
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3

; Timeouts
server_idle_timeout = 600
client_idle_timeout = 0
query_timeout = 30
```

**Pool modes:**

| Mode | Use Case | Limitation |
|------|----------|------------|
| `transaction` | Most apps, serverless | No prepared statements, no session-level SET |
| `session` | Apps needing session state | One server per client connection |
| `statement` | Simple read-only queries | No transactions, no multi-statement |

### Recommended Settings by Environment

| Environment | Pool Mode | Pool Size | Max Clients |
|-------------|-----------|-----------|-------------|
| Serverless (Vercel/Lambda) | transaction | 10-20 | 200 |
| Small app server | transaction | 10-20 | 100 |
| Large app server | transaction | 50-100 | 500 |
| Connection-heavy (many microservices) | transaction | 20 per service | 1000 |

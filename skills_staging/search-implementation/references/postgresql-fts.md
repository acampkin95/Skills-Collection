# PostgreSQL Full-Text Search Reference

## Core Concepts

PostgreSQL FTS converts text into **tsvector** (searchable tokens) and matches against **tsquery** (search expressions).

```sql
-- Basic FTS query
SELECT title, ts_rank(search_vector, query) AS rank
FROM products, to_tsquery('english', 'wireless & headphones') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 20;
```

## tsvector and tsquery

### tsvector — Indexed Document Representation

```sql
-- Convert text to tsvector
SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog');
-- Result: 'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2

-- Concatenate multiple fields with weights
SELECT
  setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
  setweight(to_tsvector('english', coalesce(brand, '')), 'B') ||
  setweight(to_tsvector('english', coalesce(description, '')), 'C')
FROM products;
-- Weights: A (highest) > B > C > D (lowest, default)
```

### tsquery — Search Expression

```sql
-- Simple term
SELECT to_tsquery('english', 'headphones');

-- AND (both terms must match)
SELECT to_tsquery('english', 'wireless & headphones');

-- OR (either term matches)
SELECT to_tsquery('english', 'wireless | wired');

-- NOT (exclude term)
SELECT to_tsquery('english', 'headphones & !wired');

-- Phrase match (adjacent words)
SELECT to_tsquery('english', 'noise <-> cancelling');

-- Proximity (within N words)
SELECT to_tsquery('english', 'noise <2> cancelling');

-- plainto_tsquery: simpler, auto-ANDs words
SELECT plainto_tsquery('english', 'wireless headphones');
-- Same as: to_tsquery('english', 'wireless & headphones')

-- phraseto_tsquery: phrase search
SELECT phraseto_tsquery('english', 'noise cancelling headphones');
-- Same as: to_tsquery('english', 'noise <-> cancelling <-> headphones')

-- websearch_to_tsquery: Google-like syntax (PG 11+)
SELECT websearch_to_tsquery('english', 'wireless headphones -wired "noise cancelling"');
-- Supports: AND (space), OR, - (NOT), "quotes" (phrase)
```

## Table Setup with Generated Column

### Method 1: Generated Column (Recommended, PG 12+)

```sql
CREATE TABLE products (
  id          SERIAL PRIMARY KEY,
  title       TEXT NOT NULL,
  brand       TEXT,
  description TEXT,
  price       NUMERIC(10,2),
  category    TEXT,
  tags        TEXT[],
  in_stock    BOOLEAN DEFAULT true,
  created_at  TIMESTAMPTZ DEFAULT now(),

  -- Generated search column: auto-updates when source columns change
  search_vector TSVECTOR GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(brand, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(array_to_string(tags, ' '), '')), 'B') ||
    setweight(to_tsvector('english', coalesce(description, '')), 'C')
  ) STORED
);

-- Create GIN index on the search column
CREATE INDEX idx_products_search ON products USING GIN (search_vector);
```

### Method 2: Trigger (PG < 12 or complex logic)

```sql
-- Add tsvector column
ALTER TABLE products ADD COLUMN search_vector TSVECTOR;

-- Create trigger function
CREATE OR REPLACE FUNCTION products_search_trigger() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.brand, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(NEW.description, '')), 'C');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
CREATE TRIGGER trg_products_search
  BEFORE INSERT OR UPDATE ON products
  FOR EACH ROW
  EXECUTE FUNCTION products_search_trigger();

-- Create GIN index
CREATE INDEX idx_products_search ON products USING GIN (search_vector);

-- Backfill existing rows
UPDATE products SET search_vector =
  setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
  setweight(to_tsvector('english', coalesce(brand, '')), 'B') ||
  setweight(to_tsvector('english', coalesce(description, '')), 'C');
```

## GIN Index

GIN (Generalized Inverted Index) is the standard index type for FTS:

```sql
-- Basic GIN index on tsvector column
CREATE INDEX idx_products_search ON products USING GIN (search_vector);

-- GIN index on expression (no stored column needed, but slower writes)
CREATE INDEX idx_products_search_expr ON products USING GIN (
  to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
);

-- Check index size
SELECT pg_size_pretty(pg_relation_size('idx_products_search'));
```

**When to use GIN vs GiST:**
- **GIN**: Faster reads, slower writes, larger index. Best for most FTS use cases.
- **GiST**: Faster writes, slower reads, smaller index. Best for rapidly changing data with fewer reads.

## Ranking

### ts_rank

```sql
-- Basic ranking
SELECT
  id, title,
  ts_rank(search_vector, query) AS rank
FROM products, websearch_to_tsquery('english', 'wireless headphones') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 20;

-- Weighted ranking (match weights A=1.0, B=0.4, C=0.2, D=0.1)
SELECT
  id, title,
  ts_rank('{0.1, 0.2, 0.4, 1.0}', search_vector, query) AS rank
FROM products, websearch_to_tsquery('english', 'wireless headphones') AS query
WHERE search_vector @@ query
ORDER BY rank DESC;

-- Normalize by document length (avoid long documents dominating)
SELECT
  id, title,
  ts_rank(search_vector, query, 32) AS rank  -- 32 = normalize by rank / (rank + 1)
FROM products, websearch_to_tsquery('english', 'wireless headphones') AS query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

### ts_rank_cd (Cover Density)

```sql
-- Considers proximity of matching terms (better for phrase-like relevance)
SELECT
  id, title,
  ts_rank_cd(search_vector, query) AS rank
FROM products, websearch_to_tsquery('english', 'noise cancelling headphones') AS query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

### Combined Ranking with Business Logic

```sql
SELECT
  id, title, price, rating,
  ts_rank(search_vector, query) * 0.7 +
  (rating / 5.0) * 0.2 +
  CASE WHEN in_stock THEN 0.1 ELSE 0 END AS combined_score
FROM products, websearch_to_tsquery('english', 'headphones') AS query
WHERE search_vector @@ query
ORDER BY combined_score DESC
LIMIT 20;
```

## Highlighting

```sql
SELECT
  id,
  ts_headline(
    'english',
    description,
    websearch_to_tsquery('english', 'wireless headphones'),
    'StartSel=<mark>, StopSel=</mark>, MaxWords=35, MinWords=15, MaxFragments=2'
  ) AS highlighted_description
FROM products
WHERE search_vector @@ websearch_to_tsquery('english', 'wireless headphones')
ORDER BY ts_rank(search_vector, websearch_to_tsquery('english', 'wireless headphones')) DESC
LIMIT 20;

-- ts_headline options:
-- StartSel / StopSel: highlight wrapper tags
-- MaxWords: max words in each fragment
-- MinWords: min words in each fragment
-- MaxFragments: number of fragments (0 = use whole document)
-- FragmentDelimiter: string between fragments (default " ... ")
```

## Trigram Similarity (pg_trgm)

Trigrams enable fuzzy matching — essential for typo tolerance.

```sql
-- Enable the extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create trigram index for fuzzy matching
CREATE INDEX idx_products_title_trgm ON products USING GIN (title gin_trgm_ops);
CREATE INDEX idx_products_brand_trgm ON products USING GIN (brand gin_trgm_ops);

-- Similarity search (0-1 scale, 1 = exact match)
SELECT title, similarity(title, 'wireles headfones') AS sim
FROM products
WHERE title % 'wireles headfones'  -- % operator uses default threshold (0.3)
ORDER BY sim DESC
LIMIT 10;

-- Adjust similarity threshold
SET pg_trgm.similarity_threshold = 0.2;  -- More permissive (catches more typos)

-- Word similarity (matches if ANY word is similar)
SELECT title, word_similarity('headfones', title) AS wsim
FROM products
WHERE 'headfones' <% title  -- word similarity operator
ORDER BY wsim DESC;

-- LIKE/ILIKE with trigram index acceleration
SELECT * FROM products
WHERE title ILIKE '%headphone%';  -- Uses trigram index!
```

## Combined FTS + Trigram Search

Best of both worlds: full-text search with fuzzy fallback.

```sql
-- Search function with FTS primary, trigram fallback
CREATE OR REPLACE FUNCTION search_products(search_query TEXT, result_limit INT DEFAULT 20)
RETURNS TABLE(id INT, title TEXT, brand TEXT, price NUMERIC, rank FLOAT) AS $$
BEGIN
  -- Try FTS first
  RETURN QUERY
  SELECT p.id, p.title, p.brand, p.price,
    ts_rank(p.search_vector, websearch_to_tsquery('english', search_query))::FLOAT AS rank
  FROM products p
  WHERE p.search_vector @@ websearch_to_tsquery('english', search_query)
  ORDER BY rank DESC
  LIMIT result_limit;

  -- If no FTS results, fallback to trigram
  IF NOT FOUND THEN
    RETURN QUERY
    SELECT p.id, p.title, p.brand, p.price,
      similarity(p.title, search_query)::FLOAT AS rank
    FROM products p
    WHERE p.title % search_query OR p.brand % search_query
    ORDER BY rank DESC
    LIMIT result_limit;
  END IF;
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT * FROM search_products('wireles headfones');
```

## Faceted Search (Manual)

PostgreSQL doesn't have built-in facets, but you can compute them:

```sql
-- Get facet counts alongside search results
WITH search_results AS (
  SELECT *
  FROM products
  WHERE search_vector @@ websearch_to_tsquery('english', 'headphones')
)
SELECT 'category' AS facet, category AS value, COUNT(*) AS count
FROM search_results GROUP BY category
UNION ALL
SELECT 'brand', brand, COUNT(*)
FROM search_results GROUP BY brand
UNION ALL
SELECT 'in_stock', in_stock::TEXT, COUNT(*)
FROM search_results GROUP BY in_stock
ORDER BY facet, count DESC;
```

## Prisma Integration

```typescript
// prisma/schema.prisma — no native tsvector support, use raw SQL

// Search with Prisma raw query
async function searchProducts(query: string, limit = 20) {
  return prisma.$queryRaw<Product[]>`
    SELECT id, title, brand, price, description,
      ts_rank(search_vector, websearch_to_tsquery('english', ${query})) AS rank
    FROM products
    WHERE search_vector @@ websearch_to_tsquery('english', ${query})
    ORDER BY rank DESC
    LIMIT ${limit}
  `;
}

// Search with highlighting
async function searchWithHighlights(query: string) {
  return prisma.$queryRaw`
    SELECT id, title, price,
      ts_headline('english', description,
        websearch_to_tsquery('english', ${query}),
        'StartSel=<mark>, StopSel=</mark>, MaxFragments=2'
      ) AS highlighted_description,
      ts_rank(search_vector, websearch_to_tsquery('english', ${query})) AS rank
    FROM products
    WHERE search_vector @@ websearch_to_tsquery('english', ${query})
    ORDER BY rank DESC
    LIMIT 20
  `;
}
```

## Drizzle ORM Integration

```typescript
import { sql } from 'drizzle-orm';
import { pgTable, serial, text, numeric, boolean, index, customType } from 'drizzle-orm/pg-core';

// Custom tsvector type
const tsvector = customType<{ data: string }>({
  dataType() { return 'tsvector'; },
});

export const products = pgTable('products', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  brand: text('brand'),
  description: text('description'),
  price: numeric('price', { precision: 10, scale: 2 }),
  searchVector: tsvector('search_vector'),
}, (table) => ({
  searchIdx: index('idx_products_search').using('gin', table.searchVector),
}));

// Search query
const results = await db.execute(sql`
  SELECT id, title, price,
    ts_rank(search_vector, websearch_to_tsquery('english', ${query})) as rank
  FROM products
  WHERE search_vector @@ websearch_to_tsquery('english', ${query})
  ORDER BY rank DESC
  LIMIT 20
`);
```

## Custom Dictionaries and Configurations

```sql
-- Create a custom text search configuration based on English
CREATE TEXT SEARCH CONFIGURATION product_search (COPY = english);

-- Add synonym dictionary
CREATE TEXT SEARCH DICTIONARY product_synonyms (
  TEMPLATE = synonym,
  SYNONYMS = product_syn  -- references $SHAREDIR/tsearch_data/product_syn.syn
);

-- Use the synonym dictionary in your configuration
ALTER TEXT SEARCH CONFIGURATION product_search
  ALTER MAPPING FOR asciiword WITH product_synonyms, english_stem;

-- Use custom config in queries
SELECT to_tsvector('product_search', 'smartphone accessories');
```

## Performance Tips

```sql
-- Check query plan to confirm index usage
EXPLAIN ANALYZE
SELECT * FROM products
WHERE search_vector @@ websearch_to_tsquery('english', 'headphones')
ORDER BY ts_rank(search_vector, websearch_to_tsquery('english', 'headphones')) DESC
LIMIT 20;

-- Partial index: only index active products
CREATE INDEX idx_active_products_search ON products USING GIN (search_vector)
WHERE in_stock = true;

-- Covering index with INCLUDE (PG 12+)
-- (Not applicable to GIN — use alongside B-tree indexes for filters)

-- VACUUM and ANALYZE regularly for FTS performance
VACUUM ANALYZE products;
```

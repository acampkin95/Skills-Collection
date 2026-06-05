---
name: search-implementation
description: Search engine architecture and full-text search implementation.
---

# Search Implementation Architecture

Use this skill for **choosing and implementing search engines**. Covers architecture patterns, indexing strategies, relevance tuning, faceted search, autocomplete, and user experience considerations.

## Engine Selection Matrix

| Engine | Latency | Setup | Cost | Full-Text | Faceting | Typo Tolerance | Real-Time | Best For |
|--------|---------|-------|------|-----------|----------|-----------------|-----------|----------|
| **Meilisearch** | 50ms | Easy | Free/Self | Excellent | Yes | Yes | Yes | Content search, UX-first |
| **Algolia** | 10ms | Trivial | $$$$ | Excellent | Yes | Yes | Yes | E-commerce, production |
| **Typesense** | 50ms | Moderate | $/Self | Excellent | Yes | Yes | Yes | Balanced option |
| **PostgreSQL FTS** | 500ms | Built-in | $ | Good | Limited | No | Yes | Simple, existing DB |
| **Elasticsearch** | 100ms | Complex | $/Self | Excellent | Yes | Yes | Eventual | Large scale |
| **Solr** | 100ms | Complex | Free/Self | Excellent | Yes | Yes | Eventual | Enterprise |

---

## Indexing Strategy

### Incremental Indexing

```typescript
// Sync database changes to search index
async function syncProductsToIndex(since: Date) {
  const products = await db.product.findMany({
    where: { updatedAt: { gte: since } }
  });

  const records = products.map(p => ({
    objectID: p.id,
    name: p.name,
    description: p.description,
    price: p.price,
    category: p.category,
    inStock: p.quantity > 0,
    rating: p.rating,
    updatedAt: p.updatedAt.getTime()
  }));

  await searchClient.index('products').saveObjects(records);
}

// Run periodically or on webhook
setInterval(() => syncProductsToIndex(new Date(Date.now() - 5000)), 5000);
```

### Bulk Reindexing

```typescript
async function reindexAll() {
  const allProducts = await db.product.findMany();
  const index = searchClient.index('products');

  // Clear existing
  await index.clearObjects();

  // Batch insert (most engines prefer batch API)
  const BATCH_SIZE = 1000;
  for (let i = 0; i < allProducts.length; i += BATCH_SIZE) {
    const batch = allProducts.slice(i, i + BATCH_SIZE).map(p => ({
      objectID: p.id,
      name: p.name,
      // ... other fields
    }));
    await index.saveObjects(batch);
  }
}
```

---

## Relevance Tuning

### Ranking Factors

```typescript
// Meilisearch example
const settings = {
  rankingRules: [
    'words',           // Exact word match
    'typo',            // Typo tolerance
    'proximity',       // Words close together
    'attribute',       // Which field matched
    'sort',            // Sort parameter
    'exactness',       // Exact matches prioritized
    'recency:desc',    // Newer first
    'popularity:desc', // By rating/views
  ],
  sortableAttributes: ['price', 'rating', 'createdAt'],
  filterableAttributes: ['category', 'inStock', 'brand'],
};

await client.index('products').updateSettings(settings);
```

### Custom Scoring

```typescript
// Boost high-rated products
const query = 'laptop';
const results = await searchClient.search('products', {
  q: query,
  facets: ['category'],
  customRanking: [
    'desc(rating)',           // Higher rating = higher rank
    'desc(popularity)',       // Popular first
    'asc(price)',            // Lower price = slight boost
  ],
  attributesToHighlight: ['name', 'description'],
});
```

---

## Faceted Search

### Facet Configuration

```typescript
interface SearchFilters {
  category?: string[];
  priceRange?: [number, number];
  inStock?: boolean;
  rating?: number;
  brand?: string[];
}

async function facetedSearch(
  query: string,
  filters: SearchFilters,
  page: number = 1
) {
  const filterArray: string[] = [];

  if (filters.category?.length) {
    filterArray.push(`category IN [${filters.category.map(c => `"${c}"`).join(', ')}]`);
  }

  if (filters.priceRange) {
    filterArray.push(`price >= ${filters.priceRange[0]} AND price <= ${filters.priceRange[1]}`);
  }

  if (filters.inStock !== undefined) {
    filterArray.push(`inStock = ${filters.inStock}`);
  }

  if (filters.rating) {
    filterArray.push(`rating >= ${filters.rating}`);
  }

  return searchClient.index('products').search(query, {
    filters: filterArray.join(' AND '),
    facets: ['category', 'brand', 'price:0-50', 'price:50-200', 'price:200+'],
    page,
    hitsPerPage: 20,
  });
}
```

---

## Autocomplete

### Type-Ahead Implementation

```typescript
async function autocomplete(prefix: string, limit: number = 5) {
  // Option 1: Prefix search
  const results = await searchClient.index('products').search(prefix, {
    hitsPerPage: limit,
    attributesToRetrieve: ['id', 'name'],
  });

  // Option 2: Dedicated suggestions index
  const suggestions = await suggestionsIndex.search(prefix, {
    hitsPerPage: limit,
  });

  return results.hits.map(h => ({
    value: h.name,
    id: h.id,
  }));
}

// Debounce in UI
const [suggestions, setSuggestions] = useState<string[]>([]);
const [query, setQuery] = useState('');
const debounceTimer = useRef<NodeJS.Timeout>();

const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
  setQuery(e.target.value);

  clearTimeout(debounceTimer.current);
  debounceTimer.current = setTimeout(async () => {
    const results = await autocomplete(e.target.value);
    setSuggestions(results);
  }, 300);
};
```

---

## UX Patterns

### Search Results Page

```typescript
export default async function SearchPage({
  searchParams,
}: {
  searchParams: { q?: string; category?: string; page?: string };
}) {
  const query = searchParams.q || '';
  const page = parseInt(searchParams.page || '1', 10);

  const results = await facetedSearch(query, {
    category: searchParams.category ? [searchParams.category] : undefined,
  }, page);

  return (
    <div className="grid grid-cols-4">
      <aside>
        <Facets facets={results.facets} />
      </aside>
      <main className="col-span-3">
        <SearchHeader query={query} resultCount={results.nbHits} />
        <Results hits={results.hits} />
        <Pagination page={page} nbPages={results.nbPages} />
      </main>
    </div>
  );
}
```

### No Results Handling

```typescript
function SearchResults({ hits, query }: { hits: any[]; query: string }) {
  if (hits.length === 0) {
    return (
      <div className="text-center py-12">
        <h2>No results for "{query}"</h2>
        <ul className="mt-4 text-sm text-gray-600">
          <li>Try different keywords</li>
          <li>Check spelling</li>
          <li>Try more general terms</li>
        </ul>
      </div>
    );
  }

  return (
    <div>
      {hits.map(hit => (
        <ResultCard key={hit.objectID} hit={hit} />
      ))}
    </div>
  );
}
```

---

## Performance Optimization

### Caching Strategy

```typescript
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 60000; // 1 minute

async function cachedSearch(query: string, filters: any) {
  const cacheKey = JSON.stringify({ query, filters });
  const cached = cache.get(cacheKey);

  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }

  const results = await facetedSearch(query, filters);
  cache.set(cacheKey, { data: results, timestamp: Date.now() });
  return results;
}

// Cleanup old entries
setInterval(() => {
  const now = Date.now();
  for (const [key, value] of cache.entries()) {
    if (now - value.timestamp > CACHE_TTL * 2) {
      cache.delete(key);
    }
  }
}, CACHE_TTL);
```

### Lazy Loading

```typescript
// Load more results on scroll
const [results, setResults] = useState<any[]>([]);
const [page, setPage] = useState(1);
const observerTarget = useRef<HTMLDivElement>(null);

useEffect(() => {
  const observer = new IntersectionObserver(async (entries) => {
    if (entries[0].isIntersecting) {
      const nextPage = page + 1;
      const newResults = await search(query, { page: nextPage });
      setResults(r => [...r, ...newResults.hits]);
      setPage(nextPage);
    }
  });

  if (observerTarget.current) {
    observer.observe(observerTarget.current);
  }

  return () => observer.disconnect();
}, [page, query]);
```

---

## Monitoring

### Search Analytics

```typescript
// Track search queries
async function logSearch(query: string, resultCount: number, userId: string) {
  await db.searchLog.create({
    query,
    resultCount,
    userId,
    timestamp: new Date(),
  });
}

// Find popular searches
async function getPopularSearches(limit: number = 10) {
  const popular = await db.searchLog.groupBy({
    by: ['query'],
    _count: { id: true },
    orderBy: { _count: { id: 'desc' } },
    take: limit,
  });

  return popular;
}
```

---

## Resources

| Resource | Purpose |
|----------|---------|
| [Meilisearch Docs](https://docs.meilisearch.com) | Meilisearch guide |
| [Algolia Docs](https://www.algolia.com/doc/) | Algolia guide |
| [Typesense Docs](https://typesense.org/docs/) | Typesense guide |
| [PostgreSQL FTS](https://www.postgresql.org/docs/current/textsearch.html) | PostgreSQL full-text search |

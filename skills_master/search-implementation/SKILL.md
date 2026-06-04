---
name: search-implementation
description: Full-text search with Algolia, Meilisearch, Typesense, Elasticsearch, or PostgreSQL FTS. Use for indexing, typo tolerance, faceted search, and relevance tuning.
version: 2.0.0
reviewed: "2026-06-04"
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


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.
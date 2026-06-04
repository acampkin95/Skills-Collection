# Meilisearch Reference

## Setup

### Docker (Recommended for Production)

```bash
# Run Meilisearch with persistence
docker run -d \
  --name meilisearch \
  -p 7700:7700 \
  -v $(pwd)/meili_data:/meili_data \
  -e MEILI_MASTER_KEY='your-master-key-min-16-chars' \
  -e MEILI_ENV='production' \
  getmeili/meilisearch:v1.12

# Development (no auth)
docker run -d -p 7700:7700 getmeili/meilisearch:v1.12
```

### Docker Compose

```yaml
services:
  meilisearch:
    image: getmeili/meilisearch:v1.12
    ports:
      - "7700:7700"
    environment:
      MEILI_MASTER_KEY: "your-master-key-min-16-chars"
      MEILI_ENV: "production"
      MEILI_DB_PATH: "/meili_data"
      MEILI_HTTP_PAYLOAD_SIZE_LIMIT: "100MB"
    volumes:
      - meili_data:/meili_data
    restart: unless-stopped

volumes:
  meili_data:
```

### Client Setup (JavaScript/TypeScript)

```bash
npm install meilisearch
```

```typescript
import { MeiliSearch } from 'meilisearch';

// Server-side: use admin key
const adminClient = new MeiliSearch({
  host: 'http://localhost:7700',
  apiKey: process.env.MEILI_MASTER_KEY,
});

// Client-side: use search-only key
const searchClient = new MeiliSearch({
  host: 'http://localhost:7700',
  apiKey: process.env.NEXT_PUBLIC_MEILI_SEARCH_KEY,
});
```

## Indexing

### Add Documents

```typescript
const index = adminClient.index('products');

// Add or replace documents (primary key auto-detected or specified)
const task = await index.addDocuments([
  {
    id: 1,
    title: 'Wireless Headphones',
    description: 'Noise-cancelling Bluetooth headphones',
    price: 79.99,
    brand: 'AudioTech',
    categoryName: 'Electronics',
    tags: ['wireless', 'bluetooth', 'noise-cancelling'],
    rating: 4.5,
    inStock: true,
    imageUrl: '/images/headphones.jpg',
  },
  // ... more documents
], { primaryKey: 'id' });

// addDocuments is async — wait for task to complete
await adminClient.waitForTask(task.taskUid);
```

### Update Documents (Partial)

```typescript
// Only updates specified fields, keeps the rest
await index.updateDocuments([
  { id: 1, price: 69.99, inStock: false },
]);
```

### Delete Documents

```typescript
// Delete by ID
await index.deleteDocument(1);

// Delete multiple by ID
await index.deleteDocuments([1, 2, 3]);

// Delete by filter
await index.deleteDocuments({
  filter: 'inStock = false AND rating < 2',
});

// Delete all documents in index
await index.deleteAllDocuments();
```

### Batch Indexing

```typescript
async function batchIndex(documents: any[], batchSize = 1000) {
  const index = adminClient.index('products');
  const tasks: number[] = [];

  for (let i = 0; i < documents.length; i += batchSize) {
    const batch = documents.slice(i, i + batchSize);
    const task = await index.addDocuments(batch);
    tasks.push(task.taskUid);
  }

  // Wait for all batches to complete
  for (const taskUid of tasks) {
    const task = await adminClient.waitForTask(taskUid);
    if (task.status === 'failed') {
      console.error(`Task ${taskUid} failed:`, task.error);
    }
  }
}
```

## Index Settings

### Searchable Attributes (field priority)

```typescript
// Order defines search priority (first = highest)
await index.updateSearchableAttributes([
  'title',        // Matches here rank highest
  'brand',
  'tags',
  'categoryName',
  'description',  // Matches here rank lowest
]);
```

### Filterable Attributes

```typescript
// MUST configure before using in filter/facets
await index.updateFilterableAttributes([
  'categoryName',
  'brand',
  'price',
  'rating',
  'inStock',
  'tags',
  'createdAt',
]);
```

### Sortable Attributes

```typescript
await index.updateSortableAttributes([
  'price',
  'rating',
  'createdAt',
]);
```

### Displayed Attributes

```typescript
// Only return these fields in search results (reduces payload)
await index.updateDisplayedAttributes([
  'id', 'title', 'description', 'price', 'brand',
  'imageUrl', 'rating', 'inStock', 'categoryName',
]);
```

### All Settings at Once

```typescript
await index.updateSettings({
  searchableAttributes: ['title', 'brand', 'tags', 'description'],
  filterableAttributes: ['categoryName', 'brand', 'price', 'rating', 'inStock'],
  sortableAttributes: ['price', 'rating', 'createdAt'],
  displayedAttributes: ['id', 'title', 'price', 'brand', 'imageUrl', 'rating'],
  rankingRules: ['words', 'typo', 'proximity', 'attribute', 'sort', 'exactness'],
  stopWords: ['the', 'a', 'an', 'is', 'at', 'to', 'for', 'of'],
  synonyms: {
    phone: ['mobile', 'smartphone', 'cell'],
    laptop: ['notebook', 'computer'],
  },
  typoTolerance: {
    enabled: true,
    minWordSizeForTypos: { oneTypo: 4, twoTypos: 8 },
    disableOnAttributes: ['brand'], // Exact match for brand names
  },
  pagination: { maxTotalHits: 10000 },
  faceting: { maxValuesPerFacet: 200 },
});
```

## Search Queries

### Basic Search

```typescript
const results = await index.search('wireless headphones');
// results = {
//   hits: [...],
//   query: 'wireless headphones',
//   processingTimeMs: 2,
//   estimatedTotalHits: 42,
// }
```

### Search with Parameters

```typescript
const results = await index.search('headphones', {
  limit: 20,               // Results per page
  offset: 0,               // Pagination offset
  attributesToRetrieve: ['id', 'title', 'price', 'imageUrl'],
  attributesToHighlight: ['title', 'description'],
  attributesToCrop: ['description'],
  cropLength: 50,
  highlightPreTag: '<mark>',
  highlightPostTag: '</mark>',
  showMatchesPosition: true,
  showRankingScore: true,   // Debug relevance
});

// Highlighted results in hits[n]._formatted
// results.hits[0]._formatted.title = "Wireless <mark>Headphones</mark>"
```

### Filtering

```typescript
// Single filter
const results = await index.search('', {
  filter: 'inStock = true',
});

// Multiple conditions (AND)
const results = await index.search('headphones', {
  filter: 'price >= 20 AND price <= 100 AND inStock = true',
});

// OR conditions
const results = await index.search('headphones', {
  filter: 'brand = "AudioTech" OR brand = "SoundMax"',
});

// Array contains (tags)
const results = await index.search('', {
  filter: 'tags = "wireless"',
});

// Combine with parentheses
const results = await index.search('headphones', {
  filter: '(brand = "AudioTech" OR brand = "SoundMax") AND price < 100',
});

// NOT
const results = await index.search('headphones', {
  filter: 'brand != "CheapBrand" AND NOT tags = "wired"',
});

// Filter array syntax (each string is ANDed, items within are ORed)
const results = await index.search('headphones', {
  filter: [
    ['brand = "AudioTech"', 'brand = "SoundMax"'],  // OR
    'price < 100',                                     // AND
    'inStock = true',                                  // AND
  ],
});
```

### Sorting

```typescript
const results = await index.search('headphones', {
  sort: ['price:asc'],
});

const results = await index.search('headphones', {
  sort: ['rating:desc', 'price:asc'],
});
```

### Faceted Search

```typescript
const results = await index.search('headphones', {
  facets: ['categoryName', 'brand', 'tags'],
  filter: 'price >= 20 AND price <= 100',
});

// results.facetDistribution:
// {
//   categoryName: { "Electronics": 42, "Accessories": 15 },
//   brand: { "AudioTech": 20, "SoundMax": 18 },
//   tags: { "wireless": 35, "bluetooth": 30 },
// }
//
// results.facetStats (for numeric facets):
// { price: { min: 20, max: 99.99 } }
```

## Geo Search

```typescript
// Documents must have _geo field
await index.addDocuments([
  { id: 1, name: 'Store A', _geo: { lat: 40.7128, lng: -74.0060 } },
  { id: 2, name: 'Store B', _geo: { lat: 34.0522, lng: -118.2437 } },
]);

// Configure _geo as filterable and sortable
await index.updateFilterableAttributes(['_geo']);
await index.updateSortableAttributes(['_geo']);

// Filter by radius (meters)
const results = await index.search('', {
  filter: '_geoRadius(40.7128, -74.0060, 5000)', // 5km radius
});

// Filter by bounding box
const results = await index.search('', {
  filter: '_geoBoundingBox([40.82, -73.95], [40.68, -74.02])',
});

// Sort by distance
const results = await index.search('coffee shop', {
  sort: ['_geoPoint(40.7128, -74.0060):asc'],
});
// Each hit includes _geoDistance (meters from point)
```

## Multi-Search

```typescript
// Search across multiple indexes in one HTTP request
const results = await adminClient.multiSearch({
  queries: [
    {
      indexUid: 'products',
      q: 'wireless',
      limit: 5,
      attributesToRetrieve: ['id', 'title', 'price'],
    },
    {
      indexUid: 'articles',
      q: 'wireless',
      limit: 3,
      attributesToRetrieve: ['id', 'title', 'excerpt'],
    },
    {
      indexUid: 'brands',
      q: 'wireless',
      limit: 3,
    },
  ],
});

// results.results[0].hits → products
// results.results[1].hits → articles
// results.results[2].hits → brands
```

## Synonyms

```typescript
// One-way synonyms
await index.updateSynonyms({
  phone: ['mobile', 'smartphone', 'cell', 'cellphone'],
  laptop: ['notebook', 'portable computer'],
  tv: ['television', 'telly', 'flat screen'],
  cheap: ['affordable', 'budget', 'inexpensive'],
});
// Searching "phone" also matches "mobile", "smartphone", etc.
// But searching "mobile" does NOT match "phone" unless you add reverse mapping

// Two-way: add both directions
await index.updateSynonyms({
  phone: ['mobile'],
  mobile: ['phone'],
});
```

## Typo Tolerance

```typescript
await index.updateTypoTolerance({
  enabled: true,
  minWordSizeForTypos: {
    oneTypo: 4,   // Words with 4+ chars allow 1 typo
    twoTypos: 8,  // Words with 8+ chars allow 2 typos
  },
  disableOnWords: ['iphone', 'sql'],  // Exact match only
  disableOnAttributes: ['sku', 'isbn'], // No typos on codes
});
```

## API Keys and Security

```typescript
// Create a search-only key (safe for frontend)
const searchKey = await adminClient.createKey({
  description: 'Frontend search key',
  actions: ['search'],
  indexes: ['products', 'articles'],
  expiresAt: null, // Never expires
});

// Create an admin key for indexing (server-side only)
const adminKey = await adminClient.createKey({
  description: 'Indexing key',
  actions: ['documents.add', 'documents.delete', 'settings.update'],
  indexes: ['products'],
  expiresAt: null,
});

// Tenant tokens for multi-tenant search
const tenantToken = adminClient.generateTenantToken(
  searchKey.uid, // Must be the UID, not the key itself
  {
    products: {
      filter: `tenantId = ${currentTenantId}`,
    },
  },
  {
    expiresAt: new Date(Date.now() + 3600 * 1000), // 1 hour
  }
);
```

## Task Management

All write operations are asynchronous. Track status:

```typescript
const task = await index.addDocuments(documents);

// Poll for completion
const completed = await adminClient.waitForTask(task.taskUid, {
  timeOutMs: 30000,
  intervalMs: 500,
});

if (completed.status === 'succeeded') {
  console.log(`Indexed ${completed.details.indexedDocuments} documents`);
} else if (completed.status === 'failed') {
  console.error('Indexing failed:', completed.error);
}

// List recent tasks
const tasks = await adminClient.getTasks({
  statuses: ['failed'],
  limit: 10,
});
```

## Production Deployment

### Environment Variables

```bash
MEILI_MASTER_KEY=your-secure-key-min-16-characters
MEILI_ENV=production          # Disables dashboard, requires API key
MEILI_DB_PATH=/meili_data     # Persistent storage path
MEILI_HTTP_PAYLOAD_SIZE_LIMIT=100MB
MEILI_MAX_INDEXING_MEMORY=2Gb
MEILI_MAX_INDEXING_THREADS=4
```

### Health Check

```typescript
const health = await adminClient.health();
// { status: 'available' }

const stats = await adminClient.getStats();
// { databaseSize: 12345678, indexes: { products: { numberOfDocuments: 5000 } } }

const version = await adminClient.getVersion();
```

### Backup and Snapshots

```bash
# Create a dump (portable backup)
curl -X POST 'http://localhost:7700/dumps' \
  -H 'Authorization: Bearer YOUR_MASTER_KEY'

# Snapshots (for disaster recovery)
# Enable via MEILI_SCHEDULE_SNAPSHOT=true
# Or: MEILI_SCHEDULE_SNAPSHOT="0 */6 * * *"  (every 6 hours)
```

### Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name search.example.com;

    location / {
        proxy_pass http://localhost:7700;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

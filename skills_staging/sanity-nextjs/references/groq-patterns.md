# Advanced GROQ Query Patterns

## Pagination

```groq
// Offset pagination
*[_type == "post"] | order(publishedAt desc)[$start...$end]

// Cursor-based (more efficient for large datasets)
*[_type == "post" && publishedAt < $lastDate] | order(publishedAt desc)[0...20]

// With total count for UI
{
  "items": *[_type == "post"] | order(publishedAt desc)[$start...$end],
  "total": count(*[_type == "post"])
}
```

## Aggregations

```groq
// Count by category
*[_type == "category"]{
  title,
  "postCount": count(*[_type == "post" && references(^._id)])
}

// Sum values
{
  "totalProducts": count(*[_type == "product"]),
  "totalValue": math::sum(*[_type == "product"].price),
  "averagePrice": math::avg(*[_type == "product"].price)
}

// Group by field
*[_type == "post"]{
  "year": string::split(publishedAt, "-")[0],
  title
}
```

## Joins and References

```groq
// Deep reference expansion
*[_type == "post"]{
  title,
  author->{
    name,
    organization->{name, logo}
  },
  "relatedPosts": *[_type == "post" && references(^.author._ref) && _id != ^._id][0...3]{
    title, slug
  }
}

// Reverse references (find all posts by author)
*[_type == "author" && slug.current == $slug][0]{
  name,
  "posts": *[_type == "post" && references(^._id)] | order(publishedAt desc)
}

// Multiple reference types
*[_type == "page"]{
  title,
  "linkedContent": *[references(^._id)]{
    _type,
    title,
    "slug": slug.current
  }
}
```

## Conditional Projections

```groq
// Type-based projections
*[_type in ["post", "page"]]{
  _type,
  title,
  _type == "post" => {
    author->,
    publishedAt,
    "category": categories[0]->title
  },
  _type == "page" => {
    sections,
    "sectionCount": count(sections)
  }
}

// Conditional field selection
*[_type == "product"]{
  title,
  price,
  "displayPrice": select(
    onSale == true => salePrice,
    price
  ),
  "badge": select(
    stock == 0 => "Out of Stock",
    stock < 5 => "Low Stock",
    "In Stock"
  )
}
```

## Array Operations

```groq
// Filter array items
*[_type == "page"]{
  "visibleSections": sections[visibility == true],
  "heroSection": sections[_type == "hero"][0]
}

// Map array items
*[_type == "gallery"]{
  "imageUrls": images[].asset->url,
  "imageDimensions": images[]{
    "width": asset->metadata.dimensions.width,
    "height": asset->metadata.dimensions.height
  }
}

// Array includes
*[_type == "post" && "featured" in tags]
*[_type == "post" && $category in categories[]->slug.current]

// Array length
*[_type == "post" && count(comments) > 10]

// Unique values
array::unique(*[_type == "post"].category)
```

## Text Search

```groq
// Basic match (prefix search)
*[_type == "post" && title match $query + "*"]

// Multi-field search
*[_type == "post" && (
  title match $query + "*" || 
  pt::text(body) match $query + "*" ||
  author->name match $query + "*"
)]

// Boost relevance with score
*[_type == "post"] | score(
  boost(title match $query + "*", 3),
  boost(pt::text(body) match $query + "*", 1),
  boost(excerpt match $query + "*", 2)
) | order(_score desc)[0...20]
```

## Date Operations

```groq
// Posts from last 30 days
*[_type == "post" && dateTime(publishedAt) > dateTime(now()) - 60*60*24*30]

// Date range
*[_type == "event" && 
  dateTime(startDate) >= dateTime($from) && 
  dateTime(startDate) <= dateTime($to)
]

// Future scheduled posts
*[_type == "post" && dateTime(publishedAt) > dateTime(now())]

// Format date parts
*[_type == "post"]{
  title,
  "year": string::split(publishedAt, "-")[0],
  "month": string::split(publishedAt, "-")[1]
}

// Current date/time
*[_type == "event" && endDate >= now()]
```

## Portable Text Queries

```groq
// Extract plain text
*[_type == "post"]{
  title,
  "excerpt": pt::text(body)[0...200] + "..."
}

// Find posts containing block type
*[_type == "post" && "image" in body[]._type]
*[_type == "post" && "code" in body[]._type]

// Extract all links
*[_type == "post"]{
  title,
  "links": body[].markDefs[_type == "link"].href
}

// Count images in body
*[_type == "post"]{
  title,
  "imageCount": count(body[_type == "image"])
}
```

## Geolocation

```groq
// Find within radius (requires geo index)
*[_type == "location" && geo::distance(location, geo::latLng($lat, $lng)) < $radius] 
  | order(geo::distance(location, geo::latLng($lat, $lng)))

// Distance calculation
*[_type == "store"]{
  name,
  "distance": geo::distance(location, geo::latLng($lat, $lng))
} | order(distance)
```

## Slugs and Paths

```groq
// Nested path construction
*[_type == "page"]{
  title,
  "path": "/" + coalesce(parent->slug.current + "/", "") + slug.current
}

// All slugs for static paths
*[_type == "post" && defined(slug.current)].slug.current

// Validate slug exists
count(*[_type == "post" && slug.current == $slug]) > 0
```

## Performance Patterns

```groq
// ✅ Use projections to limit data
*[_type == "post"][0...10]{
  _id,
  title,
  "slug": slug.current,
  "imageUrl": mainImage.asset->url
}

// ❌ Avoid deep chains in list queries
*[_type == "post"]{
  author->{organization->{team[]->{members[]->}}}
}

// ✅ Flatten or use separate queries
*[_type == "post"]{
  "authorName": author->name,
  "orgName": author->organization->name
}

// ✅ Use coalesce for fallbacks (not multiple queries)
*[_type == "post"]{
  "image": coalesce(mainImage, author->image, defaultImage)
}
```

## Debugging Queries

```groq
// Check document exists
count(*[_type == "post" && slug.current == $slug]) > 0

// Inspect full document
*[_type == "post"][0]

// Find documents missing fields
*[_type == "post" && !defined(mainImage)]

// Check reference integrity
*[_type == "post" && defined(author) && !defined(author->_id)]

// List all unique _types in dataset
array::unique(*[]._type)

// Check schema structure
*[_type == "post"][0]{
  "fields": keys(@)
}
```

## Common Gotchas

```groq
// ❌ Wrong: accessing undefined
*[_type == "post"]{slug: slug.current}

// ✅ Correct: filter first
*[_type == "post" && defined(slug.current)]{slug: slug.current}

// ❌ Wrong: reference without arrow
*[_type == "post"]{authorName: author.name}

// ✅ Correct: dereference with arrow
*[_type == "post"]{authorName: author->name}

// ❌ Wrong: comparing to array
*[_type == "post" && categories == $cat]

// ✅ Correct: use 'in' for arrays
*[_type == "post" && $cat in categories[]._ref]
```

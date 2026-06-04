#!/usr/bin/env tsx
/**
 * Batch URL Crawler for Tapestry
 * Processes multiple URLs from a file or list.
 */

interface CrawlOptions {
  urls: string[]
  outputDir?: string
  format?: 'markdown' | 'json' | 'html'
  maxConcurrency?: number
}

export async function batchCrawl(options: CrawlOptions) {
  const { urls, outputDir = './output', format = 'markdown', maxConcurrency = 5 } = options

  console.log(`Crawling ${urls.length} URLs with concurrency ${maxConcurrency}...`)

  // Implementation would use crawl4ai or similar
  // This is a template for the skill to reference

  for (const url of urls) {
    console.log(`  Processing: ${url}`)
    // await crawlUrl(url, { format, outputDir })
  }

  console.log(`Done! Output saved to ${outputDir}`)
}

export async function crawlFromFile(filePath: string, options: Omit<CrawlOptions, 'urls'>) {
  const { readFileSync } = await import('fs')
  const urls = readFileSync(filePath, 'utf-8')
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0 && !line.startsWith('#'))

  return batchCrawl({ ...options, urls })
}

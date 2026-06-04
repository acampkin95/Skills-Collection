#!/usr/bin/env tsx
/**
 * Clerk Setup Verification Script
 * Run this to check if Clerk is properly configured in your Next.js project.
 */

import { readFileSync, existsSync } from 'fs'
import { join } from 'path'

interface Check {
  name: string
  pass: boolean
  message: string
}

const checks: Check[] = []

// Check 1: Environment variables
console.log('Checking environment variables...')
const envExample = existsSync('.env.example') ? readFileSync('.env.example', 'utf-8') : ''
const envLocal = existsSync('.env.local') ? readFileSync('.env.local', 'utf-8') : ''

if (envLocal.includes('NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY')) {
  checks.push({ name: 'PUBLISHABLE_KEY', pass: true, message: 'Found in .env.local' })
} else {
  checks.push({ name: 'PUBLISHABLE_KEY', pass: false, message: 'Missing NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY' })
}

if (envLocal.includes('CLERK_SECRET_KEY') || envExample.includes('CLERK_SECRET_KEY')) {
  checks.push({ name: 'SECRET_KEY', pass: true, message: 'Found' })
} else {
  checks.push({ name: 'SECRET_KEY', pass: false, message: 'CLERK_SECRET_KEY not found' })
}

// Check 2: package.json dependencies
console.log('Checking dependencies...')
if (existsSync('package.json')) {
  const pkg = JSON.parse(readFileSync('package.json', 'utf-8'))
  const hasClerk = Object.keys(pkg.dependencies || {}).some(d => d.startsWith('@clerk/'))
  checks.push({
    name: 'Clerk SDK',
    pass: hasClerk,
    message: hasClerk ? 'Installed' : '@clerk/nextjs not in dependencies'
  })
} else {
  checks.push({ name: 'package.json', pass: false, message: 'Not found' })
}

// Check 3: Root layout
console.log('Checking root layout...')
const layoutPath = join('app', 'layout.tsx')
if (existsSync(layoutPath)) {
  const layout = readFileSync(layoutPath, 'utf-8')
  const hasClerkProvider = layout.includes('ClerkProvider')
  checks.push({
    name: 'ClerkProvider',
    pass: hasClerkProvider,
    message: hasClerkProvider ? 'Found in layout.tsx' : 'Missing ClerkProvider in layout.tsx'
  })
} else {
  checks.push({ name: 'layout.tsx', pass: false, message: 'Not found at app/layout.tsx' })
}

// Check 4: Middleware
console.log('Checking middleware...')
if (existsSync('middleware.ts') || existsSync('middleware.js')) {
  const middleware = readFileSync(existsSync('middleware.ts') ? 'middleware.ts' : 'middleware.js', 'utf-8')
  const hasAuthMiddleware = middleware.includes('authMiddleware')
  checks.push({
    name: 'authMiddleware',
    pass: hasAuthMiddleware,
    message: hasAuthMiddleware ? 'Found' : 'Missing authMiddleware in middleware'
  })
} else {
  checks.push({ name: 'middleware.ts', pass: false, message: 'Not found' })
}

// Print results
console.log('\n=== Clerk Setup Verification ===\n')
checks.forEach(check => {
  const status = check.pass ? '✓' : '✗'
  console.log(`${status} ${check.name}: ${check.message}`)
})

const passed = checks.filter(c => c.pass).length
const total = checks.length
console.log(`\n${passed}/${total} checks passed`)

if (passed < total) {
  console.log('\nTip: See https://clerk.com/docs/quickstarts/nextjs for setup instructions')
  process.exit(1)
}

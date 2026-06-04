# Translation Workflow & TMS Integration

## Message Extraction

### Script: Extract Messages from Code

Create a script to find all translation keys actually used in your codebase:

```ts
// scripts/extract-messages.ts
import { readFileSync, writeFileSync, readdirSync, statSync } from 'fs';
import { join } from 'path';

const KEY_PATTERNS = [
  /useTranslations\(['"](\w+)['"]\)/g,      // useTranslations('Namespace')
  /getTranslations\(['"](\w+)['"]\)/g,       // getTranslations('Namespace')
  /getTranslations\(\{[^}]*namespace:\s*['"](\w+)['"]/g,  // getTranslations({ namespace: 'X' })
  /t\(['"]([^'"]+)['"]/g                     // t('key') calls
];

function scanFile(filePath: string): string[] {
  const content = readFileSync(filePath, 'utf-8');
  const keys: string[] = [];

  for (const pattern of KEY_PATTERNS) {
    let match;
    const regex = new RegExp(pattern.source, pattern.flags);
    while ((match = regex.exec(content)) !== null) {
      keys.push(match[1]);
    }
  }
  return keys;
}

function walkDir(dir: string, ext: string[]): string[] {
  const files: string[] = [];
  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry);
    if (statSync(fullPath).isDirectory()) {
      if (!entry.startsWith('.') && entry !== 'node_modules') {
        files.push(...walkDir(fullPath, ext));
      }
    } else if (ext.some((e) => fullPath.endsWith(e))) {
      files.push(fullPath);
    }
  }
  return files;
}

// Run extraction
const files = walkDir('./src', ['.tsx', '.ts']);
const allKeys = files.flatMap(scanFile);
const uniqueKeys = [...new Set(allKeys)].sort();

console.log(`Found ${uniqueKeys.length} unique translation keys in ${files.length} files`);
writeFileSync('./extracted-keys.json', JSON.stringify(uniqueKeys, null, 2));
```

### Find Unused Translations

```ts
// scripts/find-unused.ts
import sourceKeys from './extracted-keys.json';
import messages from '../messages/en.json';

function flattenKeys(obj: Record<string, any>, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([key, value]) => {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    if (typeof value === 'object' && value !== null) {
      return flattenKeys(value, fullKey);
    }
    return [fullKey];
  });
}

const messageKeys = flattenKeys(messages);
const usedNamespaces = new Set(sourceKeys);

const unused = messageKeys.filter((key) => {
  const namespace = key.split('.')[0];
  // Keep if namespace is referenced (conservative check)
  return !usedNamespaces.has(namespace);
});

console.log(`Potentially unused translations (${unused.length}):`);
unused.forEach((k) => console.log(`  - ${k}`));
```

### package.json Scripts

```json
{
  "scripts": {
    "i18n:extract": "tsx scripts/extract-messages.ts",
    "i18n:unused": "tsx scripts/find-unused.ts",
    "i18n:check": "tsx scripts/check-missing.ts",
    "i18n:sync": "tsx scripts/sync-translations.ts"
  }
}
```

---

## Crowdin Integration

### Project Structure

```
crowdin.yml            # Crowdin configuration
messages/
├── en.json            # Source language (uploaded to Crowdin)
├── fr.json            # Downloaded from Crowdin
├── de.json
└── ar.json
```

### crowdin.yml

```yaml
# crowdin.yml
project_id_env: CROWDIN_PROJECT_ID
api_token_env: CROWDIN_API_TOKEN

preserve_hierarchy: true

files:
  - source: /messages/en.json
    translation: /messages/%two_letters_code%.json
    type: json

  # If using split files:
  # - source: /messages/en/*.json
  #   translation: /messages/%two_letters_code%/%original_file_name%
```

### CLI Commands

```bash
# Install Crowdin CLI
npm install -g @crowdin/cli

# Upload source strings
crowdin upload sources

# Download translations
crowdin download

# Check translation progress
crowdin status

# Pre-translate using Translation Memory + MT
crowdin pre-translate --method mt --engine-id 1
```

### CI/CD: GitHub Action

```yaml
# .github/workflows/crowdin-sync.yml
name: Crowdin Sync
on:
  push:
    branches: [main]
    paths: ['messages/en.json']

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Upload to Crowdin
        uses: crowdin/github-action@v2
        with:
          upload_sources: true
          download_translations: false
          crowdin_branch_name: main
        env:
          CROWDIN_PROJECT_ID: ${{ secrets.CROWDIN_PROJECT_ID }}
          CROWDIN_PERSONAL_TOKEN: ${{ secrets.CROWDIN_API_TOKEN }}

  download:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download from Crowdin
        uses: crowdin/github-action@v2
        with:
          upload_sources: false
          download_translations: true
          create_pull_request: true
          pull_request_title: 'chore(i18n): update translations'
          crowdin_branch_name: main
        env:
          CROWDIN_PROJECT_ID: ${{ secrets.CROWDIN_PROJECT_ID }}
          CROWDIN_PERSONAL_TOKEN: ${{ secrets.CROWDIN_API_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Lokalise Integration

### lokalise.yml

```yaml
# lokalise.yml (for @lokalise/cli)
project_id: "<PROJECT_ID>"
token: "<API_TOKEN>"

upload:
  file: messages/en.json
  lang_iso: en

download:
  type: json
  dest: messages/
  filename: "%lang_iso%.json"
  placeholder_format: icu
  export_empty_as: base  # Use English as fallback
```

### CLI Commands

```bash
# Install Lokalise CLI
npm install -g @lokalise/cli2

# Push source strings
lokalise2 file upload \
  --project-id $LOKALISE_PROJECT_ID \
  --token $LOKALISE_API_TOKEN \
  --file messages/en.json \
  --lang-iso en

# Pull all translations
lokalise2 file download \
  --project-id $LOKALISE_PROJECT_ID \
  --token $LOKALISE_API_TOKEN \
  --format json \
  --dest messages/ \
  --original-filenames=false \
  --export-empty-as base \
  --placeholder-format icu
```

---

## Translator Context

### Adding Context for Translators

Provide context comments in your source JSON using description keys:

```json
{
  "Auth": {
    "_description": "Authentication and login related strings",
    "login": "Log in",
    "login_description": "Button text on the main login form",
    "greeting": "Welcome back, {name}!",
    "greeting_description": "Shown on dashboard after login. {name} is the user's display name."
  }
}
```

### Screenshot Context

Most TMS platforms support screenshot uploads linked to keys:

```bash
# Crowdin: Upload screenshots with key mapping
crowdin screenshot upload ./screenshots/login-page.png \
  --auto-tag \
  --file-id 123

# Lokalise: Upload screenshot
lokalise2 screenshot create \
  --project-id $PROJECT_ID \
  --data '{"screenshot": "base64...", "key_ids": [456, 789]}'
```

### Character Limits

```json
{
  "Nav": {
    "home": "Home",
    "home_charlimit": "15",
    "notifications": "Notifications",
    "notifications_charlimit": "20"
  }
}
```

---

## Machine Translation QA

### Post-MT Quality Checks

```ts
// scripts/mt-qa.ts
import en from '../messages/en.json';
import fr from '../messages/fr.json';

interface QAIssue {
  key: string;
  type: string;
  detail: string;
}

function checkTranslation(
  sourceObj: Record<string, any>,
  targetObj: Record<string, any>,
  prefix = ''
): QAIssue[] {
  const issues: QAIssue[] = [];

  for (const [key, sourceVal] of Object.entries(sourceObj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    const targetVal = targetObj[key];

    if (typeof sourceVal === 'object') {
      if (typeof targetVal === 'object') {
        issues.push(...checkTranslation(sourceVal, targetVal, fullKey));
      } else if (targetVal === undefined) {
        issues.push({ key: fullKey, type: 'missing', detail: 'Key missing in target' });
      }
      continue;
    }

    if (targetVal === undefined) {
      issues.push({ key: fullKey, type: 'missing', detail: 'Key missing in target' });
      continue;
    }

    // Check ICU variable consistency
    const sourceVars = (sourceVal.match(/\{[^}]+\}/g) || []).sort();
    const targetVars = (targetVal.match(/\{[^}]+\}/g) || []).sort();
    if (JSON.stringify(sourceVars) !== JSON.stringify(targetVars)) {
      issues.push({
        key: fullKey,
        type: 'variable-mismatch',
        detail: `Source vars: ${sourceVars.join(', ')} | Target vars: ${targetVars.join(', ')}`
      });
    }

    // Check untranslated (identical to source)
    if (sourceVal === targetVal && sourceVal.length > 3) {
      issues.push({
        key: fullKey,
        type: 'untranslated',
        detail: `Identical to source: "${sourceVal}"`
      });
    }

    // Check length ratio (target shouldn't be >3x or <0.3x source)
    const ratio = targetVal.length / sourceVal.length;
    if (ratio > 3 || ratio < 0.3) {
      issues.push({
        key: fullKey,
        type: 'length-warning',
        detail: `Length ratio ${ratio.toFixed(1)}x (source: ${sourceVal.length}, target: ${targetVal.length})`
      });
    }
  }

  return issues;
}

const issues = checkTranslation(en, fr);
console.log(`QA Issues found: ${issues.length}`);
issues.forEach((i) => console.log(`  [${i.type}] ${i.key}: ${i.detail}`));
```

---

## Translation Memory & Glossaries

### Glossary File Format

Create a project glossary for consistent terminology:

```csv
# glossary.csv — import into Crowdin/Lokalise
term,description,translation_fr,translation_de,do_not_translate
Dashboard,Main user interface after login,Tableau de bord,Dashboard,false
API key,Authentication credential for API access,Cle API,API-Schlussel,false
Acme Corp,Company brand name,,,true
OAuth,Authentication protocol name,,,true
```

### Enforcing Glossary in CI

```ts
// scripts/check-glossary.ts
const glossary = [
  { term: 'Dashboard', translations: { fr: 'Tableau de bord', de: 'Dashboard' } },
  { term: 'Sign up', translations: { fr: "S'inscrire", de: 'Registrieren' } }
];

function checkGlossaryConsistency(locale: string, messages: Record<string, any>) {
  const flat = flattenValues(messages);
  const violations: string[] = [];

  for (const entry of glossary) {
    const expected = entry.translations[locale];
    if (!expected) continue;

    for (const [key, value] of Object.entries(flat)) {
      if (
        value.toLowerCase().includes(entry.term.toLowerCase()) &&
        !value.includes(expected)
      ) {
        violations.push(
          `${key}: Contains "${entry.term}" but expected translation "${expected}"`
        );
      }
    }
  }

  return violations;
}
```

---

## Sync Script: Check Missing Keys

```ts
// scripts/check-missing.ts
import { readdirSync, readFileSync } from 'fs';

const SOURCE_LOCALE = 'en';
const messagesDir = './messages';

function flattenKeys(obj: Record<string, any>, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([key, value]) => {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    return typeof value === 'object' && value !== null
      ? flattenKeys(value, fullKey)
      : [fullKey];
  });
}

const sourceFile = JSON.parse(
  readFileSync(`${messagesDir}/${SOURCE_LOCALE}.json`, 'utf-8')
);
const sourceKeys = new Set(flattenKeys(sourceFile));

const localeFiles = readdirSync(messagesDir)
  .filter((f) => f.endsWith('.json') && f !== `${SOURCE_LOCALE}.json`);

for (const file of localeFiles) {
  const locale = file.replace('.json', '');
  const targetFile = JSON.parse(readFileSync(`${messagesDir}/${file}`, 'utf-8'));
  const targetKeys = new Set(flattenKeys(targetFile));

  const missing = [...sourceKeys].filter((k) => !targetKeys.has(k));
  const extra = [...targetKeys].filter((k) => !sourceKeys.has(k));

  if (missing.length > 0) {
    console.log(`\n[${locale}] Missing ${missing.length} keys:`);
    missing.forEach((k) => console.log(`  + ${k}`));
  }
  if (extra.length > 0) {
    console.log(`\n[${locale}] Extra ${extra.length} keys (possibly stale):`);
    extra.forEach((k) => console.log(`  - ${k}`));
  }
  if (missing.length === 0 && extra.length === 0) {
    console.log(`[${locale}] All keys in sync`);
  }
}
```

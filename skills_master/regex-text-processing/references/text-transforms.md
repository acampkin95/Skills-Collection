# Text Transforms & Processing Recipes

## sed One-Liners

```bash
# Replace first occurrence per line
sed 's/old/new/' file.txt

# Replace all occurrences
sed 's/old/new/g' file.txt

# Case-insensitive replace
sed 's/old/new/gI' file.txt

# Delete lines matching pattern
sed '/pattern/d' file.txt

# Delete blank lines
sed '/^$/d' file.txt

# Print only matching lines (like grep)
sed -n '/pattern/p' file.txt

# Replace in-place (macOS needs backup extension)
sed -i '' 's/old/new/g' file.txt     # macOS
sed -i 's/old/new/g' file.txt        # Linux

# Insert line before match
sed '/pattern/i\New line before' file.txt

# Insert line after match
sed '/pattern/a\New line after' file.txt

# Replace between line numbers
sed '10,20s/old/new/g' file.txt

# Print line numbers of matches
sed -n '/pattern/=' file.txt

# Extract text between markers
sed -n '/START/,/END/p' file.txt

# Remove HTML tags
sed 's/<[^>]*>//g' file.html

# Add prefix to every line
sed 's/^/PREFIX: /' file.txt

# Remove trailing whitespace
sed 's/[[:space:]]*$//' file.txt
```

## awk Patterns

```bash
# Print specific columns
awk '{print $1, $3}' file.txt

# Custom delimiter
awk -F',' '{print $1, $2}' data.csv

# Filter rows
awk '$3 > 100 {print $0}' data.txt

# Sum a column
awk '{sum += $2} END {print sum}' data.txt

# Average
awk '{sum += $1; n++} END {print sum/n}' numbers.txt

# Count occurrences
awk '{count[$1]++} END {for (k in count) print k, count[k]}' access.log

# Print lines longer than N characters
awk 'length > 80' file.txt

# Print unique lines (like sort -u but preserves order)
awk '!seen[$0]++' file.txt

# Replace field value
awk -F',' 'BEGIN{OFS=","} {$3="REDACTED"; print}' data.csv

# Multiple conditions
awk '$1 == "ERROR" && $NF > 500 {print}' log.txt

# Format output
awk '{printf "%-20s %10.2f\n", $1, $2}' data.txt

# Process CSV with quoted fields
awk -v FPAT='[^,]*|"[^"]*"' '{print $1, $3}' data.csv
```

## jq for JSON

```bash
# Pretty print
echo '{"a":1}' | jq .

# Extract field
echo '{"name":"John","age":30}' | jq '.name'
# "John"

# Extract without quotes
echo '{"name":"John"}' | jq -r '.name'
# John

# Array access
echo '[1,2,3]' | jq '.[0]'
# 1

# Array map
echo '[{"n":"a"},{"n":"b"}]' | jq '.[].n'
# "a"
# "b"

# Filter array
echo '[1,2,3,4,5]' | jq '[.[] | select(. > 3)]'
# [4, 5]

# Object filter
echo '[{"name":"a","age":20},{"name":"b","age":30}]' | jq '[.[] | select(.age > 25)]'

# Transform
echo '{"first":"John","last":"Doe"}' | jq '{fullName: (.first + " " + .last)}'
# {"fullName": "John Doe"}

# Nested access
echo '{"a":{"b":{"c":1}}}' | jq '.a.b.c'

# Keys and values
echo '{"a":1,"b":2}' | jq 'keys'
# ["a", "b"]

# Length
echo '[1,2,3]' | jq 'length'
# 3

# Sort by field
echo '[{"n":"b","v":2},{"n":"a","v":1}]' | jq 'sort_by(.v)'

# Group by
echo '[{"t":"a","v":1},{"t":"a","v":2},{"t":"b","v":3}]' | jq 'group_by(.t)'

# Convert to CSV
echo '[{"a":1,"b":2},{"a":3,"b":4}]' | jq -r '.[] | [.a,.b] | @csv'
# 1,2
# 3,4

# Slurp multiple JSON objects
cat *.json | jq -s '.'
```

## JavaScript String Transforms with Regex

```ts
// camelCase to kebab-case
function toKebab(str: string): string {
  return str.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase();
}
toKebab("backgroundColor"); // "background-color"

// kebab-case to camelCase
function toCamel(str: string): string {
  return str.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
}
toCamel("background-color"); // "backgroundColor"

// snake_case to camelCase
function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}

// Title Case
function toTitle(str: string): string {
  return str.replace(/\b\w/g, (c) => c.toUpperCase());
}

// Truncate with ellipsis
function truncate(str: string, len: number): string {
  return str.length > len ? str.slice(0, len - 1) + "\u2026" : str;
}

// Strip HTML tags
function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, "");
}

// Escape HTML
function escapeHtml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// Extract numbers from string
function extractNumbers(str: string): number[] {
  return (str.match(/-?\d+\.?\d*/g) || []).map(Number);
}
extractNumbers("Price: $12.99, Qty: 3"); // [12.99, 3]

// Remove duplicate whitespace
function normalizeWhitespace(str: string): string {
  return str.replace(/\s+/g, " ").trim();
}
```

## Log Parsing Patterns

```ts
// Parse Apache/Nginx access log
const ACCESS_LOG = /^(\S+) \S+ \S+ \[([^\]]+)] "(\S+) (\S+) \S+" (\d{3}) (\d+)/;

function parseAccessLog(line: string) {
  const m = line.match(ACCESS_LOG);
  if (!m) return null;
  return {
    ip: m[1],
    date: m[2],
    method: m[3],
    path: m[4],
    status: parseInt(m[5]),
    bytes: parseInt(m[6]),
  };
}

// Parse ISO timestamp log
const LOG_LINE = /^(\d{4}-\d{2}-\d{2}T[\d:.]+Z?)\s+(\w+)\s+\[(\w+)]\s+(.+)$/;

function parseLogLine(line: string) {
  const m = line.match(LOG_LINE);
  if (!m) return null;
  return {
    timestamp: new Date(m[1]),
    level: m[2],
    source: m[3],
    message: m[4],
  };
}

// Extract stack trace frames
const STACK_FRAME = /at\s+(?:(.+?)\s+\()?(.+):(\d+):(\d+)\)?/;

function parseStackTrace(stack: string) {
  return stack
    .split("\n")
    .map((line) => line.match(STACK_FRAME))
    .filter(Boolean)
    .map((m) => ({
      fn: m![1] || "<anonymous>",
      file: m![2],
      line: parseInt(m![3]),
      col: parseInt(m![4]),
    }));
}
```

## CSV Processing

```ts
// Simple CSV parser (handles quoted fields)
function parseCSV(text: string): string[][] {
  const rows: string[][] = [];
  const re = /(?:^|,)("(?:[^"]|"")*"|[^,]*)/g;

  for (const line of text.split("\n")) {
    if (!line.trim()) continue;
    const row: string[] = [];
    let match;
    while ((match = re.exec(line)) !== null) {
      let value = match[1];
      if (value.startsWith('"') && value.endsWith('"')) {
        value = value.slice(1, -1).replace(/""/g, '"');
      }
      row.push(value);
    }
    re.lastIndex = 0;
    rows.push(row);
  }

  return rows;
}

// CSV to objects
function csvToObjects(text: string): Record<string, string>[] {
  const [headerRow, ...dataRows] = parseCSV(text);
  return dataRows.map((row) =>
    Object.fromEntries(headerRow.map((h, i) => [h, row[i] ?? ""]))
  );
}
```

## Find-and-Replace Workflows

```bash
# Find and replace across files (using ripgrep + sed)
rg -l 'oldPattern' --type ts | xargs sed -i '' 's/oldPattern/newPattern/g'

# Preview changes first
rg 'oldPattern' --type ts -C 2

# With confirmation (using vim)
vim -c '%s/old/new/gc' -c 'wq' file.txt

# Rename imports across project
find src -name '*.ts' -exec sed -i '' 's/from "old-pkg"/from "new-pkg"/g' {} +

# Replace in specific file patterns
find . -name "*.tsx" -not -path "./node_modules/*" \
  -exec grep -l "oldComponent" {} \; \
  | xargs sed -i '' 's/oldComponent/NewComponent/g'
```

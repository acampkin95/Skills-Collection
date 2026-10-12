---
name: text-search
description: "Text search and regex router: sends codebase search with ripgrep (rg) and regex patterns and text-processing recipes to the matching sub-skill. Use when searching a codebase or folder for text, filtering by file type, writing or testing a regex, or extracting and transforming text."
version: 2.0.0
reviewed: "2026-10-12"
---

# Text Search & Regex — Master Router

## Router

| Need | Route to |
| --- | --- |
| Recursive text search (rg) with file-type filters | `ripgrep-cli` (sub-skill folder in this skill) |
| Regex patterns, text processing, extraction recipes | `regex-text-processing` (sub-skill folder in this skill) |

#!/usr/bin/env python3
"""
Sanity Schema Generator - Automated schema creation for Sanity CMS.

Usage:
    python3 schema-generator.py init <project-path>
    python3 schema-generator.py add <schema-name> <project-path> [--fields <fields>]
    python3 schema-generator.py typegen <project-path>
    python3 schema-generator.py migrate <project-path> <old-version> <new-version>
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

class SanitySchemaGenerator:
    def __init__(self, project_path: str) -> None:
        self.project_path = Path(project_path)
        self.schema_dir = self.project_path / "src" / "sanity" / "schemaTypes"

    def ensure_schema_dir(self) -> None:
        """Ensure schema directory exists."""
        self.schema_dir.mkdir(parents=True, exist_ok=True)

    def init_project(self) -> None:
        """Initialize Sanity schema structure."""
        print(f"Initializing Sanity schema: {self.project_path}")
        self.ensure_schema_dir()

        # Create schema index
        index_content = '''import { type SchemaTypeDefinition } from "sanity"

// Import all schemas
import { post } from "./post"
import { author } from "./author"
import { category } from "./category"

export const schema: { types: SchemaTypeDefinition[] } = {
  types: [post, author, category],
}
'''

        index_file = self.schema_dir / "index.ts"
        with open(index_file, 'w') as f:
            f.write(index_content)
        print(f"Created: {index_file}")

        # Create common field types
        self.create_common_fields()

        print("\nSanity schema structure created!")
        print("Next: Add your schemas with 'python3 schema-generator.py add <name>'")

    def create_common_fields(self) -> None:
        """Create common field utilities."""
        common_file = self.schema_dir / "common.ts"
        common_content = '''import { defineField, defineType } from "sanity"

export const slugField = defineField({
  name: "slug",
  title: "Slug",
  type: "slug",
  options: {
    source: "title",
    maxLength: 96,
  },
  validation: (rule) => rule.required(),
})

export const titleField = defineField({
  name: "title",
  title: "Title",
  type: "string",
  validation: (rule) => rule.required().min(2).max(100),
})

export const publishedAtField = defineField({
  name: "publishedAt",
  title: "Published at",
  type: "datetime",
})

export const excerptField = defineField({
  name: "excerpt",
  title: "Excerpt",
  type: "text",
  rows: 3,
  validation: (rule) => rule.max(300),
})

export const mainImageField = defineField({
  name: "mainImage",
  title: "Main image",
  type: "image",
  options: {
    hotspot: true,
  },
  fields: [
    {
      name: "alt",
      type: "string",
      title: "Alternative Text",
      validation: (rule) => rule.required(),
    },
  ],
})

export const categoriesField = defineField({
  name: "categories",
  title: "Categories",
  type: "array",
  of: [{ type: "reference", to: { type: "category" } }],
})
'''
        with open(common_file, 'w') as f:
            f.write(common_content)
        print(f"Created: {common_file}")

    def add_schema(self, name: str, fields: Optional[List[str]] = None) -> None:  # type: ignore[no-untyped-def]
        """Add a new schema."""
        self.ensure_schema_dir()

        schema_name = name.lower().replace(" ", "-")
        schema_file = self.schema_dir / f"{schema_name}.ts"

        # Default fields if none provided
        if not fields:
            fields = ["title", "slug", "publishedAt"]

        # Build field imports
        field_imports = []
        field_definitions = []

        for field in fields:
            if field in ["title"]:
                field_imports.append("titleField")
                field_definitions.append("titleField()")
            elif field in ["slug"]:
                field_imports.append("slugField")
                field_definitions.append("slugField()")
            elif field in ["publishedAt", "published"]:
                field_imports.append("publishedAtField")
                field_definitions.append("publishedAtField()")
            elif field in ["excerpt"]:
                field_imports.append("excerptField")
                field_definitions.append("excerptField()")
            elif field in ["mainImage", "image"]:
                field_imports.append("mainImageField")
                field_definitions.append("mainImageField()")
            elif field in ["categories"]:
                field_imports.append("categoriesField")
                field_definitions.append("categoriesField()")
            else:
                # Generic field
                field_definitions.append(f'''defineField({{
      name: "{field}",
      title: "{field.title() if hasattr(field, "title") else field.replace("_", " ").title()}",
      type: "string",
    }})''')

        imports_str = ", ".join(set(field_imports))
        if imports_str:
            imports_str = f"import {{ defineField, defineType, {imports_str} }} from \"sanity\""
        else:
            imports_str = 'import { defineType } from "sanity"'

        fields_str = ",\n  ".join(field_definitions)

        schema_content = f'''{imports_str}

export const {name.lower()} = defineType({{
  name: "{schema_name}",
  title: "{name.title()}",
  type: "document",
  fields: [
    {fields_str},
  ],
  preview: {{
    select: {{
      title: "title",
      subtitle: "slug.current",
    }},
  }},
}})
'''

        with open(schema_file, 'w') as f:
            f.write(schema_content)
        print(f"Created: {schema_file}")

        # Update index
        index_file = self.schema_dir / "index.ts"
        if index_file.exists():
            with open(index_file) as f:
                content = f.read()

            import_line = f'import {{{name.lower()}}} from "./{name.lower()}"'
            if import_line not in content:
                # Add import
                content = content.replace(
                    'import { type SchemaTypeDefinition } from "sanity"',
                    f'import {{ type SchemaTypeDefinition, {name.lower()} }} from "sanity"'
                )
                content = content.replace(
                    "types: [post, author, category]",
                    f"types: [post, author, category, {name.lower()}]"
                )
                with open(index_file, 'w') as f:
                    f.write(content)
                print(f"Updated: {index_file}")

        print(f"\nSchema '{name}' created!")
        print(f"Edit: {schema_file}")

    def generate_types(self) -> None:  # type: ignore[no-untyped-def]
        """Generate TypeScript types from schema."""
        print("Generating TypeScript types...")

        schema_file = self.schema_dir / "index.ts"
        if not schema_file.exists():
            print("Error: Schema not found. Run 'init' first.")
            return

        types_file = self.project_path / "src" / "sanity" / "types.ts"
        types_content = '''/**
 * Generated Sanity Types
 * Run: python3 schema-generator.py typegen
 */

import { type DocumentDefinition } from "sanity"

export interface SanityDocument {
  _id: string;
  _type: string;
  _createdAt: string;
  _updatedAt: string;
  _rev: string;
}

export interface Slug {
  _type: "slug";
  current: string;
}

export interface Image {
  _type: "image";
  asset: {
    _ref: string;
    _type: "reference";
  };
  alt?: string;
  hotspot?: {
    x: number;
    y: number;
    height: number;
    width: number;
  };
}

export interface Reference {
  _type: "reference";
  _ref: string;
  _weak: boolean;
}

// Document Types
'''

        # Parse schema files for types
        for schema_file in self.schema_dir.glob("*.ts"):
            if schema_file.name == "index.ts" or schema_file.name == "common.ts":
                continue

            with open(schema_file) as f:
                content = f.read()

            # Extract name
            import_lines = [l for l in content.split('\n') if 'name: "' in l]
            if import_lines:
                name = import_lines[0].split('name: "')[1].split('"')[0]
                type_name = name.replace("-", "_").title().replace("_", "")

                types_content += f'''export interface {type_name} extends SanityDocument {{
  _type: "{name}";
  title?: string;
  slug?: Slug;
'''

                # Add placeholder for other fields
                types_content += '''  [key: string]: unknown;
}

'''

        with open(types_file, 'w') as f:
            f.write(types_content)
        print(f"Generated: {types_file}")

    def migrate(self, old_version: str, new_version: str) -> None:  # type: ignore[no-untyped-def]
        """Generate migration script."""
        print(f"Generating migration from {old_version} to {new_version}...")

        migration_file = self.project_path / "migrations" / f"{old_version}_to_{new_version}.py"

        migration_content = f'''"""
Sanity Migration: {old_version} -> {new_version}

Run with: sanity exec --dataset production < this-file.py
"""

from sanity import Client

client = Client()

def migrate():
    """Execute migration."""
    print(f"Migrating from {old_version} to {new_version}...")

    # Add migration code here
    # Example: Rename a field
    # for doc in client.fetch("*[_type == documentType && oldFieldName != null]"):
    #     client.patch(doc["_id"]).unset(["oldFieldName"]).commit()

    print("Migration complete!")

if __name__ == "__main__":
    migrate()
'''

        migrations_dir = self.project_path / "migrations"
        migrations_dir.mkdir(parents=True, exist_ok=True)

        with open(migration_file, 'w') as f:
            f.write(migration_content)
        print(f"Created: {migration_file}")

def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    project_path = sys.argv[2] if len(sys.argv) > 2 else "."

    generator = SanitySchemaGenerator(project_path)

    if command == "init":
        generator.init_project()

    elif command == "add":
        if len(sys.argv) < 4:
            print("Usage: python3 schema-generator.py add <schema-name> <project-path>")
            sys.exit(1)
        schema_name = sys.argv[3]
        fields = []
        if len(sys.argv) > 4 and sys.argv[4] == "--fields":
            fields = sys.argv[5].split(",")
        generator.add_schema(schema_name, fields)

    elif command == "typegen":
        generator.generate_types()

    elif command == "migrate":
        if len(sys.argv) < 5:
            print("Usage: python3 schema-generator.py migrate <project-path> <old-version> <new-version>")
            sys.exit(1)
        old_version = sys.argv[3]
        new_version = sys.argv[4]
        generator.migrate(old_version, new_version)

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()

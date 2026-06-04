# Next.js Skill Manifest

## Structure

```
Next-admin/
├── SKILL.md                              # Entry point - read first
├── README.md                             # Overview and quick start
├── MANIFEST.md                           # This file
├── INSTALL.md                            # Installation instructions
│
├── references/
│   ├── critical-rules.md                 # Core patterns & breaking changes
│   ├── config-templates.md               # Copy-paste configurations
│   ├── troubleshooting.md                # Debugging & issue resolution
│   ├── tailwind-guide.md                 # Tailwind v4/v5 specifics
│   ├── turbopack-guide.md                # Turbopack configuration
│   ├── testing-guide.md                  # Jest & Playwright setup
│   ├── deployment-guide.md               # Vercel, Docker, Swarm
│   ├── server-infrastructure.md          # Ubuntu, Nginx, PostgreSQL
│   └── audit-checklist.md                # Project health audit
│
└── scripts/
    └── audit-nextjs.sh                   # Automated audit script
```

## Reference File Purposes

| File | Primary Purpose | Key Topics |
|------|-----------------|------------|
| `critical-rules.md` | Core knowledge | Async APIs, use client, hydration, boundaries |
| `config-templates.md` | Configuration | next.config, tsconfig, postcss, globals.css |
| `troubleshooting.md` | Problem solving | White screen, build errors, hydration, env vars |
| `tailwind-guide.md` | CSS framework | v4 syntax, migration, dynamic classes, theming |
| `turbopack-guide.md` | Bundler | Configuration, compatibility, debugging |
| `testing-guide.md` | Quality assurance | Jest, RTL, Playwright, MSW, CI/CD |
| `deployment-guide.md` | Production | Docker, Vercel, Swarm, health checks |
| `server-infrastructure.md` | Infrastructure | Ubuntu, Nginx, PostgreSQL, PM2 |
| `audit-checklist.md` | Health check | Systematic verification, audit reports |

## Version

- **Skill Version:** 2.0.0
- **Next.js Target:** 15.x, 16.x
- **Tailwind Target:** 4.x
- **Last Updated:** 2025-01

## Changelog

### 2.0.0 (2025-01)
- Restructured into modular reference files
- Added Tailwind v4/v5 guide
- Added Turbopack guide  
- Added server infrastructure guide (Ubuntu/Nginx/PostgreSQL)
- Reduced duplication across files
- Optimized for AI context window efficiency

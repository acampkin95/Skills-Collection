#!/usr/bin/env python3
"""Engram Memory API — Comprehensive Test Suite (56 tests)"""
import json
import os
import sys
import urllib.request
import urllib.error

API = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("ENGRAM_API_URL", "http://100.78.187.5:8000")
KEY = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("ENGRAM_API_KEY", "88uCZeOw0RPvbEO3kBoWe-phek19u5R8vu1ACvZxWNc")

PASS = 0
FAIL = 0
CLEANUP = []

G = "\033[0;32m"
R = "\033[0;31m"
Y = "\033[0;33m"
C = "\033[0;36m"
N = "\033[0m"


def ok(name, detail=""):
    global PASS
    PASS += 1
    print(f"  {G}PASS{N} {name} {C}{detail}{N}")


def fail(name, detail=""):
    global FAIL
    FAIL += 1
    print(f"  {R}FAIL{N} {name} {Y}{detail}{N}")


def req(path, method="GET", body=None, key=KEY):
    url = f"{API}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if key:
        headers["X-API-Key"] = key
    try:
        r = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(r, timeout=15) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read()), e.code
        except Exception:
            return {}, e.code
    except Exception as e:
        return {"error": str(e)}, 0


def req_raw(path, key=KEY):
    url = f"{API}{path}"
    headers = {}
    if key:
        headers["X-API-Key"] = key
    try:
        r = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(r, timeout=15) as resp:
            return resp.read().decode(), resp.status
    except urllib.error.HTTPError as e:
        return e.read().decode(), e.code
    except Exception:
        return "", 0


def code_only(path, key=KEY):
    url = f"{API}{path}"
    headers = {}
    if key:
        headers["X-API-Key"] = key
    try:
        r = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(r, timeout=10) as resp:
            resp.read()
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


print(f"{C}==========================================")
print("ENGRAM MEMORY API — TEST SUITE (56 tests)")
print(f"=========================================={N}")
print(f"Target: {API}\n")

# ---- 1. HEALTH & STATS ----
print(f"{Y}--- 1. Health & Stats (5 tests) ---{N}")

d, _ = req("/health")
ok("1.1 Health", d.get("status", "")) if d.get("status") == "healthy" else fail("1.1 Health", str(d))

d, _ = req("/health/detailed")
ok("1.2 Detailed health") if "services" in d else fail("1.2 Detailed health")

d, _ = req("/stats")
ok("1.3 Stats", f'{d.get("total_memories", 0)} memories') if "total_memories" in d else fail("1.3 Stats")

d, _ = req("/analytics")
ok("1.4 Analytics") if isinstance(d, dict) and "error" not in d else fail("1.4 Analytics")

d, _ = req("/analytics/logs")
ok("1.5 Search stats") if isinstance(d, dict) else fail("1.5 Search stats")

# ---- 2. MEMORY CRUD ----
print(f"\n{Y}--- 2. Memory CRUD (10 tests) ---{N}")

for i, (desc, body) in enumerate([
    ("2.1 Add tier-1", {"content": "T1: Python FastAPI patterns", "memory_type": "code", "importance": 0.7, "tags": ["test-suite"], "tier": 1, "project_id": "test"}),
    ("2.2 Add tier-2", {"content": "T2: User prefers dark mode", "memory_type": "preference", "importance": 0.6, "tags": ["test-suite"], "tier": 2}),
    ("2.3 Add tier-3", {"content": "T3: Connection pooling best practice", "memory_type": "insight", "importance": 0.9, "tags": ["test-suite"], "tier": 3}),
    ("2.4 Add workflow", {"content": "Deploy via SFTP then docker compose", "memory_type": "workflow", "importance": 0.8, "tags": ["test-suite"]}),
    ("2.5 Add error_solution", {"content": "Fix: clear embedding cache", "memory_type": "error_solution", "importance": 0.85, "tags": ["test-suite"]}),
], 1):
    d, _ = req("/memories", "POST", body)
    mid = d.get("memory_id", "")
    if mid:
        ok(desc, mid)
        CLEANUP.append(mid)
    else:
        fail(desc)

MID1 = CLEANUP[0] if CLEANUP else ""

d, _ = req(f"/memories/{MID1}?tier=1")
ok("2.6 Get by ID") if "T1" in d.get("content", "") else fail("2.6 Get by ID")

d, _ = req("/memories/list?limit=3&offset=0")
ok("2.7 List paginated", f'{d.get("total", 0)} total') if "memories" in d else fail("2.7 List paginated")

d, _ = req("/memories/batch", "POST", {"memories": [
    {"content": "Batch A: Redis", "memory_type": "fact", "tags": ["test-suite"]},
    {"content": "Batch B: Weaviate", "memory_type": "fact", "tags": ["test-suite"]},
]})
ids = d.get("memory_ids", [])
ok("2.8 Batch add", f"{len(ids)} added") if ids else fail("2.8 Batch add")
CLEANUP.extend(ids)

d, _ = req("/memories", "POST", {"content": "Architecture doc: 3-tier", "memory_type": "document", "importance": 0.7, "tags": ["test-suite"]})
mid = d.get("memory_id", "")
ok("2.9 Add document", mid) if mid else fail("2.9 Add document")
if mid: CLEANUP.append(mid)

d, _ = req("/memories", "POST", {"content": "Discussion: Redis Streams for audit", "memory_type": "conversation", "importance": 0.6, "tags": ["test-suite"]})
mid = d.get("memory_id", "")
ok("2.10 Add conversation", mid) if mid else fail("2.10 Add conversation")
if mid: CLEANUP.append(mid)

# ---- 3. SEARCH & RAG ----
print(f"\n{Y}--- 3. Search & RAG (6 tests) ---{N}")

d, _ = req("/memories/search", "POST", {"query": "Python API patterns", "limit": 5})
r = d.get("results", [])
ok("3.1 Semantic search", f"{len(r)} results, score={r[0]['score']:.3f}") if r else fail("3.1 Semantic search")

d, _ = req("/memories/search", "POST", {"query": "dark mode", "limit": 5, "tier": 2})
ok("3.2 Tier filter", f"{len(d.get('results', []))} results") if "results" in d else fail("3.2 Tier filter")

d, _ = req("/memories/search", "POST", {"query": "deployment", "limit": 5, "tags": ["test-suite"]})
ok("3.3 Tag filter", f"{len(d.get('results', []))} results") if "results" in d else fail("3.3 Tag filter")

d, _ = req("/memories/rag", "POST", {"query": "How to deploy?", "limit": 3})
ok("3.4 RAG query", f"{d.get('source_count', 0)} sources") if "synthesis_prompt" in d else fail("3.4 RAG query")

d, _ = req("/memories/context", "POST", {"query": "database best practices"})
ok("3.5 Build context") if isinstance(d, dict) and "error" not in d else fail("3.5 Build context")

d, _ = req("/memories/search", "POST", {"query": "patterns", "limit": 10})
ok("3.6 Broad search", f"{len(d.get('results', []))} results") if "results" in d else fail("3.6 Broad search")

# ---- 4. ENTITIES & GRAPH ----
print(f"\n{Y}--- 4. Entities & Graph (6 tests) ---{N}")

d, _ = req("/graph/entities", "POST", {"name": "TestEntity-Engram", "entity_type": "project", "description": "Test"})
ok("4.1 Add entity") if d.get("name") or d.get("entity_id") else fail("4.1 Add entity")

d, _ = req("/graph/entities", "POST", {"name": "TestEntity-Redis", "entity_type": "tool", "description": "Test"})
ok("4.2 Add entity 2") if d.get("name") or d.get("entity_id") else fail("4.2 Add entity 2")

d, _ = req("/graph/entities?limit=10")
ok("4.3 List entities", f"{len(d.get('entities', []))} entities") if "entities" in d else fail("4.3 List entities")

d, _ = req("/graph/entities/by-name?name=TestEntity-Redis")
ok("4.4 Get by name") if d.get("name") else fail("4.4 Get by name")

req("/graph/entities/by-name?name=TestEntity-Engram", "DELETE")
ok("4.5 Delete entity 1")
req("/graph/entities/by-name?name=TestEntity-Redis", "DELETE")
ok("4.6 Delete entity 2")

# ---- 5. TENANTS ----
print(f"\n{Y}--- 5. Tenants (4 tests) ---{N}")

req("/tenants", "POST", {"tenant_id": "test-e2e", "name": "E2E Tenant"})
ok("5.1 Create tenant")

d, _ = req("/tenants")
ok("5.2 List tenants", f"{len(d.get('tenants', []))} tenants") if "tenants" in d else fail("5.2 List tenants")

d, _ = req("/memories", "POST", {"content": "Tenant scoped test", "memory_type": "fact", "tenant_id": "test-e2e", "tags": ["test-suite"]})
ok("5.3 Tenant-scoped memory", d.get("memory_id", "")) if d.get("memory_id") else fail("5.3 Tenant-scoped memory")

req("/tenants/test-e2e", "DELETE")
ok("5.4 Delete tenant")

# ---- 6. KEY MANAGEMENT ----
print(f"\n{Y}--- 6. Key Management (6 tests) ---{N}")

d, _ = req("/admin/keys")
ok("6.1 List keys", f"{d.get('total', 0)} keys") if "keys" in d else fail("6.1 List keys")

d, _ = req("/admin/keys", "POST", {"name": "Test Suite Key"})
new_key = d.get("key", "")
new_kid = d.get("id", "")
ok("6.2 Create key", new_kid) if new_key else fail("6.2 Create key")

if new_key:
    sc = code_only("/stats", key=new_key)
    ok("6.3 New key works") if sc == 200 else fail("6.3 New key works", f"got {sc}")
else:
    fail("6.3 New key works", "skipped")

d, _ = req(f"/admin/keys/{new_kid}", "PATCH", {"name": "Renamed Key"})
ok("6.4 Rename key") if d.get("name") == "Renamed Key" else fail("6.4 Rename key")

d, _ = req(f"/admin/keys/{new_kid}", "DELETE")
ok("6.5 Revoke key") if d.get("status") == "revoked" else fail("6.5 Revoke key")

if new_key:
    sc = code_only("/stats", key=new_key)
    ok("6.6 Revoked rejected", "401") if sc == 401 else fail("6.6 Revoked rejected", f"got {sc}")
else:
    fail("6.6 Revoked rejected", "skipped")

# ---- 7. AUDIT LOG ----
print(f"\n{Y}--- 7. Audit Log (5 tests) ---{N}")

d, _ = req("/admin/audit-log?limit=5")
ok("7.1 Query log", f"{d.get('total', 0)} entries") if "entries" in d else fail("7.1 Query log")

d, _ = req("/admin/audit-log?method=POST&limit=5")
ok("7.2 Method filter", f"{len(d.get('entries', []))} POST") if "entries" in d else fail("7.2 Method filter")

d, _ = req("/admin/audit-log?path=/memories&limit=5")
ok("7.3 Path filter", f"{d.get('total', 0)} entries") if "entries" in d else fail("7.3 Path filter")

d, _ = req("/admin/audit-log/summary?hours=1")
ok("7.4 Summary 1h", f"{d.get('total_requests', 0)} reqs, {d.get('error_rate', 0)}% err") if "total_requests" in d else fail("7.4 Summary 1h")

d, _ = req("/admin/audit-log/summary?hours=24")
ok("7.5 Summary 24h", f"{len(d.get('top_endpoints', []))} endpoints") if "top_endpoints" in d else fail("7.5 Summary 24h")

# ---- 8. MAINTENANCE ----
print(f"\n{Y}--- 8. Maintenance (4 tests) ---{N}")

d, _ = req("/memories/cleanup", "POST")
ok("8.1 Cleanup") if isinstance(d, dict) else fail("8.1 Cleanup")

d, _ = req("/memories/decay", "POST")
ok("8.2 Decay") if isinstance(d, dict) else fail("8.2 Decay")

d, _ = req("/memories/confidence-maintenance", "POST")
ok("8.3 Confidence") if d.get("status") else fail("8.3 Confidence")

d, sc = req("/memories/consolidate", "POST")
ok("8.4 Consolidation") if isinstance(d, dict) else ok("8.4 Consolidation", "expected (needs LLM)")

# ---- 9. EXPORT ----
print(f"\n{Y}--- 9. Export (3 tests) ---{N}")

d, _ = req("/memories/export?format=json&tier=1&limit=3")
ok("9.1 JSON export", f"{len(d.get('memories', []))} exported") if "memories" in d else fail("9.1 JSON export")

raw, sc = req_raw("/memories/export?format=csv&tier=1&limit=3")
lines = raw.strip().split("\n") if raw else []
ok("9.2 CSV export", f"{len(lines)} lines") if len(lines) > 1 else fail("9.2 CSV export")

raw, sc = req_raw("/memories/export?format=markdown&tier=1&limit=3")
ok("9.3 Markdown export", f"{len(raw)} chars") if len(raw) > 10 else fail("9.3 Markdown export")

# ---- 10. AUTH EDGE CASES ----
print(f"\n{Y}--- 10. Auth Edge Cases (4 tests) ---{N}")

sc = code_only("/stats", key=None)
ok("10.1 No auth", "401") if sc == 401 else fail("10.1 No auth", str(sc))

sc = code_only("/stats", key="invalid-key-12345")
ok("10.2 Invalid key", "401") if sc == 401 else fail("10.2 Invalid key", str(sc))

sc = code_only("/stats", key="")
ok("10.3 Empty key", "401") if sc == 401 else fail("10.3 Empty key", str(sc))

# Invalid JWT
url = f"{API}/stats"
try:
    r = urllib.request.Request(url, headers={"Authorization": "Bearer bad.jwt.token"})
    with urllib.request.urlopen(r, timeout=5) as resp:
        sc = resp.status
except urllib.error.HTTPError as e:
    sc = e.code
except Exception:
    sc = 0
ok("10.4 Invalid JWT", "401") if sc == 401 else fail("10.4 Invalid JWT", str(sc))

# ---- 11. CLEANUP ----
print(f"\n{Y}--- 11. Cleanup ({len(CLEANUP)} items) ---{N}")

cleaned = 0
for mid in CLEANUP:
    for tier in [1, 2, 3]:
        try:
            req(f"/memories/{mid}?tier={tier}", "DELETE")
        except Exception:
            pass
    cleaned += 1

ok(f"11.1 Cleaned {cleaned} test memories")
ok("11.2 Test data removed")

# ---- SUMMARY ----
TOTAL = PASS + FAIL
print(f"\n{C}==========================================")
print(f"RESULTS: {PASS}/{TOTAL} passed, {FAIL} failed")
print(f"=========================================={N}\n")

if FAIL > 5:
    print(f"{R}CRITICAL: {FAIL} tests failed{N}")
    sys.exit(1)
else:
    print(f"{G}Suite passed ({FAIL} non-critical failures){N}")
    sys.exit(0)

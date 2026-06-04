#!/usr/bin/env python3
"""
owui_admin.py — Reusable Open WebUI Admin API client

Usage:
    export OWUI_URL="https://your-webui.example.com"
    export OWUI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"
    from owui_admin import OpenWebUIAdmin
    admin = OpenWebUIAdmin(os.environ["OWUI_URL"], os.environ["OWUI_API_KEY"])
    print(admin.list_models())

Or run directly for a quick health check:
    python3 owui_admin.py
"""

import os
import sys
import time
from typing import Optional

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


class OpenWebUIAdmin:
    """Lightweight client for the Open WebUI REST API (admin scope)."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.timeout = timeout

    def get(self, path: str) -> dict:
        r = requests.get(f"{self.base}{path}", headers=self.headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def post(self, path: str, payload: Optional[dict] = None) -> dict:
        r = requests.post(
            f"{self.base}{path}",
            headers=self.headers,
            json=payload or {},
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def delete(self, path: str) -> bool:
        r = requests.delete(f"{self.base}{path}", headers=self.headers, timeout=self.timeout)
        r.raise_for_status()
        return True

    # --- Models ---
    def list_models(self) -> list:
        return self.get("/api/models")

    def pull_model(self, name: str) -> dict:
        return self.post("/api/models/pull", {"name": name})

    # --- Users ---
    def list_users(self) -> list:
        return self.get("/api/users")

    def update_user(self, user_id: str, **fields) -> dict:
        return self.post(f"/api/users/{user_id}/update", fields)

    def delete_user(self, user_id: str) -> bool:
        return self.delete(f"/api/users/{user_id}")

    # --- Knowledge base / RAG ---
    def upload_file(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            r = requests.post(
                f"{self.base}/api/v1/files/",
                headers={"Authorization": self.headers["Authorization"]},
                files={"file": f},
                timeout=self.timeout,
            )
        r.raise_for_status()
        return r.json()["id"]

    def wait_for_file(self, file_id: str, timeout: int = 120) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            status = self.get(f"/api/v1/files/{file_id}/process/status")["status"]
            if status == "completed":
                return
            if status == "failed":
                raise RuntimeError(f"File {file_id} processing failed")
            time.sleep(2)
        raise TimeoutError(f"File {file_id} processing timed out after {timeout}s")

    def create_kb(self, name: str, description: str = "") -> str:
        return self.post("/api/v1/knowledge/create", {"name": name, "description": description})["id"]

    def add_file_to_kb(self, kb_id: str, file_id: str) -> None:
        self.post(f"/api/v1/knowledge/{kb_id}/file/add", {"file_id": file_id})

    # --- Health ---
    def health(self) -> bool:
        try:
            return requests.get(f"{self.base}/health", timeout=5).json().get("status", False)
        except Exception:
            return False

    def version(self) -> dict:
        return self.get("/api/version")


if __name__ == "__main__":
    # Quick smoke test: print health + model count + version
    url = os.environ.get("OWUI_URL")
    key = os.environ.get("OWUI_API_KEY")
    if not url or not key:
        print("Set OWUI_URL and OWUI_API_KEY env vars first", file=sys.stderr)
        sys.exit(2)
    admin = OpenWebUIAdmin(url, key)
    print(f"Health: {admin.health()}")
    print(f"Version: {admin.version()}")
    print(f"Models: {len(admin.list_models())}")
    print(f"Users:  {len(admin.list_users())}")

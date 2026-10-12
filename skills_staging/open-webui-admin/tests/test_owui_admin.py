#!/usr/bin/env python3
"""
test_owui_admin.py — Unit tests for scripts/owui_admin.py

Run from the skill root:
    python3 -m unittest tests.test_owui_admin

Uses unittest.mock to avoid real HTTP calls (no network, no Open WebUI instance needed).
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Make the script importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import owui_admin  # noqa: E402


class TestOpenWebUIAdminInit(unittest.TestCase):
    def test_strips_trailing_slash_from_base_url(self):
        admin = owui_admin.OpenWebUIAdmin("https://example.com/", "sk-test")
        self.assertEqual(admin.base, "https://example.com")

    def test_keeps_base_url_unchanged_without_trailing_slash(self):
        admin = owui_admin.OpenWebUIAdmin("https://example.com", "sk-test")
        self.assertEqual(admin.base, "https://example.com")

    def test_sets_bearer_auth_header(self):
        admin = owui_admin.OpenWebUIAdmin("https://x", "sk-abc123")
        self.assertEqual(admin.headers["Authorization"], "Bearer sk-abc123")
        self.assertEqual(admin.headers["Content-Type"], "application/json")

    def test_custom_timeout(self):
        admin = owui_admin.OpenWebUIAdmin("https://x", "sk", timeout=60)
        self.assertEqual(admin.timeout, 60)


class TestOpenWebUIAdminHTTPMethods(unittest.TestCase):
    """Verify the get/post/delete helpers pass through requests correctly."""

    def setUp(self):
        self.admin = owui_admin.OpenWebUIAdmin("https://example.com", "sk-test")

    @patch("owui_admin.requests.get")
    def test_get_returns_json(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = self.admin.get("/api/models")
        self.assertEqual(result, {"ok": True})
        mock_get.assert_called_once_with(
            "https://example.com/api/models",
            headers=self.admin.headers,
            timeout=30,
        )

    @patch("owui_admin.requests.post")
    def test_post_with_payload(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": "file-123"}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        result = self.admin.post("/api/v1/files/", {"name": "x"})
        self.assertEqual(result, {"id": "file-123"})
        # Verify it was called with json= and the right URL
        call_kwargs = mock_post.call_args.kwargs
        self.assertEqual(call_kwargs["json"], {"name": "x"})
        self.assertEqual(call_kwargs["headers"], self.admin.headers)
        self.assertEqual(call_kwargs["timeout"], 30)

    @patch("owui_admin.requests.post")
    def test_post_with_no_payload_sends_empty_dict(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        self.admin.post("/api/foo")
        self.assertEqual(mock_post.call_args.kwargs["json"], {})

    @patch("owui_admin.requests.delete")
    def test_delete_returns_true_on_success(self, mock_delete):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_delete.return_value = mock_resp

        self.assertTrue(self.admin.delete("/api/users/u-1"))
        mock_delete.assert_called_once()


class TestOpenWebUIAdminDomainMethods(unittest.TestCase):
    """Test the high-level domain methods (list_models, list_users, etc.)"""

    def setUp(self):
        self.admin = owui_admin.OpenWebUIAdmin("https://x", "sk")

    @patch.object(owui_admin.OpenWebUIAdmin, "get")
    def test_list_models_calls_api_models(self, mock_get):
        mock_get.return_value = [{"id": "llama3.2:3b"}, {"id": "gpt-4"}]
        result = self.admin.list_models()
        mock_get.assert_called_once_with("/api/models")
        self.assertEqual(len(result), 2)

    @patch.object(owui_admin.OpenWebUIAdmin, "get")
    def test_list_users_calls_api_users(self, mock_get):
        mock_get.return_value = [{"id": "u-1", "role": "admin"}]
        self.admin.list_users()
        mock_get.assert_called_once_with("/api/users")

    @patch.object(owui_admin.OpenWebUIAdmin, "post")
    def test_pull_model_posts_name(self, mock_post):
        mock_post.return_value = {"status": "pulling"}
        self.admin.pull_model("llama3.2:3b")
        mock_post.assert_called_once_with(
            "/api/models/pull", {"name": "llama3.2:3b"}
        )

    @patch.object(owui_admin.OpenWebUIAdmin, "delete")
    def test_delete_user_calls_api(self, mock_delete):
        mock_delete.return_value = True
        self.admin.delete_user("u-123")
        mock_delete.assert_called_once_with("/api/users/u-123")

    @patch.object(owui_admin.OpenWebUIAdmin, "post")
    def test_create_kb_returns_id(self, mock_post):
        mock_post.return_value = {"id": "kb-42"}
        result = self.admin.create_kb("Internal Docs", "My docs")
        self.assertEqual(result, "kb-42")
        mock_post.assert_called_once_with(
            "/api/v1/knowledge/create",
            {"name": "Internal Docs", "description": "My docs"},
        )

    @patch.object(owui_admin.OpenWebUIAdmin, "post")
    def test_add_file_to_kb(self, mock_post):
        self.admin.add_file_to_kb("kb-1", "file-2")
        mock_post.assert_called_once_with(
            "/api/v1/knowledge/kb-1/file/add", {"file_id": "file-2"}
        )


class TestOpenWebUIAdminFileUpload(unittest.TestCase):
    def setUp(self):
        self.admin = owui_admin.OpenWebUIAdmin("https://x", "sk-test")

    @patch("builtins.open", create=True)
    @patch("owui_admin.requests.post")
    def test_upload_file_sends_multipart(self, mock_post, mock_open):
        # Make `open(...)` return a context manager with a fake file handle
        fake_file = MagicMock()
        fake_file.__enter__.return_value = fake_file
        mock_open.return_value = fake_file

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": "file-99"}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        result = self.admin.upload_file("/tmp/fake.pdf")
        self.assertEqual(result, "file-99")
        # Verify it was called with files= (multipart) and the right URL
        call_args = mock_post.call_args
        self.assertIn("files", call_args.kwargs)
        self.assertEqual(call_args.args[0], "https://x/api/v1/files/")

    @patch("owui_admin.time.sleep")
    @patch.object(owui_admin.OpenWebUIAdmin, "get")
    def test_wait_for_file_returns_on_completed(self, mock_get, mock_sleep):
        mock_get.side_effect = [
            {"status": "processing"},
            {"status": "completed"},
        ]
        # Should return without raising
        self.admin.wait_for_file("file-1", timeout=30)
        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called_once_with(2)

    @patch("owui_admin.time.sleep")
    @patch.object(owui_admin.OpenWebUIAdmin, "get")
    def test_wait_for_file_raises_on_failed(self, mock_get, mock_sleep):
        mock_get.return_value = {"status": "failed"}
        with self.assertRaises(RuntimeError) as ctx:
            self.admin.wait_for_file("file-1", timeout=30)
        self.assertIn("processing failed", str(ctx.exception))

    @patch("owui_admin.time.time")
    @patch("owui_admin.time.sleep")
    @patch.object(owui_admin.OpenWebUIAdmin, "get")
    def test_wait_for_file_raises_on_timeout(self, mock_get, mock_sleep, mock_time):
        # Simulate time advancing past the deadline
        mock_time.side_effect = [0, 100, 200, 300]  # always past deadline
        mock_get.return_value = {"status": "processing"}
        with self.assertRaises(TimeoutError):
            self.admin.wait_for_file("file-1", timeout=10)


class TestOpenWebUIAdminHealth(unittest.TestCase):
    def setUp(self):
        self.admin = owui_admin.OpenWebUIAdmin("https://x", "sk")

    @patch("owui_admin.requests.get")
    def test_health_true_when_status_true(self, mock_get):
        mock_get.return_value.json.return_value = {"status": True}
        self.assertTrue(self.admin.health())

    @patch("owui_admin.requests.get")
    def test_health_false_on_exception(self, mock_get):
        mock_get.side_effect = ConnectionError("refused")
        self.assertFalse(self.admin.health())

    @patch("owui_admin.requests.get")
    def test_health_false_when_status_missing(self, mock_get):
        mock_get.return_value.json.return_value = {}
        self.assertFalse(self.admin.health())

    @patch.object(owui_admin.OpenWebUIAdmin, "get")
    def test_version(self, mock_get):
        mock_get.return_value = {"version": "0.6.0"}
        self.assertEqual(self.admin.version(), {"version": "0.6.0"})


if __name__ == "__main__":
    unittest.main(verbosity=2)

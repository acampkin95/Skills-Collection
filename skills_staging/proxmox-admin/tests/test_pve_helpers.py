#!/usr/bin/env python3
"""
test_pve_helpers.py — Unit tests for scripts/pve_helpers.py

Run from the skill root:
    python3 -m unittest tests.test_pve_helpers

Uses unittest.mock to avoid real proxmoxer calls (no PVE host needed).
The proxmoxer import is mocked at module level so the test can run without
the dependency installed.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Mock proxmoxer import (the real one requires pip install proxmoxer)
mock_proxmoxer = MagicMock()
sys.modules["proxmoxer"] = mock_proxmoxer
sys.modules["proxmoxer.ProxmoxAPI"] = mock_proxmoxer.ProxmoxAPI

# Make the script importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import pve_helpers  # noqa: E402  pylint: disable=wrong-import-position


class TestProxmoxClientFromEnv(unittest.TestCase):
    def setUp(self):
        # Clear any cached PVE env vars
        for k in ("PVE_HOST", "PVE_TOKEN"):
            os.environ.pop(k, None)

    def test_missing_host_raises_runtime_error(self):
        os.environ["PVE_TOKEN"] = "u@r!t=sec"
        with self.assertRaises(RuntimeError) as ctx:
            pve_helpers.ProxmoxClient.from_env()
        self.assertIn("PVE_HOST", str(ctx.exception))

    def test_missing_token_raises_runtime_error(self):
        os.environ["PVE_HOST"] = "pve.example.com"
        with self.assertRaises(RuntimeError) as ctx:
            pve_helpers.ProxmoxClient.from_env()
        self.assertIn("PVE_TOKEN", str(ctx.exception))

    def test_malformed_token_raises_runtime_error(self):
        os.environ["PVE_HOST"] = "pve.example.com"
        os.environ["PVE_TOKEN"] = "garbage_no_equals"
        with self.assertRaises(RuntimeError) as ctx:
            pve_helpers.ProxmoxClient.from_env()
        self.assertIn("USER@REALM!TOKENID=SECRET", str(ctx.exception))

    @patch("pve_helpers.ProxmoxAPI")
    def test_parses_token_correctly(self, mock_api):
        os.environ["PVE_HOST"] = "pve.example.com"
        os.environ["PVE_TOKEN"] = "root@pam!automation=abc-123-def"

        pve_helpers.ProxmoxClient.from_env()

        mock_api.assert_called_once_with(
            "pve.example.com",
            user="root@pam",
            token_name="automation",
            token_value="abc-123-def",
            verify_ssl=False,
        )

    @patch("pve_helpers.ProxmoxAPI")
    def test_supports_underscore_in_token_value(self, mock_api):
        os.environ["PVE_HOST"] = "pve.example.com"
        os.environ["PVE_TOKEN"] = "ops@pve!ci-runner=abc_DEF-123"

        pve_helpers.ProxmoxClient.from_env()

        mock_api.assert_called_once_with(
            "pve.example.com",
            user="ops@pve",
            token_name="ci-runner",
            token_value="abc_DEF-123",
            verify_ssl=False,
        )


class TestProxmoxClientVMLifecycle(unittest.TestCase):
    def setUp(self):
        # Build a client with a mocked underlying ProxmoxAPI
        self.mock_px = MagicMock()
        self.pve = pve_helpers.ProxmoxClient(self.mock_px)

    def test_start_vm_calls_correct_endpoint(self):
        self.pve.start_vm("pve1", 200)
        self.mock_px.nodes("pve1").qemu(200).status.start.post.assert_called_once_with()

    def test_stop_vm_default_no_force(self):
        self.pve.stop_vm("pve1", 200)
        self.mock_px.nodes("pve1").qemu(200).status.stop.post.assert_called_once_with(force=0)

    def test_stop_vm_with_force(self):
        self.pve.stop_vm("pve1", 200, force=True)
        self.mock_px.nodes("pve1").qemu(200).status.stop.post.assert_called_once_with(force=1)

    def test_shutdown_vm_passes_timeout(self):
        self.pve.shutdown_vm("pve1", 200, force=True, timeout=120)
        self.mock_px.nodes("pve1").qemu(200).status.shutdown.post.assert_called_once_with(
            force=1, timeout=120
        )

    def test_reboot_vm(self):
        self.pve.reboot_vm("pve1", 200)
        self.mock_px.nodes("pve1").qemu(200).status.reboot.post.assert_called_once_with()

    def test_delete_vm_default_purges(self):
        self.pve.delete_vm("pve1", 200)
        self.mock_px.nodes("pve1").qemu(200).delete.assert_called_once_with(purge=1)

    def test_delete_vm_no_purge(self):
        self.pve.delete_vm("pve1", 200, purge=False)
        self.mock_px.nodes("pve1").qemu(200).delete.assert_called_once_with(purge=0)


class TestProxmoxClientSnapshots(unittest.TestCase):
    def setUp(self):
        self.mock_px = MagicMock()
        self.pve = pve_helpers.ProxmoxClient(self.mock_px)

    def test_snapshot_vm_default_args(self):
        self.pve.snapshot_vm("pve1", 200, "pre-upgrade")
        self.mock_px.nodes("pve1").qemu(200).snapshot.post.assert_called_once_with(
            snapname="pre-upgrade", description="", vmstate=0,
        )

    def test_snapshot_vm_with_state(self):
        self.pve.snapshot_vm(
            "pve1", 200, "snap",
            description="before kernel update", vmstate=True,
        )
        self.mock_px.nodes("pve1").qemu(200).snapshot.post.assert_called_once_with(
            snapname="snap", description="before kernel update", vmstate=1,
        )

    def test_rollback_vm(self):
        self.pve.rollback_vm("pve1", 200, "snap-name")
        self.mock_px.nodes("pve1").qemu(200).snapshot("snap-name").rollback.post.assert_called_once_with()

    def test_list_snapshots(self):
        self.mock_px.nodes("pve1").qemu(200).snapshot.get.return_value = [
            {"name": "snap1", "snaptime": 1700000000},
            {"name": "snap2", "snaptime": 1700100000},
        ]
        result = self.pve.list_snapshots("pve1", 200)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "snap1")


class TestProxmoxClientClone(unittest.TestCase):
    def setUp(self):
        self.mock_px = MagicMock()
        self.pve = pve_helpers.ProxmoxClient(self.mock_px)

    def test_clone_vm_full(self):
        self.pve.clone_vm("pve1", 100, 201, "web-server-01", full=True)
        self.mock_px.nodes("pve1").qemu(100).clone.post.assert_called_once_with(
            newid=201, name="web-server-01", full=1,
        )

    def test_clone_vm_linked(self):
        self.pve.clone_vm("pve1", 100, 201, "web-server-01", full=False)
        self.mock_px.nodes("pve1").qemu(100).clone.post.assert_called_once_with(
            newid=201, name="web-server-01", full=0,
        )


class TestProxmoxClientBulk(unittest.TestCase):
    def setUp(self):
        self.mock_px = MagicMock()
        self.pve = pve_helpers.ProxmoxClient(self.mock_px)

    def test_bulk_start_stopped_vms_only_starts_stopped(self):
        # The function returns the list of started VMIDs — that's the
        # primary verification. The 101 "running" VM should NOT appear in
        # the returned list (and therefore not have been started).
        self.mock_px.nodes("pve1").qemu.get.return_value = [
            {"vmid": 100, "name": "web", "status": "stopped"},
            {"vmid": 101, "name": "db", "status": "running"},
            {"vmid": 102, "name": "cache", "status": "stopped"},
        ]
        started = self.pve.bulk_start_stopped_vms("pve1")
        self.assertEqual(started, [100, 102])
        self.assertNotIn(101, started)
        self.assertEqual(len(started), 2)

    def test_bulk_start_all_running_returns_empty(self):
        self.mock_px.nodes("pve1").qemu.get.return_value = [
            {"vmid": 100, "name": "a", "status": "running"},
        ]
        self.assertEqual(self.pve.bulk_start_stopped_vms("pve1"), [])


class TestProxmoxClientResources(unittest.TestCase):
    def setUp(self):
        self.mock_px = MagicMock()
        self.pve = pve_helpers.ProxmoxClient(self.mock_px)

    def test_list_nodes(self):
        self.mock_px.nodes.get.return_value = [
            {"node": "pve1", "status": "online"},
            {"node": "pve2", "status": "online"},
        ]
        result = self.pve.list_nodes()
        self.assertEqual(len(result), 2)

    def test_list_vms(self):
        self.mock_px.nodes("pve1").qemu.get.return_value = [
            {"vmid": 100, "name": "web"},
        ]
        self.pve.list_vms("pve1")
        self.mock_px.nodes("pve1").qemu.get.assert_called_once_with()

    def test_list_containers(self):
        self.mock_px.nodes("pve1").lxc.get.return_value = [
            {"vmid": 200, "name": "ct"},
        ]
        result = self.pve.list_containers("pve1")
        self.assertEqual(len(result), 1)

    def test_get_vm_config(self):
        self.mock_px.nodes("pve1").qemu(200).config.get.return_value = {
            "name": "web", "cores": 4, "memory": 8192,
        }
        result = self.pve.get_vm_config("pve1", 200)
        self.assertEqual(result["cores"], 4)

    def test_get_cluster_resources_default_vm(self):
        self.pve.get_cluster_resources()
        self.mock_px.cluster.resources.get.assert_called_once_with(type="vm")

    def test_get_cluster_resources_custom_type(self):
        self.pve.get_cluster_resources(type_="node")
        self.mock_px.cluster.resources.get.assert_called_once_with(type="node")


if __name__ == "__main__":
    unittest.main(verbosity=2)

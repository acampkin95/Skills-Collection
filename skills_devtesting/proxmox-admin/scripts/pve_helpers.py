#!/usr/bin/env python3
"""
pve_helpers.py — Reusable Proxmox VE API client (wraps proxmoxer)

Usage:
    export PVE_HOST="pve.example.com"
    export PVE_TOKEN="root@pam!automation=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    from pve_helpers import ProxmoxClient
    pve = ProxmoxClient.from_env()
    pve.start_vm("pve", 200)

Or run directly for a quick cluster overview:
    python3 pve_helpers.py
"""

import os
import sys
from typing import Iterator

try:
    from proxmoxer import ProxmoxAPI
except ImportError:
    print("ERROR: proxmoxer library required. Install with: pip install proxmoxer requests", file=sys.stderr)
    sys.exit(1)


class ProxmoxClient:
    """Thin convenience wrapper over proxmoxer.ProxmoxAPI for common admin tasks."""

    def __init__(self, proxmox: ProxmoxAPI):
        self.px = proxmox

    @classmethod
    def from_env(cls) -> "ProxmoxClient":
        """Build from PVE_HOST + PVE_TOKEN env vars (USER@REALM!TOKENID=SECRET)."""
        host = os.environ.get("PVE_HOST")
        token = os.environ.get("PVE_TOKEN")
        if not host or not token:
            raise RuntimeError("Set PVE_HOST and PVE_TOKEN env vars")
        try:
            user_part, token_value = token.split("=", 1)
            user_realm, token_name = user_part.rsplit("!", 1)
        except ValueError as e:
            raise RuntimeError(f"PVE_TOKEN must be USER@REALM!TOKENID=SECRET, got: {token}") from e
        return cls(
            ProxmoxAPI(
                host,
                user=user_realm,
                token_name=token_name,
                token_value=token_value,
                verify_ssl=False,  # set True with valid cert
            )
        )

    # --- Cluster / nodes ---
    def list_nodes(self) -> list:
        return self.px.nodes.get()

    def list_vms(self, node: str) -> list:
        return self.px.nodes(node).qemu.get()

    def list_containers(self, node: str) -> list:
        return self.px.nodes(node).lxc.get()

    # --- VM lifecycle ---
    def start_vm(self, node: str, vmid: int) -> None:
        self.px.nodes(node).qemu(vmid).status.start.post()

    def stop_vm(self, node: str, vmid: int, force: bool = False) -> None:
        self.px.nodes(node).qemu(vmid).status.stop.post(force=int(force))

    def shutdown_vm(self, node: str, vmid: int, force: bool = False, timeout: int = 60) -> None:
        self.px.nodes(node).qemu(vmid).status.shutdown.post(force=int(force), timeout=timeout)

    def reboot_vm(self, node: str, vmid: int) -> None:
        self.px.nodes(node).qemu(vmid).status.reboot.post()

    def delete_vm(self, node: str, vmid: int, purge: bool = True) -> None:
        self.px.nodes(node).qemu(vmid).delete(purge=int(purge))

    # --- Snapshots ---
    def snapshot_vm(self, node: str, vmid: int, name: str, description: str = "", vmstate: bool = False) -> None:
        self.px.nodes(node).qemu(vmid).snapshot.post(
            snapname=name, description=description, vmstate=int(vmstate),
        )

    def rollback_vm(self, node: str, vmid: int, snapname: str) -> None:
        self.px.nodes(node).qemu(vmid).snapshot(snapname).rollback.post()

    def list_snapshots(self, node: str, vmid: int) -> list:
        return self.px.nodes(node).qemu(vmid).snapshot.get()

    # --- Cloning ---
    def clone_vm(self, node: str, src_vmid: int, new_vmid: int, name: str, full: bool = True) -> None:
        self.px.nodes(node).qemu(src_vmid).clone.post(
            newid=new_vmid, name=name, full=int(full),
        )

    # --- Resources ---
    def get_vm_config(self, node: str, vmid: int) -> dict:
        return self.px.nodes(node).qemu(vmid).config.get()

    def get_cluster_resources(self, type_: str = "vm") -> list:
        return self.px.cluster.resources.get(type=type_)

    # --- Bulk helpers ---
    def bulk_start_stopped_vms(self, node: str) -> list[int]:
        """Start all stopped VMs on a node. Returns list of VMIDs started."""
        started = []
        for vm in self.list_vms(node):
            if vm["status"] == "stopped":
                self.start_vm(node, vm["vmid"])
                started.append(vm["vmid"])
        return started


if __name__ == "__main__":
    # Quick smoke test: print cluster node + VM inventory
    pve = ProxmoxClient.from_env()
    print("Nodes:")
    for n in pve.list_nodes():
        print(f"  {n['node']:20s} status={n['status']} uptime={n.get('uptime', 0)}s")
    print("\nCluster VM inventory:")
    for res in pve.get_cluster_resources(type_="vm"):
        print(f"  vmid={res['vmid']:5d} name={res.get('name', '?'):30s} "
              f"node={res.get('node', '?'):10s} status={res['status']}")

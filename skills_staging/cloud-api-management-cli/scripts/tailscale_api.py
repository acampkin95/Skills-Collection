#!/usr/bin/env python3
"""
Tailscale API Management Script
Handles devices, DNS, keys, routes, ACLs, and tailnet management.
API key loaded from environment variables.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List
from datetime import datetime


class TailscaleAPI:
    """Tailscale REST API client."""
    
    BASE_URL = "https://api.tailscale.com/api/v2"
    
    def __init__(self, tailnet: str = "-"):
        self.api_key = os.environ.get("TAILSCALE_API_KEY")
        if not self.api_key:
            raise ValueError("TAILSCALE_API_KEY environment variable not set")
        self.tailnet = tailnet
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Tailscale API."""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        
        if data:
            headers["Content-Type"] = "application/json"
        
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 204:
                    return {"success": True}
                content = response.read().decode()
                if not content:
                    return {"success": True}
                return json.loads(content)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            try:
                return {"error": json.loads(error_body), "status": e.code}
            except:
                return {"error": error_body, "status": e.code}
    
    # === Device Operations ===
    
    def list_devices(self, fields: Optional[str] = None) -> Dict:
        """List all devices in the tailnet."""
        endpoint = f"/tailnet/{self.tailnet}/devices"
        if fields:
            endpoint += f"?fields={fields}"
        return self._request("GET", endpoint)
    
    def get_device(self, device_id: str) -> Dict:
        """Get device details by ID."""
        return self._request("GET", f"/device/{device_id}")
    
    def delete_device(self, device_id: str) -> Dict:
        """Delete a device from the tailnet."""
        return self._request("DELETE", f"/device/{device_id}")
    
    def authorize_device(self, device_id: str, authorized: bool = True) -> Dict:
        """Authorize or deauthorize a device."""
        return self._request("POST", f"/device/{device_id}/authorized", 
                            {"authorized": authorized})
    
    def set_device_tags(self, device_id: str, tags: List[str]) -> Dict:
        """Set tags on a device."""
        # Ensure tags have the 'tag:' prefix
        formatted_tags = [t if t.startswith("tag:") else f"tag:{t}" for t in tags]
        return self._request("POST", f"/device/{device_id}/tags", {"tags": formatted_tags})
    
    def set_device_key_expiry(self, device_id: str, disabled: bool) -> Dict:
        """Enable or disable key expiry for a device."""
        return self._request("POST", f"/device/{device_id}/key", 
                            {"keyExpiryDisabled": disabled})
    
    def get_device_routes(self, device_id: str) -> Dict:
        """Get routes advertised and enabled for a device."""
        return self._request("GET", f"/device/{device_id}/routes")
    
    def set_device_routes(self, device_id: str, routes: List[str]) -> Dict:
        """Enable routes for a device."""
        return self._request("POST", f"/device/{device_id}/routes", {"routes": routes})
    
    # === DNS Operations ===
    
    def get_dns_nameservers(self) -> Dict:
        """Get DNS nameservers for the tailnet."""
        return self._request("GET", f"/tailnet/{self.tailnet}/dns/nameservers")
    
    def set_dns_nameservers(self, dns: List[str]) -> Dict:
        """Set DNS nameservers for the tailnet."""
        return self._request("POST", f"/tailnet/{self.tailnet}/dns/nameservers", {"dns": dns})
    
    def get_dns_preferences(self) -> Dict:
        """Get DNS preferences for the tailnet."""
        return self._request("GET", f"/tailnet/{self.tailnet}/dns/preferences")
    
    def set_dns_preferences(self, magic_dns: bool) -> Dict:
        """Set DNS preferences (MagicDNS)."""
        return self._request("POST", f"/tailnet/{self.tailnet}/dns/preferences", 
                            {"magicDNS": magic_dns})
    
    def get_dns_searchpaths(self) -> Dict:
        """Get DNS search paths for the tailnet."""
        return self._request("GET", f"/tailnet/{self.tailnet}/dns/searchpaths")
    
    def set_dns_searchpaths(self, searchpaths: List[str]) -> Dict:
        """Set DNS search paths for the tailnet."""
        return self._request("POST", f"/tailnet/{self.tailnet}/dns/searchpaths", 
                            {"searchPaths": searchpaths})
    
    # === Auth Keys Operations ===
    
    def list_keys(self) -> Dict:
        """List all auth keys in the tailnet."""
        return self._request("GET", f"/tailnet/{self.tailnet}/keys")
    
    def get_key(self, key_id: str) -> Dict:
        """Get auth key details."""
        return self._request("GET", f"/tailnet/{self.tailnet}/keys/{key_id}")
    
    def create_key(self, reusable: bool = False, ephemeral: bool = False,
                   preauthorized: bool = True, expiry_seconds: int = 86400,
                   tags: Optional[List[str]] = None, description: str = "") -> Dict:
        """Create a new auth key."""
        data = {
            "capabilities": {
                "devices": {
                    "create": {
                        "reusable": reusable,
                        "ephemeral": ephemeral,
                        "preauthorized": preauthorized,
                        "tags": tags or []
                    }
                }
            },
            "expirySeconds": expiry_seconds,
            "description": description
        }
        return self._request("POST", f"/tailnet/{self.tailnet}/keys", data)
    
    def delete_key(self, key_id: str) -> Dict:
        """Delete an auth key."""
        return self._request("DELETE", f"/tailnet/{self.tailnet}/keys/{key_id}")
    
    # === ACL/Policy Operations ===
    
    def get_acl(self) -> Dict:
        """Get the ACL policy for the tailnet."""
        return self._request("GET", f"/tailnet/{self.tailnet}/acl")
    
    def set_acl(self, acl: Dict) -> Dict:
        """Set the ACL policy for the tailnet."""
        return self._request("POST", f"/tailnet/{self.tailnet}/acl", acl)
    
    def preview_acl(self, acl: Dict, type: str = "user", previewFor: str = "") -> Dict:
        """Preview ACL changes."""
        params = f"?type={type}"
        if previewFor:
            params += f"&previewFor={previewFor}"
        return self._request("POST", f"/tailnet/{self.tailnet}/acl/preview{params}", acl)
    
    def validate_acl(self, acl: Dict) -> Dict:
        """Validate ACL without applying."""
        return self._request("POST", f"/tailnet/{self.tailnet}/acl/validate", acl)
    
    # === Tailnet Operations ===
    
    def get_tailnet(self) -> Dict:
        """Get tailnet details."""
        return self._request("GET", f"/tailnet/{self.tailnet}")


def format_device(device: Dict[str, Any], verbose: bool = False) -> str:
    """Format device for display."""
    name = device.get("name", "Unknown")
    hostname = device.get("hostname", "")
    addresses = device.get("addresses", [])
    ip = addresses[0] if addresses else "N/A"
    os_type = device.get("os", "Unknown")
    last_seen = device.get("lastSeen", "Never")
    authorized = "✓" if device.get("authorized") else "✗"
    tags = ", ".join(device.get("tags", [])) or "None"
    
    if verbose:
        return (f"{name}\n"
                f"  ID: {device.get('id', 'N/A')}\n"
                f"  Hostname: {hostname}\n"
                f"  IP: {ip}\n"
                f"  OS: {os_type}\n"
                f"  Authorized: {authorized}\n"
                f"  Tags: {tags}\n"
                f"  Last Seen: {last_seen}\n"
                f"  Node Key: {device.get('nodeKey', 'N/A')[:20]}...")
    else:
        return f"{authorized} {name:<40} {ip:<20} {os_type:<15} {tags}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Tailscale API Management")
    parser.add_argument("--tailnet", "-t", default="-", 
                        help="Tailnet name (default: current)")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # === Device Commands ===
    devices_parser = subparsers.add_parser("devices", help="Device operations")
    devices_sub = devices_parser.add_subparsers(dest="action")
    
    # List devices
    devices_list = devices_sub.add_parser("list", help="List all devices")
    devices_list.add_argument("-v", "--verbose", action="store_true", 
                              help="Show detailed info")
    devices_list.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Get device
    devices_get = devices_sub.add_parser("get", help="Get device details")
    devices_get.add_argument("device_id", help="Device ID or name")
    
    # Delete device
    devices_delete = devices_sub.add_parser("delete", help="Delete a device")
    devices_delete.add_argument("device_id", help="Device ID")
    devices_delete.add_argument("-f", "--force", action="store_true", 
                                help="Skip confirmation")
    
    # Authorize device
    devices_auth = devices_sub.add_parser("authorize", help="Authorize/deauthorize device")
    devices_auth.add_argument("device_id", help="Device ID")
    devices_auth.add_argument("--disable", action="store_true", 
                              help="Deauthorize instead")
    
    # Set device tags
    devices_tags = devices_sub.add_parser("tags", help="Set device tags")
    devices_tags.add_argument("device_id", help="Device ID")
    devices_tags.add_argument("--tags", "-T", required=True, 
                              help="Comma-separated tags")
    
    # Get/Set routes
    devices_routes = devices_sub.add_parser("routes", help="Manage device routes")
    devices_routes.add_argument("device_id", help="Device ID")
    devices_routes.add_argument("--enable", help="Comma-separated routes to enable")
    
    # === DNS Commands ===
    dns_parser = subparsers.add_parser("dns", help="DNS operations")
    dns_sub = dns_parser.add_subparsers(dest="action")
    
    # Nameservers
    dns_ns = dns_sub.add_parser("nameservers", help="Manage nameservers")
    dns_ns.add_argument("--set", help="Comma-separated nameservers to set")
    
    # MagicDNS
    dns_magic = dns_sub.add_parser("magicdns", help="Toggle MagicDNS")
    dns_magic.add_argument("state", choices=["on", "off"], help="Enable or disable")
    
    # Search paths
    dns_search = dns_sub.add_parser("searchpaths", help="Manage search paths")
    dns_search.add_argument("--set", help="Comma-separated search paths to set")
    
    # === Keys Commands ===
    keys_parser = subparsers.add_parser("keys", help="Auth key operations")
    keys_sub = keys_parser.add_subparsers(dest="action")
    
    # List keys
    keys_list = keys_sub.add_parser("list", help="List auth keys")
    keys_list.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Create key
    keys_create = keys_sub.add_parser("create", help="Create auth key")
    keys_create.add_argument("--reusable", "-r", action="store_true", 
                             help="Make key reusable")
    keys_create.add_argument("--ephemeral", "-e", action="store_true", 
                             help="Make devices ephemeral")
    keys_create.add_argument("--no-preauth", action="store_true", 
                             help="Don't preauthorize")
    keys_create.add_argument("--expiry", "-x", type=int, default=86400,
                             help="Expiry in seconds (default: 86400)")
    keys_create.add_argument("--tags", "-T", help="Comma-separated tags")
    keys_create.add_argument("--description", "-d", default="", help="Key description")
    
    # Delete key
    keys_delete = keys_sub.add_parser("delete", help="Delete auth key")
    keys_delete.add_argument("key_id", help="Key ID")
    
    # === ACL Commands ===
    acl_parser = subparsers.add_parser("acl", help="ACL/Policy operations")
    acl_sub = acl_parser.add_subparsers(dest="action")
    
    # Get ACL
    acl_get = acl_sub.add_parser("get", help="Get current ACL policy")
    acl_get.add_argument("--output", "-o", help="Save to file")
    
    # Set ACL
    acl_set = acl_sub.add_parser("set", help="Set ACL policy from file")
    acl_set.add_argument("file", help="JSON file with ACL policy")
    
    # Validate ACL
    acl_validate = acl_sub.add_parser("validate", help="Validate ACL without applying")
    acl_validate.add_argument("file", help="JSON file with ACL policy")
    
    # === Tailnet Info ===
    info_parser = subparsers.add_parser("info", help="Get tailnet info")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        api = TailscaleAPI(args.tailnet)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # === Execute Commands ===
    
    if args.command == "devices":
        if args.action == "list":
            result = api.list_devices()
            if "error" in result:
                print(f"Error: {result}", file=sys.stderr)
                sys.exit(1)
            
            devices = result.get("devices", [])
            if args.json:
                print(json.dumps(devices, indent=2))
            else:
                print(f"Found {len(devices)} devices:\n")
                if not args.verbose:
                    print(f"{'':2} {'Name':<40} {'IP':<20} {'OS':<15} Tags")
                    print("-" * 90)
                for device in devices:
                    print(format_device(device, args.verbose))
        
        elif args.action == "get":
            result = api.get_device(args.device_id)
            print(json.dumps(result, indent=2))
        
        elif args.action == "delete":
            if not args.force:
                confirm = input(f"Delete device {args.device_id}? [y/N]: ")
                if confirm.lower() != "y":
                    print("Cancelled")
                    sys.exit(0)
            result = api.delete_device(args.device_id)
            if result.get("success") or "error" not in result:
                print(f"Device {args.device_id} deleted")
            else:
                print(f"Error: {result}")
        
        elif args.action == "authorize":
            result = api.authorize_device(args.device_id, not args.disable)
            action = "deauthorized" if args.disable else "authorized"
            if "error" not in result:
                print(f"Device {args.device_id} {action}")
            else:
                print(f"Error: {result}")
        
        elif args.action == "tags":
            tags = [t.strip() for t in args.tags.split(",")]
            result = api.set_device_tags(args.device_id, tags)
            if "error" not in result:
                print(f"Tags updated for {args.device_id}: {tags}")
            else:
                print(f"Error: {result}")
        
        elif args.action == "routes":
            if args.enable:
                routes = [r.strip() for r in args.enable.split(",")]
                result = api.set_device_routes(args.device_id, routes)
                if "error" not in result:
                    print(f"Routes enabled: {routes}")
                else:
                    print(f"Error: {result}")
            else:
                result = api.get_device_routes(args.device_id)
                print(json.dumps(result, indent=2))
        
        else:
            devices_parser.print_help()
    
    elif args.command == "dns":
        if args.action == "nameservers":
            if args.set:
                servers = [s.strip() for s in args.set.split(",")]
                result = api.set_dns_nameservers(servers)
            else:
                result = api.get_dns_nameservers()
            print(json.dumps(result, indent=2))
        
        elif args.action == "magicdns":
            enabled = args.state == "on"
            result = api.set_dns_preferences(enabled)
            if "error" not in result:
                print(f"MagicDNS {'enabled' if enabled else 'disabled'}")
            else:
                print(f"Error: {result}")
        
        elif args.action == "searchpaths":
            if args.set:
                paths = [p.strip() for p in args.set.split(",")]
                result = api.set_dns_searchpaths(paths)
            else:
                result = api.get_dns_searchpaths()
            print(json.dumps(result, indent=2))
        
        else:
            dns_parser.print_help()
    
    elif args.command == "keys":
        if args.action == "list":
            result = api.list_keys()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                keys = result.get("keys", [])
                print(f"Found {len(keys)} keys:\n")
                for key in keys:
                    key_id = key.get("id", "N/A")
                    desc = key.get("description", "")
                    expires = key.get("expires", "Never")
                    reusable = "Reusable" if key.get("capabilities", {}).get(
                        "devices", {}).get("create", {}).get("reusable") else "Single-use"
                    print(f"  {key_id}: {desc} ({reusable}, expires: {expires})")
        
        elif args.action == "create":
            tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
            result = api.create_key(
                reusable=args.reusable,
                ephemeral=args.ephemeral,
                preauthorized=not args.no_preauth,
                expiry_seconds=args.expiry,
                tags=tags,
                description=args.description
            )
            if "key" in result:
                print(f"Created auth key: {result['key']}")
                print(f"Key ID: {result.get('id', 'N/A')}")
                print(f"Expires: {result.get('expires', 'N/A')}")
            else:
                print(f"Error: {result}")
        
        elif args.action == "delete":
            result = api.delete_key(args.key_id)
            if result.get("success") or "error" not in result:
                print(f"Key {args.key_id} deleted")
            else:
                print(f"Error: {result}")
        
        else:
            keys_parser.print_help()
    
    elif args.command == "acl":
        if args.action == "get":
            result = api.get_acl()
            output = json.dumps(result, indent=2)
            if args.output:
                with open(args.output, "w") as f:
                    f.write(output)
                print(f"ACL saved to {args.output}")
            else:
                print(output)
        
        elif args.action == "set":
            with open(args.file) as f:
                acl = json.load(f)
            result = api.set_acl(acl)
            if "error" not in result:
                print("ACL updated successfully")
            else:
                print(f"Error: {result}")
        
        elif args.action == "validate":
            with open(args.file) as f:
                acl = json.load(f)
            result = api.validate_acl(acl)
            if "error" not in result:
                print("ACL is valid")
            else:
                print(f"Validation errors: {result}")
        
        else:
            acl_parser.print_help()
    
    elif args.command == "info":
        result = api.get_tailnet()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

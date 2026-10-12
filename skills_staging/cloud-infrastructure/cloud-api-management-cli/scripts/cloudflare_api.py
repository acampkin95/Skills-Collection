#!/usr/bin/env python3
"""
Cloudflare API Management Script
Handles DNS, zones, firewall, cache, workers, and analytics operations.
Credentials loaded from environment variables.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


class CloudflareAPI:
    """Cloudflare API client with support for common operations."""
    
    BASE_URL = "https://api.cloudflare.com/client/v4"
    
    def __init__(self):
        self.api_key = os.environ.get("CLOUDFLARE_API_KEY")
        self.account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        self.zone_id = os.environ.get("CLOUDFLARE_ZONE_ID")
        
        if not self.api_key:
            raise ValueError("CLOUDFLARE_API_KEY environment variable not set")
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Cloudflare API."""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            try:
                error_json = json.loads(error_body)
                return error_json
            except:
                return {"success": False, "errors": [{"message": error_body}]}
    
    # === DNS Operations ===
    
    def dns_list(self, zone_id: Optional[str] = None) -> Dict:
        """List all DNS records for a zone."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required - set CLOUDFLARE_ZONE_ID or pass --zone")
        return self._request("GET", f"/zones/{zid}/dns_records")
    
    def dns_create(self, record_type: str, name: str, content: str, 
                   ttl: int = 1, proxied: bool = False, zone_id: Optional[str] = None) -> Dict:
        """Create a new DNS record."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        
        data = {
            "type": record_type.upper(),
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": proxied
        }
        return self._request("POST", f"/zones/{zid}/dns_records", data)
    
    def dns_update(self, record_id: str, record_type: str, name: str, content: str,
                   ttl: int = 1, proxied: bool = False, zone_id: Optional[str] = None) -> Dict:
        """Update an existing DNS record."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        
        data = {
            "type": record_type.upper(),
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": proxied
        }
        return self._request("PUT", f"/zones/{zid}/dns_records/{record_id}", data)
    
    def dns_delete(self, record_id: str, zone_id: Optional[str] = None) -> Dict:
        """Delete a DNS record."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("DELETE", f"/zones/{zid}/dns_records/{record_id}")
    
    # === Zone Operations ===
    
    def zones_list(self) -> Dict:
        """List all zones in the account."""
        return self._request("GET", "/zones")
    
    def zone_get(self, zone_id: Optional[str] = None) -> Dict:
        """Get details for a specific zone."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("GET", f"/zones/{zid}")
    
    def zone_settings(self, zone_id: Optional[str] = None) -> Dict:
        """Get all settings for a zone."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("GET", f"/zones/{zid}/settings")
    
    # === Cache Operations ===
    
    def cache_purge_all(self, zone_id: Optional[str] = None) -> Dict:
        """Purge all cached content for a zone."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("POST", f"/zones/{zid}/purge_cache", {"purge_everything": True})
    
    def cache_purge_urls(self, urls: List[str], zone_id: Optional[str] = None) -> Dict:
        """Purge specific URLs from cache."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("POST", f"/zones/{zid}/purge_cache", {"files": urls})
    
    def cache_purge_tags(self, tags: List[str], zone_id: Optional[str] = None) -> Dict:
        """Purge cache by tags (Enterprise only)."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("POST", f"/zones/{zid}/purge_cache", {"tags": tags})
    
    # === Firewall Operations ===
    
    def firewall_rules_list(self, zone_id: Optional[str] = None) -> Dict:
        """List all firewall rules."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("GET", f"/zones/{zid}/firewall/rules")
    
    def firewall_access_rules_list(self, zone_id: Optional[str] = None) -> Dict:
        """List IP access rules."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("GET", f"/zones/{zid}/firewall/access_rules/rules")
    
    def firewall_block_ip(self, ip: str, notes: str = "", zone_id: Optional[str] = None) -> Dict:
        """Block an IP address."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        
        data = {
            "mode": "block",
            "configuration": {"target": "ip", "value": ip},
            "notes": notes
        }
        return self._request("POST", f"/zones/{zid}/firewall/access_rules/rules", data)
    
    def firewall_allow_ip(self, ip: str, notes: str = "", zone_id: Optional[str] = None) -> Dict:
        """Whitelist an IP address."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        
        data = {
            "mode": "whitelist",
            "configuration": {"target": "ip", "value": ip},
            "notes": notes
        }
        return self._request("POST", f"/zones/{zid}/firewall/access_rules/rules", data)
    
    # === Workers Operations ===
    
    def workers_list(self) -> Dict:
        """List all Workers scripts."""
        if not self.account_id:
            raise ValueError("CLOUDFLARE_ACCOUNT_ID required for Workers operations")
        return self._request("GET", f"/accounts/{self.account_id}/workers/scripts")
    
    def worker_get(self, script_name: str) -> Dict:
        """Get a Worker script."""
        if not self.account_id:
            raise ValueError("CLOUDFLARE_ACCOUNT_ID required")
        return self._request("GET", f"/accounts/{self.account_id}/workers/scripts/{script_name}")
    
    def workers_routes_list(self, zone_id: Optional[str] = None) -> Dict:
        """List Worker routes for a zone."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("GET", f"/zones/{zid}/workers/routes")
    
    # === Analytics Operations ===
    
    def analytics_dashboard(self, since_minutes: int = -1440, zone_id: Optional[str] = None) -> Dict:
        """Get zone analytics for dashboard."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("GET", f"/zones/{zid}/analytics/dashboard?since={since_minutes}")
    
    # === Page Rules ===
    
    def page_rules_list(self, zone_id: Optional[str] = None) -> Dict:
        """List all page rules."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("GET", f"/zones/{zid}/pagerules")
    
    # === SSL/TLS ===
    
    def ssl_settings(self, zone_id: Optional[str] = None) -> Dict:
        """Get SSL/TLS settings."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("GET", f"/zones/{zid}/settings/ssl")
    
    def ssl_certificate_packs(self, zone_id: Optional[str] = None) -> Dict:
        """List SSL certificate packs."""
        zid = zone_id or self.zone_id
        if not zid:
            raise ValueError("Zone ID required")
        return self._request("GET", f"/zones/{zid}/ssl/certificate_packs")


def format_output(data: Dict[str, Any], as_json: bool = False) -> str:
    """Format API response for display."""
    if as_json:
        return json.dumps(data, indent=2)
    
    if not data.get("success", False):
        errors = data.get("errors", [])
        return f"Error: {errors[0].get('message', 'Unknown error')}" if errors else "Unknown error"
    
    result = data.get("result", data)
    if isinstance(result, list):
        return json.dumps(result, indent=2)
    return json.dumps(result, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cloudflare API Management")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--zone", help="Override zone ID")
    
    subparsers = parser.add_subparsers(dest="command", help="Command category")
    
    # DNS commands
    dns_parser = subparsers.add_parser("dns", help="DNS record management")
    dns_sub = dns_parser.add_subparsers(dest="action")
    
    dns_sub.add_parser("list", help="List DNS records")
    
    dns_create = dns_sub.add_parser("create", help="Create DNS record")
    dns_create.add_argument("--type", required=True, help="Record type (A, AAAA, CNAME, TXT, MX, etc)")
    dns_create.add_argument("--name", required=True, help="Record name")
    dns_create.add_argument("--content", required=True, help="Record content/value")
    dns_create.add_argument("--ttl", type=int, default=1, help="TTL (1=auto)")
    dns_create.add_argument("--proxied", action="store_true", help="Enable Cloudflare proxy")
    
    dns_update = dns_sub.add_parser("update", help="Update DNS record")
    dns_update.add_argument("--id", required=True, help="Record ID")
    dns_update.add_argument("--type", required=True, help="Record type")
    dns_update.add_argument("--name", required=True, help="Record name")
    dns_update.add_argument("--content", required=True, help="Record content")
    dns_update.add_argument("--ttl", type=int, default=1, help="TTL")
    dns_update.add_argument("--proxied", action="store_true", help="Enable proxy")
    
    dns_delete = dns_sub.add_parser("delete", help="Delete DNS record")
    dns_delete.add_argument("--id", required=True, help="Record ID to delete")
    
    # Zone commands
    zone_parser = subparsers.add_parser("zones", help="Zone management")
    zone_sub = zone_parser.add_subparsers(dest="action")
    zone_sub.add_parser("list", help="List all zones")
    zone_sub.add_parser("get", help="Get zone details")
    zone_sub.add_parser("settings", help="Get zone settings")
    
    # Cache commands
    cache_parser = subparsers.add_parser("cache", help="Cache management")
    cache_sub = cache_parser.add_subparsers(dest="action")
    
    cache_purge = cache_sub.add_parser("purge", help="Purge cache")
    cache_purge.add_argument("--all", action="store_true", help="Purge everything")
    cache_purge.add_argument("--urls", help="Comma-separated URLs to purge")
    cache_purge.add_argument("--tags", help="Comma-separated tags to purge")
    
    # Firewall commands
    fw_parser = subparsers.add_parser("firewall", help="Firewall management")
    fw_sub = fw_parser.add_subparsers(dest="action")
    fw_sub.add_parser("list", help="List firewall rules")
    fw_sub.add_parser("access", help="List IP access rules")
    
    fw_block = fw_sub.add_parser("block", help="Block IP")
    fw_block.add_argument("--ip", required=True, help="IP to block")
    fw_block.add_argument("--notes", default="", help="Notes")
    
    fw_allow = fw_sub.add_parser("allow", help="Allow IP")
    fw_allow.add_argument("--ip", required=True, help="IP to allow")
    fw_allow.add_argument("--notes", default="", help="Notes")
    
    # Workers commands
    workers_parser = subparsers.add_parser("workers", help="Workers management")
    workers_sub = workers_parser.add_subparsers(dest="action")
    workers_sub.add_parser("list", help="List Workers")
    workers_sub.add_parser("routes", help="List Worker routes")
    
    worker_get = workers_sub.add_parser("get", help="Get Worker")
    worker_get.add_argument("--name", required=True, help="Script name")
    
    # Analytics commands
    analytics_parser = subparsers.add_parser("analytics", help="Get analytics")
    analytics_parser.add_argument("--since", type=int, default=-1440, help="Minutes ago (negative)")
    
    # Page rules
    pagerules_parser = subparsers.add_parser("pagerules", help="Page rules management")
    pagerules_sub = pagerules_parser.add_subparsers(dest="action")
    pagerules_sub.add_parser("list", help="List page rules")
    
    # SSL commands
    ssl_parser = subparsers.add_parser("ssl", help="SSL/TLS management")
    ssl_sub = ssl_parser.add_subparsers(dest="action")
    ssl_sub.add_parser("settings", help="Get SSL settings")
    ssl_sub.add_parser("certs", help="List certificate packs")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        cf = CloudflareAPI()
        zone_id = args.zone if hasattr(args, 'zone') and args.zone else None
        result = None
        
        if args.command == "dns":
            if args.action == "list":
                result = cf.dns_list(zone_id)
            elif args.action == "create":
                result = cf.dns_create(args.type, args.name, args.content, args.ttl, args.proxied, zone_id)
            elif args.action == "update":
                result = cf.dns_update(args.id, args.type, args.name, args.content, args.ttl, args.proxied, zone_id)
            elif args.action == "delete":
                result = cf.dns_delete(args.id, zone_id)
        
        elif args.command == "zones":
            if args.action == "list":
                result = cf.zones_list()
            elif args.action == "get":
                result = cf.zone_get(zone_id)
            elif args.action == "settings":
                result = cf.zone_settings(zone_id)
        
        elif args.command == "cache":
            if args.action == "purge":
                if args.all:
                    result = cf.cache_purge_all(zone_id)
                elif args.urls:
                    result = cf.cache_purge_urls(args.urls.split(","), zone_id)
                elif args.tags:
                    result = cf.cache_purge_tags(args.tags.split(","), zone_id)
        
        elif args.command == "firewall":
            if args.action == "list":
                result = cf.firewall_rules_list(zone_id)
            elif args.action == "access":
                result = cf.firewall_access_rules_list(zone_id)
            elif args.action == "block":
                result = cf.firewall_block_ip(args.ip, args.notes, zone_id)
            elif args.action == "allow":
                result = cf.firewall_allow_ip(args.ip, args.notes, zone_id)
        
        elif args.command == "workers":
            if args.action == "list":
                result = cf.workers_list()
            elif args.action == "get":
                result = cf.worker_get(args.name)
            elif args.action == "routes":
                result = cf.workers_routes_list(zone_id)
        
        elif args.command == "analytics":
            result = cf.analytics_dashboard(args.since, zone_id)
        
        elif args.command == "pagerules":
            if args.action == "list":
                result = cf.page_rules_list(zone_id)
        
        elif args.command == "ssl":
            if args.action == "settings":
                result = cf.ssl_settings(zone_id)
            elif args.action == "certs":
                result = cf.ssl_certificate_packs(zone_id)
        
        if result:
            print(format_output(result, args.json))
            sys.exit(0 if result.get("success", False) else 1)
        else:
            parser.print_help()
            sys.exit(1)
            
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

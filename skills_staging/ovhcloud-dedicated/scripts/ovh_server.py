#!/usr/bin/env python3
"""
OVHcloud Dedicated Server Management CLI

All-in-one tool for remote administration of OVH dedicated servers via the REST API.
Covers server lifecycle, IPMI/KVM, network, firewall, OS installation, and monitoring.

Usage:
    python3 ovh_server.py <command> [SERVER_NAME] [options]

Requires: pip install ovh
Credentials: ~/.config/ovh.conf or OVH_* environment variables
"""

import argparse
import json
import sys
import time
import textwrap
from datetime import datetime

try:
    import ovh
except ImportError:
    print("ERROR: 'ovh' package not installed. Run: pip install ovh --break-system-packages")
    sys.exit(1)

# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def get_client() -> ovh.Client:
    """Create OVH API client from config file or environment variables."""
    try:
        return ovh.Client()
    except Exception as e:
        print(f"ERROR: Failed to initialise OVH client: {e}")
        print("Ensure ~/.config/ovh.conf exists or OVH_* env vars are set.")
        print("See: https://eu.api.ovh.com/createToken/")
        sys.exit(1)


def pp(data, indent: int = 2) -> None:
    """Pretty-print JSON data."""
    print(json.dumps(data, indent=indent, default=str))


def confirm(msg: str) -> bool:
    """Prompt user for yes/no confirmation."""
    resp = input(f"{msg} [y/N]: ").strip().lower()
    return resp in ("y", "yes")


def get_public_ip() -> str:
    """Detect public IP via OVH's ifconfig service."""
    import urllib.request
    try:
        return urllib.request.urlopen("https://ifconfig.ovh", timeout=10).read().decode().strip()
    except Exception:
        try:
            return urllib.request.urlopen("https://api.ipify.org", timeout=10).read().decode().strip()
        except Exception:
            return ""


def wait_for_task(client: ovh.Client, server: str, task_id: int, timeout: int = 600) -> bool:
    """Poll a server task until completion or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        task = client.get(f"/dedicated/server/{server}/task/{task_id}")
        status = task.get("status", "unknown")
        print(f"  Task {task_id}: {status} ({task.get('function', 'unknown')})")
        if status == "done":
            return True
        if status in ("error", "cancelled"):
            print(f"  Task failed: {task.get('comment', 'no details')}")
            return False
        time.sleep(10)
    print(f"  Timeout after {timeout}s waiting for task {task_id}")
    return False


# ──────────────────────────────────────────────────────────────
# Commands: Server Discovery & Info
# ──────────────────────────────────────────────────────────────

def cmd_list(client: ovh.Client, args: argparse.Namespace) -> None:
    """List all dedicated servers on the account."""
    servers = client.get("/dedicated/server")
    if not servers:
        print("No dedicated servers found on this account.")
        return
    print(f"Found {len(servers)} server(s):\n")
    for name in servers:
        try:
            info = client.get(f"/dedicated/server/{name}")
            state = info.get("state", "?")
            dc = info.get("datacenter", "?")
            os_val = info.get("os", "?")
            display = info.get("name", name)
            ip = info.get("ip", "?")
            print(f"  {name}")
            print(f"    Display: {display}  |  IP: {ip}  |  DC: {dc}  |  State: {state}  |  OS: {os_val}")
        except Exception as e:
            print(f"  {name}  (error fetching details: {e})")
    print()


def cmd_info(client: ovh.Client, args: argparse.Namespace) -> None:
    """Get full server details."""
    info = client.get(f"/dedicated/server/{args.server}")
    pp(info)


def cmd_hardware(client: ovh.Client, args: argparse.Namespace) -> None:
    """Get hardware specifications."""
    hw = client.get(f"/dedicated/server/{args.server}/specifications/hardware")
    pp(hw)


def cmd_service(client: ovh.Client, args: argparse.Namespace) -> None:
    """Get service information (billing, expiry)."""
    svc = client.get(f"/dedicated/server/{args.server}/serviceInfos")
    pp(svc)


# ──────────────────────────────────────────────────────────────
# Commands: Power & Boot
# ──────────────────────────────────────────────────────────────

def cmd_reboot(client: ovh.Client, args: argparse.Namespace) -> None:
    """Reboot the server (soft or hard)."""
    if args.hard:
        print(f"Hard rebooting {args.server} (forced power cycle via IPMI)...")
        if not confirm("This may cause data loss. Continue?"):
            return
        task = client.post(f"/dedicated/server/{args.server}/reboot")
    else:
        print(f"Soft rebooting {args.server}...")
        task = client.post(f"/dedicated/server/{args.server}/reboot")
    print(f"Reboot task created: {task.get('taskId', 'unknown')}")
    pp(task)


def cmd_rescue(client: ovh.Client, args: argparse.Namespace) -> None:
    """Enable or disable rescue mode."""
    if args.enable:
        # Find the rescue boot option
        boots = client.get(f"/dedicated/server/{args.server}/boot", bootType="rescue")
        if not boots:
            print("No rescue boot option available for this server.")
            return
        boot_id = boots[0]
        print(f"Enabling rescue mode (boot ID: {boot_id})...")
        client.put(f"/dedicated/server/{args.server}", bootId=boot_id)
        print("Rescue mode enabled. Reboot the server to enter rescue.")
        print("Credentials will be sent to your account email.")
    elif args.disable:
        # Find the normal/harddisk boot option
        boots = client.get(f"/dedicated/server/{args.server}/boot", bootType="harddisk")
        if not boots:
            print("No harddisk boot option found.")
            return
        boot_id = boots[0]
        print(f"Disabling rescue mode (restoring boot ID: {boot_id})...")
        client.put(f"/dedicated/server/{args.server}", bootId=boot_id)
        print("Normal boot restored. Reboot to exit rescue.")
    else:
        print("Specify --enable or --disable")


def cmd_boot(client: ovh.Client, args: argparse.Namespace) -> None:
    """Manage boot configuration."""
    if args.list_boots:
        boots = client.get(f"/dedicated/server/{args.server}/boot")
        print(f"Available boot options for {args.server}:\n")
        for bid in boots:
            detail = client.get(f"/dedicated/server/{args.server}/boot/{bid}")
            print(f"  ID: {bid}")
            print(f"    Type: {detail.get('bootType', '?')}  |  Kernel: {detail.get('kernel', '?')}")
            print(f"    Description: {detail.get('description', '?')}")
            print()
    elif args.set_boot:
        print(f"Setting boot ID to {args.set_boot}...")
        client.put(f"/dedicated/server/{args.server}", bootId=int(args.set_boot))
        print("Boot ID updated. Reboot to apply.")
    elif args.current:
        info = client.get(f"/dedicated/server/{args.server}")
        boot_id = info.get("bootId")
        if boot_id:
            detail = client.get(f"/dedicated/server/{args.server}/boot/{boot_id}")
            print(f"Current boot: ID {boot_id}")
            pp(detail)
        else:
            print("No boot ID set.")
    else:
        print("Specify --list, --set BOOT_ID, or --current")


# ──────────────────────────────────────────────────────────────
# Commands: IPMI / KVM
# ──────────────────────────────────────────────────────────────

def cmd_ipmi(client: ovh.Client, args: argparse.Namespace) -> None:
    """IPMI / KVM console management."""
    server = args.server

    if args.test:
        try:
            result = client.get(f"/dedicated/server/{server}/features/ipmi")
            print("IPMI status:")
            pp(result)
        except ovh.exceptions.ResourceNotFoundError:
            print("IPMI is not available on this server.")
        return

    if args.reset:
        print("Resetting IPMI interface (this takes several minutes)...")
        task = client.post(f"/dedicated/server/{server}/features/ipmi/resetInterface")
        print("IPMI reset initiated.")
        pp(task)
        return

    # Determine IP for whitelisting
    ip = args.ip or get_public_ip()
    if not ip:
        print("ERROR: Could not detect public IP. Pass --ip YOUR_IP")
        return
    print(f"Using IP for IPMI access: {ip}")

    ttl = getattr(args, "ttl", 15)

    if args.kvm_html:
        access_type = "kvmipHtml5URL"
    elif args.kvm_java:
        access_type = "kvmipJnlp"
    elif args.sol_ssh:
        access_type = "serialOverLanSshKey"
    elif args.sol_web:
        access_type = "serialOverLanURL"
    else:
        print("Specify --test, --reset, --kvm-html, --kvm-java, --sol-ssh, or --sol-web")
        return

    print(f"Requesting {access_type} access (TTL: {ttl} min)...")
    try:
        client.post(
            f"/dedicated/server/{server}/features/ipmi/access",
            ipToAllow=ip,
            ttl=ttl,
            type=access_type,
        )
    except ovh.exceptions.BadParametersError as e:
        print(f"Error requesting access: {e}")
        return

    # Poll for the access URL
    print("Waiting for access URL...", end="", flush=True)
    for _ in range(30):
        time.sleep(2)
        print(".", end="", flush=True)
        try:
            result = client.get(
                f"/dedicated/server/{server}/features/ipmi/access",
                type=access_type,
            )
            value = result.get("value")
            if value:
                print(f"\n\nAccess URL/Key:\n{value}\n")
                return
        except Exception:
            pass
    print("\nTimeout waiting for IPMI access. Try again or reset IPMI.")


# ──────────────────────────────────────────────────────────────
# Commands: OS Installation
# ──────────────────────────────────────────────────────────────

def cmd_os(client: ovh.Client, args: argparse.Namespace) -> None:
    """OS template listing and installation."""
    server = args.server

    if args.list_os:
        templates = client.get(f"/dedicated/server/{server}/install/compatibleTemplates")
        print("Compatible OS templates:\n")
        for category in sorted(templates.keys()):
            items = templates[category]
            if items:
                print(f"  [{category}]")
                for t in sorted(items):
                    print(f"    - {t}")
                print()
        return

    if args.list_ovh:
        templates = client.get(f"/dedicated/server/{server}/install/compatibleTemplates")
        ovh_templates = templates.get("ovh", [])
        print("OVH templates:\n")
        for t in sorted(ovh_templates):
            print(f"  - {t}")
        return

    if args.install:
        template = args.install
        print(f"WARNING: This will WIPE ALL DATA on {server} and install {template}.")
        if not confirm("Are you absolutely sure?"):
            return

        details = {"customHostname": args.hostname} if args.hostname else {}
        if args.ssh_key:
            details["sshKeyName"] = args.ssh_key

        body = {
            "templateName": template,
            "details": details,
        }

        print(f"Starting OS installation: {template}...")
        try:
            task = client.post(f"/dedicated/server/{server}/install/start", **body)
            print(f"Install task created:")
            pp(task)
            print("\nMonitor progress with: ovh_server.py tasks SERVER_NAME")
        except Exception as e:
            print(f"Install failed: {e}")
        return

    print("Specify --list, --list-ovh, or --install TEMPLATE")


# ──────────────────────────────────────────────────────────────
# Commands: Network & IP
# ──────────────────────────────────────────────────────────────

def cmd_ip(client: ovh.Client, args: argparse.Namespace) -> None:
    """IP address management."""
    server = args.server

    if args.list_ips:
        ips = client.get(f"/dedicated/server/{server}/ips")
        print(f"IPs assigned to {server}:\n")
        for ip in ips:
            print(f"  {ip}")
        return

    if args.detail:
        ip_block = args.detail
        info = client.get(f"/ip/{ip_block.replace('/', '%2F')}")
        pp(info)
        return

    if args.reverse:
        ip_addr = args.reverse
        ip_block = ip_addr  # For single IPs, the block is the IP itself
        if args.delete:
            print(f"Deleting reverse DNS for {ip_addr}...")
            client.delete(f"/ip/{ip_block.replace('/', '%2F')}/reverse/{ip_addr}")
            print("Reverse DNS deleted.")
        elif args.value:
            print(f"Setting reverse DNS for {ip_addr} to {args.value}...")
            client.post(
                f"/ip/{ip_block.replace('/', '%2F')}/reverse",
                ipReverse=ip_addr,
                reverse=args.value,
            )
            print("Reverse DNS set.")
        else:
            # Get current reverse
            try:
                rev = client.get(f"/ip/{ip_block.replace('/', '%2F')}/reverse/{ip_addr}")
                pp(rev)
            except Exception:
                print(f"No reverse DNS set for {ip_addr}")
        return

    print("Specify --list, --detail IP, or --reverse IP [--value HOST | --delete]")


def cmd_network(client: ovh.Client, args: argparse.Namespace) -> None:
    """Network interfaces and bandwidth stats."""
    server = args.server

    if args.interfaces:
        try:
            ifaces = client.get(f"/dedicated/server/{server}/networkInterfaceController")
            print(f"Network interfaces for {server}:\n")
            for mac in ifaces:
                detail = client.get(f"/dedicated/server/{server}/networkInterfaceController/{mac}")
                print(f"  MAC: {mac}")
                pp(detail)
                print()
        except Exception as e:
            print(f"Could not retrieve interfaces: {e}")
        return

    if args.bandwidth:
        try:
            bw = client.get(f"/dedicated/server/{server}/specifications/network")
            print(f"Network specifications for {server}:")
            pp(bw)
        except Exception as e:
            print(f"Could not retrieve bandwidth info: {e}")
        return

    if args.traffic:
        try:
            # Get OVH bandwidth stats
            period = args.period or "daily"
            stats = client.get(
                f"/dedicated/server/{server}/statistics/chart",
                period=period,
                type="traffic:download",
            )
            print(f"Traffic stats ({period}):")
            pp(stats)
        except Exception as e:
            print(f"Could not retrieve traffic stats: {e}")
        return

    print("Specify --interfaces, --bandwidth, or --traffic")


# ──────────────────────────────────────────────────────────────
# Commands: Firewall
# ──────────────────────────────────────────────────────────────

def cmd_firewall(client: ovh.Client, args: argparse.Namespace) -> None:
    """OVH network firewall management."""
    ip_block = args.ip_block.replace("/", "%2F")
    ip_addr = args.ip_block.split("/")[0]  # Base IP without mask

    if args.enable_fw:
        print(f"Enabling firewall on {args.ip_block}...")
        client.post(f"/ip/{ip_block}/firewall", ipOnFirewall=ip_addr)
        print("Firewall enabled.")
        return

    if args.disable_fw:
        print(f"Disabling firewall on {args.ip_block}...")
        client.delete(f"/ip/{ip_block}/firewall/{ip_addr}")
        print("Firewall disabled.")
        return

    if args.list_rules:
        rules = client.get(f"/ip/{ip_block}/firewall/{ip_addr}/rule")
        print(f"Firewall rules for {args.ip_block}:\n")
        for seq in sorted(rules):
            rule = client.get(f"/ip/{ip_block}/firewall/{ip_addr}/rule/{seq}")
            action = rule.get("action", "?")
            proto = rule.get("protocol", "?")
            src = rule.get("source", "?")
            dst_port = rule.get("destinationPort", "any")
            print(f"  [{seq}] {action.upper():8s} {proto:6s} src={src} dst_port={dst_port}")
        return

    if args.rule_detail is not None:
        rule = client.get(f"/ip/{ip_block}/firewall/{ip_addr}/rule/{args.rule_detail}")
        pp(rule)
        return

    if args.add_rule:
        body = {
            "sequence": args.sequence,
            "action": args.action,
            "protocol": args.protocol,
        }
        if args.source:
            body["source"] = args.source
        if args.dest_port:
            body["destinationPort"] = args.dest_port
        if args.source_port:
            body["sourcePort"] = args.source_port

        print(f"Adding firewall rule (seq {args.sequence})...")
        result = client.post(f"/ip/{ip_block}/firewall/{ip_addr}/rule", **body)
        pp(result)
        return

    if args.remove_rule is not None:
        print(f"Removing firewall rule {args.remove_rule}...")
        client.delete(f"/ip/{ip_block}/firewall/{ip_addr}/rule/{args.remove_rule}")
        print("Rule removed.")
        return

    if args.mitigation:
        if args.mitigation == "on":
            print(f"Enabling anti-DDoS mitigation on {ip_addr}...")
            client.post(f"/ip/{ip_block}/mitigation", ipOnMitigation=ip_addr)
        else:
            print(f"Disabling anti-DDoS mitigation on {ip_addr}...")
            client.delete(f"/ip/{ip_block}/mitigation/{ip_addr}")
        print("Done.")
        return

    print("Specify --list, --rule SEQ, --add, --remove SEQ, --enable, --disable, or --mitigation on|off")


# ──────────────────────────────────────────────────────────────
# Commands: Monitoring
# ──────────────────────────────────────────────────────────────

def cmd_monitoring(client: ovh.Client, args: argparse.Namespace) -> None:
    """Server monitoring management."""
    server = args.server

    if args.enable_mon:
        print(f"Enabling OVH monitoring on {server}...")
        client.put(f"/dedicated/server/{server}", monitoring=True)
        print("Monitoring enabled.")
        return

    if args.disable_mon:
        print(f"Disabling OVH monitoring on {server}...")
        client.put(f"/dedicated/server/{server}", monitoring=False)
        print("Monitoring disabled.")
        return

    if args.alerts:
        try:
            notifs = client.get(f"/dedicated/server/{server}/serviceMonitoring")
            print(f"Monitoring services for {server}:")
            for mid in notifs:
                detail = client.get(f"/dedicated/server/{server}/serviceMonitoring/{mid}")
                pp(detail)
                print()
        except Exception as e:
            print(f"Could not retrieve alerts: {e}")
        return

    # Default: show status
    info = client.get(f"/dedicated/server/{server}")
    print(f"Monitoring status for {server}:")
    print(f"  Enabled: {info.get('monitoring', 'unknown')}")
    print(f"  State:   {info.get('state', 'unknown')}")


# ──────────────────────────────────────────────────────────────
# Commands: Tasks & Interventions
# ──────────────────────────────────────────────────────────────

def cmd_tasks(client: ovh.Client, args: argparse.Namespace) -> None:
    """View server tasks."""
    server = args.server

    if args.task_id:
        task = client.get(f"/dedicated/server/{server}/task/{args.task_id}")
        pp(task)
        return

    if args.cancel_id:
        print(f"Cancelling task {args.cancel_id}...")
        try:
            client.post(f"/dedicated/server/{server}/task/{args.cancel_id}/cancel")
            print("Task cancelled.")
        except Exception as e:
            print(f"Could not cancel task: {e}")
        return

    tasks = client.get(f"/dedicated/server/{server}/task")
    if not tasks:
        print(f"No tasks found for {server}.")
        return
    print(f"Tasks for {server} (most recent first):\n")
    for tid in sorted(tasks, reverse=True)[:20]:
        try:
            task = client.get(f"/dedicated/server/{server}/task/{tid}")
            status = task.get("status", "?")
            func = task.get("function", "?")
            done = task.get("doneDate", "pending")
            print(f"  [{tid}] {func:25s} status={status:10s} done={done}")
        except Exception:
            print(f"  [{tid}] (error fetching details)")


def cmd_interventions(client: ovh.Client, args: argparse.Namespace) -> None:
    """View datacenter interventions."""
    server = args.server
    interventions = client.get(f"/dedicated/server/{server}/intervention")
    if not interventions:
        print(f"No interventions found for {server}.")
        return
    print(f"Interventions for {server}:\n")
    for iid in interventions:
        detail = client.get(f"/dedicated/server/{server}/intervention/{iid}")
        pp(detail)
        print()


# ──────────────────────────────────────────────────────────────
# Commands: Secondary DNS
# ──────────────────────────────────────────────────────────────

def cmd_dns(client: ovh.Client, args: argparse.Namespace) -> None:
    """Secondary DNS management."""
    server = args.server

    if args.list_dns:
        zones = client.get(f"/dedicated/server/{server}/secondaryDnsDomains")
        if not zones:
            print("No secondary DNS zones configured.")
            return
        for domain in zones:
            detail = client.get(f"/dedicated/server/{server}/secondaryDnsDomains/{domain}")
            pp(detail)
        return

    if args.add_dns:
        print(f"Adding secondary DNS: {args.add_dns} -> {args.dns_ip}...")
        client.post(
            f"/dedicated/server/{server}/secondaryDnsDomains",
            domain=args.add_dns,
            ip=args.dns_ip,
        )
        print("Secondary DNS added.")
        return

    if args.remove_dns:
        print(f"Removing secondary DNS: {args.remove_dns}...")
        client.delete(f"/dedicated/server/{server}/secondaryDnsDomains/{args.remove_dns}")
        print("Secondary DNS removed.")
        return

    print("Specify --list, --add DOMAIN --ip IP, or --remove DOMAIN")


# ──────────────────────────────────────────────────────────────
# Commands: Server Configuration
# ──────────────────────────────────────────────────────────────

def cmd_config(client: ovh.Client, args: argparse.Namespace) -> None:
    """Update server configuration properties."""
    server = args.server

    if args.dump:
        info = client.get(f"/dedicated/server/{server}")
        pp(info)
        return

    updates = {}
    if args.display_name:
        updates["name"] = args.display_name
    if args.set_monitoring is not None:
        updates["monitoring"] = args.set_monitoring.lower() == "true"
    if args.rescue_mail:
        updates["rescueMail"] = args.rescue_mail

    if not updates:
        print("Specify --dump, --display-name, --monitoring true|false, or --rescue-mail EMAIL")
        return

    print(f"Updating {server} config: {updates}")
    client.put(f"/dedicated/server/{server}", **updates)
    print("Configuration updated.")


# ──────────────────────────────────────────────────────────────
# Argument Parser
# ──────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OVHcloud Dedicated Server Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              %(prog)s list
              %(prog)s info ns1234567.ip-42-42-42.eu
              %(prog)s reboot ns1234567.ip-42-42-42.eu --hard
              %(prog)s ipmi ns1234567.ip-42-42-42.eu --kvm-html
              %(prog)s firewall 42.42.42.42/32 --list
        """),
    )

    sub = parser.add_subparsers(dest="command", help="Command to execute")

    # list
    sub.add_parser("list", help="List all dedicated servers")

    # info
    p = sub.add_parser("info", help="Get server details")
    p.add_argument("server", help="Server name (e.g. ns1234567.ip-42-42-42.eu)")

    # hardware
    p = sub.add_parser("hardware", help="Get hardware specifications")
    p.add_argument("server")

    # service
    p = sub.add_parser("service", help="Get service/billing info")
    p.add_argument("server")

    # reboot
    p = sub.add_parser("reboot", help="Reboot server")
    p.add_argument("server")
    p.add_argument("--hard", action="store_true", help="Force hard reboot via IPMI")

    # rescue
    p = sub.add_parser("rescue", help="Enable/disable rescue mode")
    p.add_argument("server")
    p.add_argument("--enable", action="store_true")
    p.add_argument("--disable", action="store_true")

    # boot
    p = sub.add_parser("boot", help="Boot configuration management")
    p.add_argument("server")
    p.add_argument("--list", dest="list_boots", action="store_true", help="List boot options")
    p.add_argument("--set", dest="set_boot", help="Set boot ID")
    p.add_argument("--current", action="store_true", help="Show current boot config")

    # ipmi
    p = sub.add_parser("ipmi", help="IPMI / KVM console access")
    p.add_argument("server")
    p.add_argument("--test", action="store_true", help="Test IPMI availability")
    p.add_argument("--reset", action="store_true", help="Reset IPMI interface")
    p.add_argument("--kvm-html", action="store_true", help="Get HTML5 KVM URL")
    p.add_argument("--kvm-java", action="store_true", help="Get Java KVM applet")
    p.add_argument("--sol-ssh", action="store_true", help="Get SoL SSH access")
    p.add_argument("--sol-web", action="store_true", help="Get SoL web access")
    p.add_argument("--ip", help="Your public IP (auto-detected if omitted)")
    p.add_argument("--ttl", type=int, default=15, help="Access TTL in minutes (default: 15)")

    # os
    p = sub.add_parser("os", help="OS installation management")
    p.add_argument("server")
    p.add_argument("--list", dest="list_os", action="store_true", help="List compatible templates")
    p.add_argument("--list-ovh", dest="list_ovh", action="store_true", help="List OVH templates")
    p.add_argument("--install", help="Install OS template (DESTRUCTIVE)")
    p.add_argument("--hostname", help="Custom hostname for install")
    p.add_argument("--ssh-key", help="SSH key name (must be registered in OVH)")

    # ip
    p = sub.add_parser("ip", help="IP address management")
    p.add_argument("server")
    p.add_argument("--list", dest="list_ips", action="store_true")
    p.add_argument("--detail", help="Get IP block details")
    p.add_argument("--reverse", help="Manage reverse DNS for IP")
    p.add_argument("--value", help="Reverse DNS value to set")
    p.add_argument("--delete", action="store_true", help="Delete reverse DNS")

    # network
    p = sub.add_parser("network", help="Network interfaces and bandwidth")
    p.add_argument("server")
    p.add_argument("--interfaces", action="store_true")
    p.add_argument("--bandwidth", action="store_true")
    p.add_argument("--traffic", action="store_true")
    p.add_argument("--period", choices=["daily", "monthly", "weekly", "yearly"])

    # firewall
    p = sub.add_parser("firewall", help="OVH network firewall")
    p.add_argument("ip_block", help="IP block (e.g. 42.42.42.42/32)")
    p.add_argument("--list", dest="list_rules", action="store_true")
    p.add_argument("--rule", dest="rule_detail", type=int, help="Get rule by sequence number")
    p.add_argument("--add", dest="add_rule", action="store_true")
    p.add_argument("--remove", dest="remove_rule", type=int, help="Remove rule by sequence")
    p.add_argument("--enable", dest="enable_fw", action="store_true")
    p.add_argument("--disable", dest="disable_fw", action="store_true")
    p.add_argument("--mitigation", choices=["on", "off"])
    p.add_argument("--sequence", type=int, help="Rule sequence number")
    p.add_argument("--action", choices=["permit", "deny"], help="Rule action")
    p.add_argument("--protocol", choices=["tcp", "udp", "icmp", "ipv4", "ipv6"], help="Protocol")
    p.add_argument("--source", help="Source IP/CIDR")
    p.add_argument("--dest-port", help="Destination port")
    p.add_argument("--source-port", help="Source port")

    # monitoring
    p = sub.add_parser("monitoring", help="Server monitoring")
    p.add_argument("server")
    p.add_argument("--status", action="store_true")
    p.add_argument("--enable", dest="enable_mon", action="store_true")
    p.add_argument("--disable", dest="disable_mon", action="store_true")
    p.add_argument("--alerts", action="store_true")

    # tasks
    p = sub.add_parser("tasks", help="View server tasks")
    p.add_argument("server")
    p.add_argument("--id", dest="task_id", type=int, help="Get specific task")
    p.add_argument("--cancel", dest="cancel_id", type=int, help="Cancel a task")

    # interventions
    p = sub.add_parser("interventions", help="View datacenter interventions")
    p.add_argument("server")

    # dns
    p = sub.add_parser("dns", help="Secondary DNS management")
    p.add_argument("server")
    p.add_argument("--list", dest="list_dns", action="store_true")
    p.add_argument("--add", dest="add_dns", help="Add secondary DNS domain")
    p.add_argument("--remove", dest="remove_dns", help="Remove secondary DNS domain")
    p.add_argument("--ip", dest="dns_ip", help="DNS server IP (for --add)")

    # config
    p = sub.add_parser("config", help="Server configuration")
    p.add_argument("server")
    p.add_argument("--dump", action="store_true", help="Dump full config as JSON")
    p.add_argument("--display-name", help="Set display name")
    p.add_argument("--monitoring", dest="set_monitoring", help="Enable/disable monitoring (true|false)")
    p.add_argument("--rescue-mail", help="Set rescue mode email")

    return parser


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

COMMANDS = {
    "list": cmd_list,
    "info": cmd_info,
    "hardware": cmd_hardware,
    "service": cmd_service,
    "reboot": cmd_reboot,
    "rescue": cmd_rescue,
    "boot": cmd_boot,
    "ipmi": cmd_ipmi,
    "os": cmd_os,
    "ip": cmd_ip,
    "network": cmd_network,
    "firewall": cmd_firewall,
    "monitoring": cmd_monitoring,
    "tasks": cmd_tasks,
    "interventions": cmd_interventions,
    "dns": cmd_dns,
    "config": cmd_config,
}


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = get_client()
    handler = COMMANDS.get(args.command)
    if handler:
        try:
            handler(client, args)
        except ovh.exceptions.ResourceNotFoundError as e:
            print(f"ERROR 404: Resource not found — {e}")
            print("Check server name with: ovh_server.py list")
        except ovh.exceptions.NotGrantedCallError as e:
            print(f"ERROR 403: Insufficient permissions — {e}")
            print("Regenerate consumer key with the required API scopes.")
        except ovh.exceptions.BadParametersError as e:
            print(f"ERROR 400: Bad parameters — {e}")
        except ovh.exceptions.NetworkError as e:
            print(f"ERROR: Network error — {e}")
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

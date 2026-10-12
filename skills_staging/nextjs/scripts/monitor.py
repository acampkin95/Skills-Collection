#!/usr/bin/env python3
"""
Observability Monitor - Application monitoring and alerting.

Usage:
    python3 monitor.py start
    python3 monitor.py status
    python3 monitor.py metrics <service>
    python3 monitor.py alerts [--critical|--warning]
    python3 monitor.py dashboard
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import threading

@dataclass
class Metric:
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    id: str
    service: str
    severity: str  # critical, warning, info
    message: str
    timestamp: datetime
    acknowledged: bool = False

class ObservabilityMonitor:
    def __init__(self, config_file: str = "monitoring-config.json") -> None:
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.metrics = []
        self.alerts = []
        self.running = False
        self.logger = logging.getLogger(__name__)

    def load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration."""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {
            "services": [],
            "thresholds": {
                "cpu_percent": {"warning": 70, "critical": 90},
                "memory_percent": {"warning": 80, "critical": 95},
                "response_time_ms": {"warning": 500, "critical": 2000},
                "error_rate_percent": {"warning": 1, "critical": 5}
            },
            "check_interval": 30
        }

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        import psutil

        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_bytes_sent": psutil.net_io_counters().bytes_sent,
            "network_bytes_recv": psutil.net_io_counters().bytes_recv,
        }

    def collect_docker_metrics(self, service: str) -> Dict[str, Any]:
        """Collect Docker container metrics."""
        try:
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", "json", service],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "cpu_percent": float(data.get("CPUPerc", "0%").replace("%", "")),
                    "memory_percent": float(data.get("MemPerc", "0%").replace("%", "")),
                    "memory_usage_mb": float(data.get("MemUsage", "0MiB").split("/")[0].replace("MiB", "")),
                }
        except Exception as e:
            pass
        return {}

    def check_thresholds(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check metrics against thresholds."""
        alerts = []
        thresholds = self.config.get("thresholds", {})

        for metric_name, value in metrics.items():
            if metric_name not in thresholds:
                continue

            threshold = thresholds[metric_name]
            if value >= threshold.get("critical", 100):
                alerts.append(Alert(
                    id=f"alert-{datetime.now().strftime('%Y%m%d%H%M%S')}-{metric_name}",
                    service="system",
                    severity="critical",
                    message=f"{metric_name} critical: {value:.2f}",
                    timestamp=datetime.now()
                ))
            elif value >= threshold.get("warning", 100):
                alerts.append(Alert(
                    id=f"alert-{datetime.now().strftime('%Y%m%d%H%M%S')}-{metric_name}",
                    service="system",
                    severity="warning",
                    message=f"{metric_name} warning: {value:.2f}",
                    timestamp=datetime.now()
                ))

        return alerts

    def record_metric(self, metric: Metric) -> None:
        """Record a metric."""
        self.metrics.append(metric)
        # Keep only last 10000 metrics
        if len(self.metrics) > 10000:
            self.metrics = self.metrics[-10000:]

    def record_alert(self, alert: Alert) -> None:
        """Record an alert."""
        self.alerts.append(alert)
        print(f"  [{alert.severity.upper()}] {alert.message}")

    def get_metrics(self, service: str = None, window: int = 3600) -> List[Metric]:
        """Get metrics for service within time window."""
        cutoff = datetime.now() - timedelta(seconds=window)

        if service:
            return [m for m in self.metrics
                   if m.timestamp > cutoff and m.labels.get("service") == service]
        return [m for m in self.metrics if m.timestamp > cutoff]

    def get_alerts(self, severity: str = None) -> List[Alert]:
        """Get alerts by severity."""
        if severity:
            return [a for a in self.alerts if a.severity == severity]
        return self.alerts

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def start_monitoring(self) -> None:
        """Start continuous monitoring."""
        self.running = True
        interval = self.config.get("check_interval", 30)

        print(f"Starting monitoring (interval: {interval}s)...")
        print("Press Ctrl+C to stop")
        print()

        while self.running:
            try:
                # Collect system metrics
                system_metrics = self.collect_system_metrics()
                for name, value in system_metrics.items():
                    self.record_metric(Metric(
                        name=name,
                        value=value,
                        timestamp=datetime.now(),
                        labels={"service": "system"}
                    ))

                # Check thresholds
                alerts = self.check_thresholds(system_metrics)
                for alert in alerts:
                    self.record_alert(alert)

                # Collect service metrics
                for service in self.config.get("services", []):
                    service_metrics = self.collect_docker_metrics(service)
                    for name, value in service_metrics.items():
                        self.record_metric(Metric(
                            name=name,
                            value=value,
                            timestamp=datetime.now(),
                            labels={"service": service}
                        ))

                # Print status
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"CPU: {system_metrics.get('cpu_percent', 0):.1f}% "
                      f"Mem: {system_metrics.get('memory_percent', 0):.1f}%")

                time.sleep(interval)

            except KeyboardInterrupt:
                print("\nStopping monitoring...")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(interval)

    def show_dashboard(self) -> None:
        """Show monitoring dashboard."""
        print()
        print("=" * 70)
        print(f" OBSERVABILITY DASHBOARD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # System status
        sys_metrics = self.get_metrics(service="system", window=300)
        if sys_metrics:
            latest = sys_metrics[-1]
            print(f"\nSystem Health:")
            print(f"  CPU:    {latest.value if latest.name == 'cpu_percent' else 'N/A'}%")
            print(f"  Memory: {latest.value if latest.name == 'memory_percent' else 'N/A'}%")
            print(f"  Disk:   {latest.value if latest.name == 'disk_percent' else 'N/A'}%")

        # Critical alerts
        critical = self.get_alerts("critical")
        warning = self.get_alerts("warning")

        print(f"\nAlerts:")
        print(f"  Critical: {len([a for a in critical if not a.acknowledged])}")
        print(f"  Warnings: {len([a for a in warning if not a.acknowledged])}")

        # Recent alerts
        print(f"\nRecent Alerts:")
        recent = sorted(self.alerts, key=lambda a: a.timestamp, reverse=True)[:5]
        for alert in recent:
            status = "✓" if alert.acknowledged else "○"
            print(f"  [{status}] [{alert.severity.upper():8}] {alert.message}")

        print()

    def export_metrics(self, output_file: str = "metrics.json") -> None:
        """Export metrics to file."""
        data = {
            "exported": datetime.now().isoformat(),
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "timestamp": m.timestamp.isoformat(),
                    "labels": m.labels
                }
                for m in self.metrics
            ]
        }
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Exported {len(self.metrics)} metrics to {output_file}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Observability Monitor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start monitoring")

    status_parser = subparsers.add_parser("status", help="Show current status")

    metrics_parser = subparsers.add_parser("metrics", help="Get metrics")
    metrics_parser.add_argument("service", nargs="?", default=None)
    metrics_parser.add_argument("--window", type=int, default=3600)

    alerts_parser = subparsers.add_parser("alerts", help="Show alerts")
    alerts_parser.add_argument("--critical", action="store_true")
    alerts_parser.add_argument("--warning", action="store_true")

    dashboard_parser = subparsers.add_parser("dashboard", help="Show dashboard")

    export_parser = subparsers.add_parser("export", help="Export metrics")
    export_parser.add_argument("--output", default="metrics.json")

    args = parser.parse_args()
    monitor = ObservabilityMonitor()

    if args.command == "start":
        monitor.start_monitoring()
    elif args.command == "status":
        sys_metrics = monitor.collect_system_metrics()
        print(f"CPU: {sys_metrics.get('cpu_percent', 0):.1f}%")
        print(f"Memory: {sys_metrics.get('memory_percent', 0):.1f}%")
        print(f"Disk: {sys_metrics.get('disk_percent', 0):.1f}%")
    elif args.command == "metrics":
        metrics = monitor.get_metrics(args.service, args.window)
        print(f"Found {len(metrics)} metrics")
        for m in metrics[:10]:
            print(f"  {m.name}: {m.value} ({m.timestamp})")
    elif args.command == "alerts":
        severity = "critical" if args.critical else "warning" if args.warning else None
        alerts = monitor.get_alerts(severity)
        for a in alerts:
            print(f"[{a.severity}] {a.timestamp}: {a.message}")
    elif args.command == "dashboard":
        monitor.show_dashboard()
    elif args.command == "export":
        monitor.export_metrics(args.output)


if __name__ == "__main__":
    main()

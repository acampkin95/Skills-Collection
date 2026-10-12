#!/usr/bin/env python3
"""
Docker Deployment Manager - Container deployment and orchestration.

Usage:
    python3 deploy.py build <service>
    python3 deploy.py push <service>
    python3 deploy.py deploy <service> [--env <production|staging|development>]
    python3 deploy.py scale <service> <replicas>
    python3 deploy.py logs <service> [--tail] [--follow]
    python3 deploy.py status
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

@dataclass
class Service:
    name: str
    image: str
    port: int
    replicas: int = 1
    environment: Optional[Dict[str, str]] = None
    volumes: Optional[List[str]] = None
    depends_on: Optional[List[str]] = None

class DockerDeploymentManager:
    def __init__(self, config_file: str = "docker-compose.yml") -> None:
        self.config_file = Path(config_file)
        self.compose_config = self.load_compose()

    def load_compose(self) -> Dict[str, Any]:
        """Load docker-compose configuration."""
        if self.config_file.exists():
            import yaml
            with open(self.config_file) as f:
                return yaml.safe_load(f)
        return {}

    def build_image(self, service: str) -> bool:
        """Build Docker image for service."""
        print(f"Building image for {service}...")

        cmd = [
            "docker", "build",
            "-t", f"{service}:latest",
            "-f", f"Dockerfile.{service}",
            "."
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Image built: {service}:latest")
            return True
        else:
            print(f"  ✗ Build failed: {result.stderr}")
            return False

    def push_image(self, service: str, registry: str = "localhost") -> bool:
        """Push image to registry."""
        print(f"Pushing {service} to {registry}...")

        local_tag = f"{service}:latest"
        remote_tag = f"{registry}/{service}:latest"

        # Tag image
        subprocess.run(["docker", "tag", local_tag, remote_tag], check=True)

        # Push image
        cmd = ["docker", "push", remote_tag]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"  ✓ Pushed: {remote_tag}")
            return True
        else:
            print(f"  ✗ Push failed: {result.stderr}")
            return False

    def deploy_service(self, service: str, env: str = "development") -> bool:
        """Deploy service using docker-compose."""
        print(f"Deploying {service} to {env}...")

        env_file = f".env.{env}"
        cmd = [
            "docker-compose", "-f", str(self.config_file),
            "--env-file", env_file,
            "up", "-d", "--no-deps", service
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Deployed: {service}")
            return True
        else:
            print(f"  ✗ Deployment failed: {result.stderr}")
            return False

    def scale_service(self, service: str, replicas: int) -> bool:
        """Scale service to specified replicas."""
        print(f"Scaling {service} to {replicas} replicas...")

        cmd = [
            "docker-compose", "-f", str(self.config_file),
            "up", "-d", "--scale", f"{service}={replicas}", service
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Scaled: {service} -> {replicas} replicas")
            return True
        else:
            print(f"  ✗ Scale failed: {result.stderr}")
            return False

    def get_logs(self, service: str, tail: int = 100, follow: bool = False) -> None:
        """Get logs for service."""
        cmd = ["docker-compose", "-f", str(self.config_file), "logs", "--tail", str(tail), service]
        if follow:
            cmd.append("-f")

        subprocess.run(cmd)

    def get_status(self) -> Dict[str, Any]:
        """Get deployment status."""
        status = {}

        if not self.compose_config:
            return status

        services = self.compose_config.get("services", {})

        for service_name in services:
            cmd = ["docker-compose", "-f", str(self.config_file), "ps", service_name]
            result = subprocess.run(cmd, capture_output=True, text=True)

            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                # Parse status (last line contains state)
                status[service_name] = {
                    "running": "Up" in lines[-1],
                    "status": lines[-1]
                }

        return status

    def print_status(self):
        """Print deployment status."""
        print(f"Docker Deployment Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        status = self.get_status()

        if not status:
            print("No services configured")
            return

        for service, info in status.items():
            state = "●" if info["running"] else "○"
            print(f"  {state} {service}: {info['status']}")

        print()

    def health_check(self, service: str, endpoint: str = "/health") -> bool:
        """Check service health."""
        import urllib.request
        import urllib.error

        # Get service port from config
        services = self.compose_config.get("services", {})
        service_config = services.get(service, {})

        # Use first published port
        ports = service_config.get("ports", [])
        if not ports:
            return False

        port = str(ports[0]).split(":")[0]
        url = f"http://localhost:{port}{endpoint}"

        try:
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req, timeout=5)
            return response.status == 200
        except Exception as e:
            return False

    def rollback(self, service: str, previous_version: str = "previous") -> bool:
        """Rollback to previous version."""
        print(f"Rolling back {service} to {previous_version}...")

        cmd = [
            "docker", "tag", f"{service}:{previous_version}", f"{service}:latest"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            self.deploy_service(service)
            return True
        else:
            print(f"  ✗ Rollback failed: {result.stderr}")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Docker Deployment Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build service image")
    build_parser.add_argument("service")

    push_parser = subparsers.add_parser("push", help="Push image to registry")
    push_parser.add_argument("service")
    push_parser.add_argument("--registry", default="localhost")

    deploy_parser = subparsers.add_parser("deploy", help="Deploy service")
    deploy_parser.add_argument("service")
    deploy_parser.add_argument("--env", default="development")

    scale_parser = subparsers.add_parser("scale", help="Scale service")
    scale_parser.add_argument("service")
    scale_parser.add_argument("replicas", type=int)

    logs_parser = subparsers.add_parser("logs", help="Get service logs")
    logs_parser.add_argument("service")
    logs_parser.add_argument("--tail", type=int, default=100)
    logs_parser.add_argument("--follow", action="store_true")

    status_parser = subparsers.add_parser("status", help="Show deployment status")

    health_parser = subparsers.add_parser("health", help="Check service health")
    health_parser.add_argument("service")
    health_parser.add_argument("--endpoint", default="/health")

    rollback_parser = subparsers.add_parser("rollback", help="Rollback service")
    rollback_parser.add_argument("service")
    rollback_parser.add_argument("--version", default="previous")

    args = parser.parse_args()
    manager = DockerDeploymentManager()

    if args.command == "build":
        manager.build_image(args.service)
    elif args.command == "push":
        manager.push_image(args.service, args.registry)
    elif args.command == "deploy":
        manager.deploy_service(args.service, args.env)
    elif args.command == "scale":
        manager.scale_service(args.service, args.replicas)
    elif args.command == "logs":
        manager.get_logs(args.service, args.tail, args.follow)
    elif args.command == "status":
        manager.print_status()
    elif args.command == "health":
        healthy = manager.health_check(args.service, args.endpoint)
        print(f"Health check: {'✓ PASS' if healthy else '✗ FAIL'}")
    elif args.command == "rollback":
        manager.rollback(args.service, args.version)


if __name__ == "__main__":
    main()
else:
    pass

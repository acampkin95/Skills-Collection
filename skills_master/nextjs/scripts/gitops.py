#!/usr/bin/env python3
"""
GitOps Manager - Git-based infrastructure and deployment automation.

Usage:
    python3 gitops.py init <repo-url>
    python3 gitops.py sync [--apply]
    python3 gitops.py diff <environment>
    python3 gitops.py plan <environment>
    python3 gitops.py status
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import yaml

@dataclass
class Environment:
    name: str
    cluster: str
    namespace: str
    variables: Optional[Dict[str, Any]] = None
    secrets: Optional[Dict[str, Any]] = None

class GitOpsManager:
    def __init__(self, repo_path: str = ".") -> None:
        self.repo_path = Path(repo_path)
        self.environments_file = self.repo_path / "environments.yaml"

    def load_environments(self) -> Dict[str, Any]:
        """Load environment configurations."""
        if self.environments_file.exists():
            with open(self.environments_file) as f:
                return yaml.safe_load(f)
        return {"environments": []}

    def init_repo(self, repo_url: str) -> None:
        """Initialize GitOps repository."""
        print(f"Initializing GitOps repo: {repo_url}")

        # Clone or create repo structure
        if not self.repo_path.exists():
            subprocess.run(["git", "clone", repo_url, str(self.repo_path)], check=True)

        # Create directory structure
        dirs = [
            "clusters",
            "namespaces",
            "config",
            "secrets",
            "apps",
            "environments"
        ]

        for dir_name in dirs:
            dir_path = self.repo_path / dir_name
            dir_path.mkdir(exist_ok=True)

            # Create README
            readme = dir_path / "README.md"
            if not readme.exists():
                with open(readme, 'w') as f:
                    f.write(f"# {dir_name}\n\nGitOps managed by GitOps Manager.\n")

        # Create base environments.yaml
        base_env = {
            "environments": [
                {
                    "name": "development",
                    "cluster": "dev-cluster",
                    "namespace": "dev-ns",
                    "auto_sync": True
                },
                {
                    "name": "staging",
                    "cluster": "staging-cluster",
                    "namespace": "staging-ns",
                    "auto_sync": False
                },
                {
                    "name": "production",
                    "cluster": "prod-cluster",
                    "namespace": "prod-ns",
                    "auto_sync": False
                }
            ]
        }

        with open(self.environments_file, 'w') as f:
            yaml.dump(base_env, f)

        # Create .gitignore
        gitignore = self.repo_path / ".gitignore"
        with open(gitignore, 'w') as f:
            f.write("""# GitOps .gitignore
*.local
*.secret.*
.secrets/
.env*
kustomization.override.yaml
""")

        print(f"✓ Initialized GitOps repo at {self.repo_path}")
        print("\nNext steps:")
        print("  1. Review environments.yaml")
        print("  2. Add cluster configurations to clusters/")
        print("  3. Configure namespaces in namespaces/")
        print("  4. Push to remote repository")

    def sync(self, apply: bool = False) -> None:
        """Sync with remote repository."""
        print("Syncing with remote repository...")

        # Pull latest changes
        subprocess.run(["git", "pull"], cwd=self.repo_path, check=True)

        # Check for changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        changes = result.stdout.strip()
        if not changes:
            print("✓ No changes to apply")
            return

        print("Changes detected:")
        print(changes)

        if apply:
            # Apply changes based on file type
            for line in changes.split("\n"):
                if line.strip():
                    status = line[:2]
                    filename = line[3:].strip()

                    if status == "A " or status == "M ":
                        if filename.startswith("clusters/"):
                            print(f"  Applying cluster config: {filename}")
                        elif filename.startswith("namespaces/"):
                            print(f"  Applying namespace: {filename}")
                        elif filename.startswith("apps/"):
                            print(f"  Applying application: {filename}")

            subprocess.run(["git", "add", "."], cwd=self.repo_path)
            subprocess.run(
                ["git", "commit", "-m", f"GitOps sync: {datetime.now().isoformat()}"],
                cwd=self.repo_path,
                check=True
            )
            subprocess.run(["git", "push"], cwd=self.repo_path, check=True)
            print("✓ Changes applied and committed")
        else:
            print("\nRun with --apply to apply changes")

    def diff_environment(self, environment: str) -> None:
        """Show diff for environment."""
        envs = self.load_environments()
        env_config = next((e for e in envs.get("environments", []) if e["name"] == environment), None)

        if not env_config:
            print(f"Environment '{environment}' not found")
            return

        print(f"Configuration for {environment}:")
        print(f"  Cluster: {env_config.get('cluster', 'N/A')}")
        print(f"  Namespace: {env_config.get('namespace', 'N/A')}")
        print(f"  Auto-sync: {env_config.get('auto_sync', False)}")

        # Show Kustomize overlay
        overlay_dir = self.repo_path / "apps" / environment
        if overlay_dir.exists():
            print(f"\n  Overlays: {list(overlay_dir.glob('*'))}")

    def plan_environment(self, environment: str) -> None:
        """Generate plan for environment changes."""
        envs = self.load_environments()
        env_config = next((e for e in envs.get("environments", []) if e["name"] == environment), None)

        if not env_config:
            print(f"Environment '{environment}' not found")
            return

        print(f"Planning changes for {environment}...")
        print(f"  Cluster: {env_config.get('cluster')}")
        print(f"  Namespace: {env_config.get('namespace')}")
        print()

        # Check for pending changes
        result = subprocess.run(
            ["git", "diff", "HEAD", "--name-only"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        changes = result.stdout.strip().split("\n")
        if not changes or changes == [""]:
            print("  No pending changes")
            return

        print("  Proposed changes:")
        for change in changes:
            if change:
                print(f"    + {change}")

        print("\n  This would modify:")
        print(f"    - {len([c for c in changes if c.startswith('apps/')])} app configurations")
        print(f"    - {len([c for c in changes if c.startswith('namespaces/')])} namespaces")
        print(f"    - {len([c for c in changes if c.startswith('clusters/')])} cluster configs")

    def show_status(self) -> None:
        """Show GitOps status."""
        print(f"GitOps Repository: {self.repo_path}")

        # Check git status
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        changes = result.stdout.strip().split("\n")
        pending = len([c for c in changes if c.strip()])

        # Get latest commit
        result = subprocess.run(
            ["git", "log", "-1", "--oneline"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        last_commit = result.stdout.strip()

        print(f"  Branch: {self.current_branch()}")
        print(f"  Last commit: {last_commit}")
        print(f"  Pending changes: {pending}")

        # Show environments
        envs = self.load_environments()
        print(f"\n  Environments ({len(envs.get('environments', []))}):")
        for env in envs.get("environments", []):
            auto_sync = "●" if env.get("auto_sync") else "○"
            print(f"    {auto_sync} {env['name']}")

    def current_branch(self) -> str:
        """Get current git branch."""
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    def create_app_manifest(self, app_name: str, environment: str, config: Dict[str, Any]) -> None:
        """Create application manifest for environment."""
        app_dir = self.repo_path / "apps" / environment / app_name
        app_dir.mkdir(parents=True, exist_ok=True)

        # Create kustomization
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": ["../base"],
            "namePrefix": f"{app_name}-",
            "namespace": environment,
            "images": [
                {
                    "name": "app",
                    "newName": config.get("image", app_name),
                    "newTag": config.get("tag", "latest")
                }
            ],
            "replicas": config.get("replicas", 1)
        }

        with open(app_dir / "kustomization.yaml", 'w') as f:
            yaml.dump(kustomization, f)

        print(f"Created manifest: {app_dir / 'kustomization.yaml'}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="GitOps Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize GitOps repo")
    init_parser.add_argument("repo_url")

    sync_parser = subparsers.add_parser("sync", help="Sync with remote")
    sync_parser.add_argument("--apply", action="store_true")

    diff_parser = subparsers.add_parser("diff", help="Show environment diff")
    diff_parser.add_argument("environment")

    plan_parser = subparsers.add_parser("plan", help="Plan environment changes")
    plan_parser.add_argument("environment")

    status_parser = subparsers.add_parser("status", help="Show status")

    manifest_parser = subparsers.add_parser("manifest", help="Create app manifest")
    manifest_parser.add_argument("app_name")
    manifest_parser.add_argument("environment")
    manifest_parser.add_argument("--image")
    manifest_parser.add_argument("--tag", default="latest")
    manifest_parser.add_argument("--replicas", type=int, default=1)

    args = parser.parse_args()
    manager = GitOpsManager()

    if args.command == "init":
        manager.init_repo(args.repo_url)
    elif args.command == "sync":
        manager.sync(args.apply)
    elif args.command == "diff":
        manager.diff_environment(args.environment)
    elif args.command == "plan":
        manager.plan_environment(args.environment)
    elif args.command == "status":
        manager.show_status()
    elif args.command == "manifest":
        manager.create_app_manifest(
            args.app_name,
            args.environment,
            {"image": args.image, "tag": args.tag, "replicas": args.replicas}
        )


if __name__ == "__main__":
    main()
else:
    pass

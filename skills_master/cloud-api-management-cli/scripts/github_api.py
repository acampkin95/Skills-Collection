#!/usr/bin/env python3
"""
GitHub API Management Script
Handles repos, issues, PRs, releases, and actions.
Token loaded from environment variables.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List, Tuple


class GitHubAPI:
    """GitHub REST API client."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable not set")
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to GitHub API."""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        if data:
            headers["Content-Type"] = "application/json"
        
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 204:
                    return {"success": True}
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            try:
                return json.loads(error_body)
            except:
                return {"error": error_body, "status": e.code}
    
    # === User Operations ===
    
    def get_user(self) -> Dict:
        """Get authenticated user info."""
        return self._request("GET", "/user")
    
    def get_user_by_name(self, username: str) -> Dict:
        """Get user by username."""
        return self._request("GET", f"/users/{username}")
    
    # === Repository Operations ===
    
    def list_repos(self, user: Optional[str] = None, type: str = "all", 
                   sort: str = "updated", per_page: int = 30) -> List:
        """List repositories."""
        if user:
            endpoint = f"/users/{user}/repos?type={type}&sort={sort}&per_page={per_page}"
        else:
            endpoint = f"/user/repos?type={type}&sort={sort}&per_page={per_page}"
        return self._request("GET", endpoint)
    
    def get_repo(self, owner: str, repo: str) -> Dict:
        """Get repository details."""
        return self._request("GET", f"/repos/{owner}/{repo}")
    
    def create_repo(self, name: str, private: bool = False, 
                    description: str = "", auto_init: bool = False) -> Dict:
        """Create new repository."""
        data = {
            "name": name,
            "private": private,
            "description": description,
            "auto_init": auto_init
        }
        return self._request("POST", "/user/repos", data)
    
    def delete_repo(self, owner: str, repo: str) -> Dict:
        """Delete repository."""
        return self._request("DELETE", f"/repos/{owner}/{repo}")
    
    # === Issues Operations ===
    
    def list_issues(self, owner: str, repo: str, state: str = "open",
                    labels: str = "", per_page: int = 30) -> List:
        """List repository issues."""
        endpoint = f"/repos/{owner}/{repo}/issues?state={state}&per_page={per_page}"
        if labels:
            endpoint += f"&labels={labels}"
        return self._request("GET", endpoint)
    
    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict:
        """Get issue details."""
        return self._request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")
    
    def create_issue(self, owner: str, repo: str, title: str, 
                     body: str = "", labels: List[str] = None,
                     assignees: List[str] = None) -> Dict:
        """Create new issue."""
        data = {"title": title, "body": body}
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        return self._request("POST", f"/repos/{owner}/{repo}/issues", data)
    
    def update_issue(self, owner: str, repo: str, issue_number: int,
                     title: Optional[str] = None, body: Optional[str] = None,
                     state: Optional[str] = None, labels: List[str] = None) -> Dict:
        """Update existing issue."""
        data = {}
        if title:
            data["title"] = title
        if body:
            data["body"] = body
        if state:
            data["state"] = state
        if labels is not None:
            data["labels"] = labels
        return self._request("PATCH", f"/repos/{owner}/{repo}/issues/{issue_number}", data)
    
    def close_issue(self, owner: str, repo: str, issue_number: int) -> Dict:
        """Close an issue."""
        return self.update_issue(owner, repo, issue_number, state="closed")
    
    # === Pull Request Operations ===
    
    def list_prs(self, owner: str, repo: str, state: str = "open",
                 per_page: int = 30) -> List:
        """List pull requests."""
        return self._request("GET", f"/repos/{owner}/{repo}/pulls?state={state}&per_page={per_page}")
    
    def get_pr(self, owner: str, repo: str, pr_number: int) -> Dict:
        """Get pull request details."""
        return self._request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}")
    
    def create_pr(self, owner: str, repo: str, title: str, head: str, 
                  base: str = "main", body: str = "", draft: bool = False) -> Dict:
        """Create pull request."""
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "draft": draft
        }
        return self._request("POST", f"/repos/{owner}/{repo}/pulls", data)
    
    def merge_pr(self, owner: str, repo: str, pr_number: int,
                 merge_method: str = "merge", commit_title: str = "") -> Dict:
        """Merge pull request."""
        data = {"merge_method": merge_method}
        if commit_title:
            data["commit_title"] = commit_title
        return self._request("PUT", f"/repos/{owner}/{repo}/pulls/{pr_number}/merge", data)
    
    # === Release Operations ===
    
    def list_releases(self, owner: str, repo: str, per_page: int = 30) -> List:
        """List releases."""
        return self._request("GET", f"/repos/{owner}/{repo}/releases?per_page={per_page}")
    
    def get_latest_release(self, owner: str, repo: str) -> Dict:
        """Get latest release."""
        return self._request("GET", f"/repos/{owner}/{repo}/releases/latest")
    
    def create_release(self, owner: str, repo: str, tag_name: str,
                       name: str = "", body: str = "", draft: bool = False,
                       prerelease: bool = False, target: str = "main") -> Dict:
        """Create release."""
        data = {
            "tag_name": tag_name,
            "name": name or tag_name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease,
            "target_commitish": target
        }
        return self._request("POST", f"/repos/{owner}/{repo}/releases", data)
    
    # === Actions Operations ===
    
    def list_workflows(self, owner: str, repo: str) -> Dict:
        """List repository workflows."""
        return self._request("GET", f"/repos/{owner}/{repo}/actions/workflows")
    
    def list_workflow_runs(self, owner: str, repo: str, workflow_id: Optional[str] = None,
                           status: Optional[str] = None) -> Dict:
        """List workflow runs."""
        endpoint = f"/repos/{owner}/{repo}/actions/runs"
        params = []
        if status:
            params.append(f"status={status}")
        if params:
            endpoint += "?" + "&".join(params)
        return self._request("GET", endpoint)
    
    def trigger_workflow(self, owner: str, repo: str, workflow_id: str,
                         ref: str = "main", inputs: Dict = None) -> Dict:
        """Trigger workflow dispatch."""
        data = {"ref": ref}
        if inputs:
            data["inputs"] = inputs
        return self._request("POST", f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches", data)
    
    # === Branch Operations ===
    
    def list_branches(self, owner: str, repo: str, protected: bool = False) -> List:
        """List branches."""
        endpoint = f"/repos/{owner}/{repo}/branches"
        if protected:
            endpoint += "?protected=true"
        return self._request("GET", endpoint)
    
    def get_branch(self, owner: str, repo: str, branch: str) -> Dict:
        """Get branch details."""
        return self._request("GET", f"/repos/{owner}/{repo}/branches/{branch}")


def parse_repo(repo_string: str) -> Tuple[str, str]:
    """Parse owner/repo string."""
    parts = repo_string.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid repo format: {repo_string} (expected owner/repo)")
    return parts[0], parts[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="GitHub API Management")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    subparsers = parser.add_subparsers(dest="command", help="Command category")
    
    # User commands
    user_parser = subparsers.add_parser("user", help="User operations")
    user_sub = user_parser.add_subparsers(dest="action")
    user_sub.add_parser("me", help="Get authenticated user")
    user_get = user_sub.add_parser("get", help="Get user by name")
    user_get.add_argument("username", help="GitHub username")
    
    # Repo commands
    repos_parser = subparsers.add_parser("repos", help="Repository operations")
    repos_sub = repos_parser.add_subparsers(dest="action")
    
    repos_list = repos_sub.add_parser("list", help="List repos")
    repos_list.add_argument("--user", help="User to list repos for")
    repos_list.add_argument("--type", default="all", help="Type: all, owner, public, private, member")
    
    repos_get = repos_sub.add_parser("get", help="Get repo details")
    repos_get.add_argument("repo", help="owner/repo")
    
    repos_create = repos_sub.add_parser("create", help="Create repo")
    repos_create.add_argument("name", help="Repository name")
    repos_create.add_argument("--private", action="store_true", help="Make private")
    repos_create.add_argument("--description", default="", help="Description")
    repos_create.add_argument("--init", action="store_true", help="Initialize with README")
    
    repos_delete = repos_sub.add_parser("delete", help="Delete repo")
    repos_delete.add_argument("repo", help="owner/repo")
    
    # Issues commands
    issues_parser = subparsers.add_parser("issues", help="Issue operations")
    issues_sub = issues_parser.add_subparsers(dest="action")
    
    issues_list = issues_sub.add_parser("list", help="List issues")
    issues_list.add_argument("repo", help="owner/repo")
    issues_list.add_argument("--state", default="open", help="State: open, closed, all")
    issues_list.add_argument("--labels", default="", help="Filter by labels")
    
    issues_get = issues_sub.add_parser("get", help="Get issue")
    issues_get.add_argument("repo", help="owner/repo")
    issues_get.add_argument("number", type=int, help="Issue number")
    
    issues_create = issues_sub.add_parser("create", help="Create issue")
    issues_create.add_argument("repo", help="owner/repo")
    issues_create.add_argument("--title", required=True, help="Issue title")
    issues_create.add_argument("--body", default="", help="Issue body")
    issues_create.add_argument("--labels", help="Comma-separated labels")
    
    issues_close = issues_sub.add_parser("close", help="Close issue")
    issues_close.add_argument("repo", help="owner/repo")
    issues_close.add_argument("number", type=int, help="Issue number")
    
    # PRs commands
    prs_parser = subparsers.add_parser("prs", help="Pull request operations")
    prs_sub = prs_parser.add_subparsers(dest="action")
    
    prs_list = prs_sub.add_parser("list", help="List PRs")
    prs_list.add_argument("repo", help="owner/repo")
    prs_list.add_argument("--state", default="open", help="State: open, closed, all")
    
    prs_get = prs_sub.add_parser("get", help="Get PR")
    prs_get.add_argument("repo", help="owner/repo")
    prs_get.add_argument("number", type=int, help="PR number")
    
    prs_create = prs_sub.add_parser("create", help="Create PR")
    prs_create.add_argument("repo", help="owner/repo")
    prs_create.add_argument("--title", required=True, help="PR title")
    prs_create.add_argument("--head", required=True, help="Head branch")
    prs_create.add_argument("--base", default="main", help="Base branch")
    prs_create.add_argument("--body", default="", help="PR body")
    
    prs_merge = prs_sub.add_parser("merge", help="Merge PR")
    prs_merge.add_argument("repo", help="owner/repo")
    prs_merge.add_argument("number", type=int, help="PR number")
    prs_merge.add_argument("--method", default="merge", help="merge, squash, or rebase")
    
    # Releases commands
    releases_parser = subparsers.add_parser("releases", help="Release operations")
    releases_sub = releases_parser.add_subparsers(dest="action")
    
    releases_list = releases_sub.add_parser("list", help="List releases")
    releases_list.add_argument("repo", help="owner/repo")
    
    releases_latest = releases_sub.add_parser("latest", help="Get latest release")
    releases_latest.add_argument("repo", help="owner/repo")
    
    releases_create = releases_sub.add_parser("create", help="Create release")
    releases_create.add_argument("repo", help="owner/repo")
    releases_create.add_argument("--tag", required=True, help="Tag name")
    releases_create.add_argument("--name", default="", help="Release name")
    releases_create.add_argument("--body", default="", help="Release notes")
    releases_create.add_argument("--draft", action="store_true", help="Create as draft")
    releases_create.add_argument("--prerelease", action="store_true", help="Mark as prerelease")
    
    # Actions commands
    actions_parser = subparsers.add_parser("actions", help="Actions operations")
    actions_sub = actions_parser.add_subparsers(dest="action")
    
    actions_workflows = actions_sub.add_parser("workflows", help="List workflows")
    actions_workflows.add_argument("repo", help="owner/repo")
    
    actions_runs = actions_sub.add_parser("runs", help="List workflow runs")
    actions_runs.add_argument("repo", help="owner/repo")
    actions_runs.add_argument("--status", help="Filter by status")
    
    actions_trigger = actions_sub.add_parser("trigger", help="Trigger workflow")
    actions_trigger.add_argument("repo", help="owner/repo")
    actions_trigger.add_argument("--workflow", required=True, help="Workflow ID or filename")
    actions_trigger.add_argument("--ref", default="main", help="Branch or tag")
    
    # Branches commands
    branches_parser = subparsers.add_parser("branches", help="Branch operations")
    branches_sub = branches_parser.add_subparsers(dest="action")
    
    branches_list = branches_sub.add_parser("list", help="List branches")
    branches_list.add_argument("repo", help="owner/repo")
    branches_list.add_argument("--protected", action="store_true", help="Only protected")
    
    branches_get = branches_sub.add_parser("get", help="Get branch")
    branches_get.add_argument("repo", help="owner/repo")
    branches_get.add_argument("branch", help="Branch name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        gh = GitHubAPI()
        result = None
        
        if args.command == "user":
            if args.action == "me":
                result = gh.get_user()
            elif args.action == "get":
                result = gh.get_user_by_name(args.username)
        
        elif args.command == "repos":
            if args.action == "list":
                result = gh.list_repos(args.user, args.type)
            elif args.action == "get":
                owner, repo = parse_repo(args.repo)
                result = gh.get_repo(owner, repo)
            elif args.action == "create":
                result = gh.create_repo(args.name, args.private, args.description, args.init)
            elif args.action == "delete":
                owner, repo = parse_repo(args.repo)
                result = gh.delete_repo(owner, repo)
        
        elif args.command == "issues":
            if args.action == "list":
                owner, repo = parse_repo(args.repo)
                result = gh.list_issues(owner, repo, args.state, args.labels)
            elif args.action == "get":
                owner, repo = parse_repo(args.repo)
                result = gh.get_issue(owner, repo, args.number)
            elif args.action == "create":
                owner, repo = parse_repo(args.repo)
                labels = args.labels.split(",") if args.labels else None
                result = gh.create_issue(owner, repo, args.title, args.body, labels)
            elif args.action == "close":
                owner, repo = parse_repo(args.repo)
                result = gh.close_issue(owner, repo, args.number)
        
        elif args.command == "prs":
            if args.action == "list":
                owner, repo = parse_repo(args.repo)
                result = gh.list_prs(owner, repo, args.state)
            elif args.action == "get":
                owner, repo = parse_repo(args.repo)
                result = gh.get_pr(owner, repo, args.number)
            elif args.action == "create":
                owner, repo = parse_repo(args.repo)
                result = gh.create_pr(owner, repo, args.title, args.head, args.base, args.body)
            elif args.action == "merge":
                owner, repo = parse_repo(args.repo)
                result = gh.merge_pr(owner, repo, args.number, args.method)
        
        elif args.command == "releases":
            if args.action == "list":
                owner, repo = parse_repo(args.repo)
                result = gh.list_releases(owner, repo)
            elif args.action == "latest":
                owner, repo = parse_repo(args.repo)
                result = gh.get_latest_release(owner, repo)
            elif args.action == "create":
                owner, repo = parse_repo(args.repo)
                result = gh.create_release(owner, repo, args.tag, args.name, 
                                           args.body, args.draft, args.prerelease)
        
        elif args.command == "actions":
            if args.action == "workflows":
                owner, repo = parse_repo(args.repo)
                result = gh.list_workflows(owner, repo)
            elif args.action == "runs":
                owner, repo = parse_repo(args.repo)
                result = gh.list_workflow_runs(owner, repo, status=args.status)
            elif args.action == "trigger":
                owner, repo = parse_repo(args.repo)
                result = gh.trigger_workflow(owner, repo, args.workflow, args.ref)
        
        elif args.command == "branches":
            if args.action == "list":
                owner, repo = parse_repo(args.repo)
                result = gh.list_branches(owner, repo, args.protected)
            elif args.action == "get":
                owner, repo = parse_repo(args.repo)
                result = gh.get_branch(owner, repo, args.branch)
        
        if result is not None:
            print(json.dumps(result, indent=2))
            sys.exit(0)
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

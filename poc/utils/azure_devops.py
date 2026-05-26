"""
Azure DevOps REST API client.
Handles fetching PR diffs and posting comments back to the PR.
Auth: Personal Access Token (PAT) via Basic auth.
"""

import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

API_VERSION = "7.1"


def _get_config() -> dict:
    return {
        "org_url": os.getenv("AZURE_DEVOPS_ORG_URL", "").rstrip("/"),
        "pat":     os.getenv("AZURE_DEVOPS_PAT", ""),
        "project": os.getenv("AZURE_DEVOPS_PROJECT", ""),
        "repo":    os.getenv("AZURE_DEVOPS_REPO", ""),
    }


def is_configured() -> bool:
    cfg = _get_config()
    return all([cfg["org_url"], cfg["pat"], cfg["project"], cfg["repo"]])


def _headers(pat: str) -> dict:
    token = base64.b64encode(f":{pat}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }


def _base(cfg: dict) -> str:
    return f"{cfg['org_url']}/{cfg['project']}/_apis/git/repositories/{cfg['repo']}"


# ── Pull Requests ──────────────────────────────────────────────────────────────

def list_pull_requests(status: str = "active", top: int = 20) -> list[dict]:
    """
    Returns a list of PRs. Each dict has: id, title, sourceBranch, createdBy, status.
    """
    cfg = _get_config()
    url = (
        f"{_base(cfg)}/pullRequests"
        f"?api-version={API_VERSION}"
        f"&searchCriteria.status={status}"
        f"&$top={top}"
    )
    resp = requests.get(url, headers=_headers(cfg["pat"]), timeout=15)
    resp.raise_for_status()
    prs = resp.json().get("value", [])
    return [
        {
            "id":            pr["pullRequestId"],
            "title":         pr.get("title", ""),
            "source_branch": pr.get("sourceRefName", "").replace("refs/heads/", ""),
            "target_branch": pr.get("targetRefName", "").replace("refs/heads/", ""),
            "created_by":    pr.get("createdBy", {}).get("displayName", ""),
            "status":        pr.get("status", ""),
        }
        for pr in prs
    ]


def get_pr_details(pr_id: int) -> dict:
    cfg = _get_config()
    url = f"{_base(cfg)}/pullRequests/{pr_id}?api-version={API_VERSION}"
    resp = requests.get(url, headers=_headers(cfg["pat"]), timeout=15)
    resp.raise_for_status()
    pr = resp.json()
    return {
        "id":            pr["pullRequestId"],
        "title":         pr.get("title", ""),
        "source_branch": pr.get("sourceRefName", "").replace("refs/heads/", ""),
        "target_branch": pr.get("targetRefName", "").replace("refs/heads/", ""),
        "created_by":    pr.get("createdBy", {}).get("displayName", ""),
        "description":   pr.get("description", ""),
    }


# ── Changed Files ──────────────────────────────────────────────────────────────

def get_pr_changed_files(pr_id: int) -> list[dict]:
    """
    Returns list of files changed in the PR.
    Each dict: { path, change_type }
    Filters to only .cs and .ts files (what our agents understand).
    """
    cfg = _get_config()

    # Get latest iteration
    iter_url = f"{_base(cfg)}/pullRequests/{pr_id}/iterations?api-version={API_VERSION}"
    iter_resp = requests.get(iter_url, headers=_headers(cfg["pat"]), timeout=15)
    iter_resp.raise_for_status()
    iterations = iter_resp.json().get("value", [])
    if not iterations:
        return []
    latest_iteration = iterations[-1]["id"]

    # Get changed files in that iteration
    changes_url = (
        f"{_base(cfg)}/pullRequests/{pr_id}/iterations/{latest_iteration}/changes"
        f"?api-version={API_VERSION}"
    )
    changes_resp = requests.get(changes_url, headers=_headers(cfg["pat"]), timeout=15)
    changes_resp.raise_for_status()
    changes = changes_resp.json().get("changeEntries", [])

    supported_extensions = {".cs", ".ts"}
    files = []
    for change in changes:
        item = change.get("item", {})
        path = item.get("path", "")
        if any(path.endswith(ext) for ext in supported_extensions):
            change_type = change.get("changeType", "edit")
            if change_type != "delete":
                files.append({
                    "path":        path,
                    "change_type": change_type,
                })
    return files


# ── File Content ───────────────────────────────────────────────────────────────

def get_file_content(path: str, branch: str) -> str:
    """
    Fetches raw file content from the given branch.
    """
    cfg = _get_config()
    url = (
        f"{_base(cfg)}/items"
        f"?path={requests.utils.quote(path, safe='/')}"
        f"&versionDescriptor.version={branch}"
        f"&versionDescriptor.versionType=branch"
        f"&api-version={API_VERSION}"
    )
    headers = _headers(cfg["pat"])
    headers["Accept"] = "text/plain"
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.text


# ── Post Comments ──────────────────────────────────────────────────────────────

def post_inline_comment(pr_id: int, file_path: str, line: int, comment: str) -> bool:
    """
    Posts an inline comment on a specific file and line in the PR.
    Returns True on success.
    """
    cfg = _get_config()
    url = f"{_base(cfg)}/pullRequests/{pr_id}/threads?api-version={API_VERSION}"

    body = {
        "comments": [
            {
                "parentCommentId": 0,
                "content":         comment,
                "commentType":     1,
            }
        ],
        "status": "active",
        "threadContext": {
            "filePath":       file_path,
            "rightFileStart": {"line": line, "offset": 1},
            "rightFileEnd":   {"line": line, "offset": 200},
        }
    }
    resp = requests.post(url, headers=_headers(cfg["pat"]), json=body, timeout=15)
    return resp.status_code in (200, 201)


def post_pr_summary(pr_id: int, summary_text: str) -> bool:
    """
    Posts an overall summary comment (not tied to a specific file/line) on the PR.
    Returns True on success.
    """
    cfg = _get_config()
    url = f"{_base(cfg)}/pullRequests/{pr_id}/threads?api-version={API_VERSION}"

    body = {
        "comments": [
            {
                "parentCommentId": 0,
                "content":         summary_text,
                "commentType":     1,
            }
        ],
        "status": "active",
    }
    resp = requests.post(url, headers=_headers(cfg["pat"]), json=body, timeout=15)
    return resp.status_code in (200, 201)

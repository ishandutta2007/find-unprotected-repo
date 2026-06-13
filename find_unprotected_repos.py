#!/usr/bin/env python3
"""
Find all GitHub repositories that do not have any branch protection rules.

This script uses the GitHub API to identify repositories owned by the authenticated user
that do not have any branch protection configured on any of their branches.

Features:
    - Intelligent local caching (25-hour TTL) for API responses.
    - Automatic filtering of forked repositories (default: True).
    - Clear console logging for Cache vs. API fetching.

Usage:
    python find_unprotected_repos.py

Requirements:
    - requests library: pip install requests
    - python-dotenv library: pip install python-dotenv
    - tqdm library: pip install tqdm
    - .env file with ADMIN_TOKEN set
"""

import os
import sys
import json
import time
import hashlib
import argparse
from tqdm import tqdm
from dotenv import load_dotenv
import requests
from typing import List, Dict, Tuple

# Load environment variables
load_dotenv()
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN')

if not ADMIN_TOKEN:
    sys.exit(1)

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {ADMIN_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Caching configuration
CACHE_FILE = "api_cache.json"
CACHE_TTL = 25 * 3600  # 25 hours in seconds


def get_cache_key(url: str, params: Dict) -> str:
    """Generate a unique cache key for a URL and parameters."""
    key_str = f"{url}_{json.dumps(params, sort_keys=True)}"
    return hashlib.md5(key_str.encode()).hexdigest()


def load_cache() -> Dict:
    """Load the cache from the local file."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_cache(cache: Dict):
    """Save the cache to the local file."""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except IOError:
        pass


def get_paginated_results(url: str, per_page: int = 100) -> List[Dict]:
    """
    Fetch paginated results from GitHub API with local caching.
    
    Args:
        url: The API endpoint URL
        per_page: Number of results per page
        
    Returns:
        List of all results across all pages
    """
    results = []
    page = 1
    cache = load_cache()
    now = time.time()
    cache_updated = False
    
    while True:
        params = {"per_page": per_page, "page": page}
        key = get_cache_key(url, params)
        
        data = None
        if key in cache:
            entry = cache[key]
            if now - entry['timestamp'] < CACHE_TTL:
                data = entry['data']
        
        if data is None:
            response = requests.get(url, headers=HEADERS, params=params)
            
            if response.status_code != 200:
                break
            
            data = response.json()
            
            # Update cache
            cache[key] = {
                'timestamp': now,
                'data': data
            }
            cache_updated = True
        
        if not data:
            break
        
        results.extend(data)
        page += 1
    
    if cache_updated:
        save_cache(cache)
        
    return results


def get_user_repositories(ignore_forks: bool = True) -> List[Dict]:
    """
    Fetch all repositories for the authenticated user.
    
    Args:
        ignore_forks: If True, skip forked repositories
        
    Returns:
        List of repository objects
    """
    url = f"{GITHUB_API_URL}/user/repos"
    repos = get_paginated_results(url)
    
    if ignore_forks:
        repos = [r for r in repos if not r.get('fork', False)]
        
    return repos


def get_branch_protections(repo_owner: str, repo_name: str) -> List[Dict]:
    """
    Fetch all branch protection rules for a repository.
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        
    Returns:
        List of branch protection rules
    """
    url = f"{GITHUB_API_URL}/repos/{repo_owner}/{repo_name}/branches"
    branches = get_paginated_results(url)
    
    protected_branches = []
    for branch in branches:
        if branch.get('protected', False):
            protected_branches.append(branch)
    
    return protected_branches


def find_unprotected_repos(ignore_forks: bool = True):
    """
    Find all repositories without any branch protection (Generator).
    
    Args:
        ignore_forks: If True, skip forked repositories
        
    Yields:
        Dict: {"current": int, "total": int, "repo": Optional[Dict]}
    """
    repos = get_user_repositories(ignore_forks=ignore_forks)
    total = len(repos)
    
    for i, repo in enumerate(repos, 1):
        repo_owner = repo['owner']['login']
        repo_name = repo['name']
        
        unprotected_repo = None
        # Skip archived repositories
        if not repo.get('archived', False):
            try:
                protected_branches = get_branch_protections(repo_owner, repo_name)
                
                if not protected_branches:
                    unprotected_repo = repo
            except Exception:
                pass
        
        yield {
            "current": i,
            "total": total,
            "repo": unprotected_repo
        }


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="GitHub Repository Branch Protection Checker")
    parser.add_argument(
        "--ignore-forks",
        type=str2bool,
        nargs='?',
        const=True,
        default=True,
        help="Ignore forked repositories (default: True. Use --ignore-forks False to include forks)"
    )
    args = parser.parse_args()
    
    unprotected_repos = []
    try:
        # We need to get the generator to start it
        generator = find_unprotected_repos(ignore_forks=args.ignore_forks)
        
        pbar = None
        for step in generator:
            if pbar is None:
                pbar = tqdm(total=step['total'], desc="Scanning repositories", unit="repo", file=sys.stderr)
            
            pbar.update(1)
            if step['repo']:
                unprotected_repos.append(step['repo'])
                pbar.write(step['repo']['html_url'])
        
        if pbar:
            pbar.close()
            
        # Exit with appropriate code
        if unprotected_repos:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()

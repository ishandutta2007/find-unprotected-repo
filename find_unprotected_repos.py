#!/usr/bin/env python3
"""
Find all GitHub repositories that do not have any branch protection rules.

This script uses the GitHub API to identify repositories owned by the authenticated user
that do not have any branch protection configured on any of their branches.

Usage:
    python find_unprotected_repos.py

Requirements:
    - requests library: pip install requests
    - .env file with ADMIN_TOKEN set
"""

import os
import sys
from dotenv import load_dotenv
import requests
from typing import List, Dict, Tuple

# Load environment variables
load_dotenv()
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN')

if not ADMIN_TOKEN:
    print("ERROR: ADMIN_TOKEN not found in .env file")
    sys.exit(1)

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {ADMIN_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


def get_paginated_results(url: str, per_page: int = 100) -> List[Dict]:
    """
    Fetch paginated results from GitHub API.
    
    Args:
        url: The API endpoint URL
        per_page: Number of results per page
        
    Returns:
        List of all results across all pages
    """
    results = []
    page = 1
    
    while True:
        params = {"per_page": per_page, "page": page}
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code != 200:
            print(f"ERROR: Failed to fetch from {url}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            break
        
        data = response.json()
        
        if not data:
            break
        
        results.extend(data)
        page += 1
    
    return results


def get_user_repositories() -> List[Dict]:
    """
    Fetch all repositories for the authenticated user.
    
    Returns:
        List of repository objects
    """
    print("Fetching repositories...")
    url = f"{GITHUB_API_URL}/user/repos"
    repos = get_paginated_results(url)
    print(f"Found {len(repos)} repositories")
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


def find_unprotected_repos() -> Tuple[List[Dict], int]:
    """
    Find all repositories without any branch protection.
    
    Returns:
        Tuple containing (list of unprotected repos, total repos checked)
    """
    repos = get_user_repositories()
    unprotected_repos = []
    
    print("\nChecking branch protection for each repository...\n")
    
    for i, repo in enumerate(repos, 1):
        repo_owner = repo['owner']['login']
        repo_name = repo['name']
        
        print(f"[{i}/{len(repos)}] Checking {repo_owner}/{repo_name}...", end=" ")
        
        # Skip archived repositories
        if repo.get('archived', False):
            print("SKIPPED (archived)")
            continue
        
        try:
            protected_branches = get_branch_protections(repo_owner, repo_name)
            
            if not protected_branches:
                print("⚠️  UNPROTECTED")
                unprotected_repos.append(repo)
            else:
                print(f"✓ Protected ({len(protected_branches)} branch(es) protected)")
        except Exception as e:
            print(f"ERROR ({str(e)})")
    
    return unprotected_repos, len(repos)


def print_results(unprotected_repos: List[Dict], total_repos: int):
    """
    Print the results in a formatted way.
    
    Args:
        unprotected_repos: List of unprotected repositories
        total_repos: Total number of repositories checked
    """
    print("\n" + "="*80)
    print(f"SUMMARY: {len(unprotected_repos)}/{total_repos} repositories are UNPROTECTED")
    print("="*80 + "\n")
    
    if unprotected_repos:
        print("Unprotected Repositories:\n")
        for i, repo in enumerate(unprotected_repos, 1):
            print(f"{i}. {repo['full_name']}")
            print(f"   URL: {repo['html_url']}")
            print(f"   Private: {repo['private']}")
            print(f"   Default Branch: {repo['default_branch']}")
            print()
    else:
        print("✓ All repositories have branch protection configured!")


def main():
    """Main entry point."""
    print("GitHub Repository Branch Protection Checker")
    print("="*80 + "\n")
    
    try:
        unprotected_repos, total_repos = find_unprotected_repos()
        print_results(unprotected_repos, total_repos)
        
        # Exit with appropriate code
        if unprotected_repos:
            print(f"\n⚠️  Action Required: {len(unprotected_repos)} repository/repositories need branch protection!")
            sys.exit(1)
        else:
            print("\n✓ All repositories are protected!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

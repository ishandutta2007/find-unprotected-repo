# Find Unprotected Repos

Find all your GitHub repositories that have not been protected with branch protection rules.

This tool helps identify repositories without any branch protection configured, ensuring your codebase is secure and follows best practices.

## Features

- ✅ **Identifies unprotected repositories** - Finds all repos without branch protection rules
- ✅ **Handles pagination** - Works with large numbers of repositories
- ✅ **Skips archived repos** - Automatically ignores archived repositories
- ✅ **Detailed reporting** - Shows repository URLs, privacy status, and default branch
- ✅ **Progress tracking** - Visual indicators during scanning
- ✅ **CI/CD ready** - Exit codes for automation (0 = all protected, 1 = unprotected repos found)

## Installation

### Prerequisites

- Python 3.6 or higher
- `pip` package manager
- A GitHub Personal Access Token with admin permissions

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ishandutta2007/find-unprotected-repo.git
   cd find-unprotected-repo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Or manually install:
   ```bash
   pip install requests python-dotenv
   ```

3. **Create your `.env` file**
   ```bash
   cp .env.example .env
   ```

## Configuration

### Setting up your GitHub Personal Access Token

The script requires a GitHub Personal Access Token (PAT) with appropriate permissions.

**Step-by-Step to generate it:**

1. **Open GitHub Settings**: Go to your [Fine-grained Personal Access Tokens](https://github.com/settings/tokens?type=beta) page.

2. **Edit the Token**: Click on the name of the token you are using.

3. **Repository Access**: Look for the Repository access section near the top.
   - Select "Only select repositories"
   - Click the "Select repositories" dropdown
   - Search for and check the box next to the specific repo you want to use

4. **Verify Administration**: Scroll down to Permissions → Repository permissions.
   - Find "Administration"
   - Ensure it is set to "Read and Write"

5. **Save**: Click the "Update token" button at the bottom of the page.

6. **Add to `.env`**: Copy your token and add it to the `.env` file:
   ```
   ADMIN_TOKEN=github_pat_<your_token_here>
   ```

## Usage

### Run the script

```bash
python find_unprotected_repos.py
```

### Output Example

The script will display progress as it checks each repository:

```
GitHub Repository Branch Protection Checker
================================================================================

Fetching repositories...
Found 25 repositories

Checking branch protection for each repository...

[1/25] Checking username/repo1... ✓ Protected (1 branch(es) protected)
[2/25] Checking username/repo2... ⚠️  UNPROTECTED
[3/25] Checking username/repo3... SKIPPED (archived)
...

================================================================================
SUMMARY: 3/25 repositories are UNPROTECTED
================================================================================

Unprotected Repositories:

1. username/repo2
   URL: https://github.com/username/repo2
   Private: false
   Default Branch: main

2. username/repo4
   URL: https://github.com/username/repo4
   Private: true
   Default Branch: master

3. username/repo5
   URL: https://github.com/username/repo5
   Private: false
   Default Branch: develop

⚠️  Action Required: 3 repository/repositories need branch protection!
```

## Exit Codes

- `0` - Success: All repositories have branch protection configured
- `1` - Warning: One or more repositories are unprotected
- `130` - Interrupted: User cancelled the script
- Other codes - Error occurred during execution

## Use Cases

### Manual checks
```bash
python find_unprotected_repos.py
```

### Integration with CI/CD
```bash
python find_unprotected_repos.py || echo "Unprotected repos found!"
```

### Scheduled checks
Set up a cron job or GitHub Action to run this script regularly:
```bash
0 0 * * 0 cd /path/to/find-unprotected-repo && python find_unprotected_repos.py
```

## Troubleshooting

### "ERROR: ADMIN_TOKEN not found in .env file"
- Make sure you have created the `.env` file (copy from `.env.example`)
- Verify your GitHub Personal Access Token is correctly set in the file
- Check that the `.env` file is in the same directory as the script

### "Failed to fetch from GitHub API"
- Verify your token has the correct permissions (Administration: Read and Write)
- Check that your token hasn't expired
- Ensure you have internet connectivity

### "Status Code: 401"
- Your token is invalid or expired
- Generate a new Personal Access Token and update your `.env` file

### "Status Code: 403"
- Your token doesn't have the required permissions
- Follow the "Repository Access" and "Verify Administration" steps above
- Regenerate the token with correct permissions

## Repository Protection Best Practices

Once you identify unprotected repositories, consider implementing:

1. **Require pull request reviews** - Enforce code review before merging
2. **Dismiss stale pull request approvals** - Require fresh approvals when code changes
3. **Require status checks to pass** - Ensure CI/CD pipelines pass before merging
4. **Require branches to be up to date** - Prevent merging outdated branches
5. **Restrict who can push** - Limit push access to specific users/teams
6. **Require signed commits** - Enforce commit signing for security

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have suggestions, please open an [issue](https://github.com/ishandutta2007/find-unprotected-repo/issues).

---

**Note**: Always ensure your Personal Access Token is kept secure and never commit it to version control. Use `.env` files and add them to `.gitignore`.

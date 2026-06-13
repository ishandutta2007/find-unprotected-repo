<div align="center">

# 🛡️ GitHub Repository Branch Protection Checker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub API](https://img.shields.io/badge/GitHub%20API-v3-orange.svg)](https://docs.github.com/en/rest)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

### *Automate security audits for your GitHub repositories in seconds.*

---

<!-- Simple SVG Banner -->
<svg width="800" height="200" viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0d1117;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#161b22;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="800" height="200" rx="10" fill="url(#grad1)" />
  <text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial" font-size="32" fill="#58a6ff" font-weight="bold">🛡️ Find Unprotected Repos</text>
  <text x="50%" y="65%" dominant-baseline="middle" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial" font-size="16" fill="#8b949e">Intelligent Caching • Fork Filtering • Security Auditing</text>
  <path d="M350 140 L450 140" stroke="#238636" stroke-width="4" stroke-linecap="round" />
</svg>

</div>

## 📖 Overview

**Find Unprotected Repos** is a high-performance security tool designed for GitHub power users and organizations. It scans your repositories to identify those lacking **Branch Protection Rules**, helping you prevent accidental deletions or unreviewed code merges.

### ✨ Key Features

- **🚀 Intelligent API Caching:** Built-in local cache with a **25-hour TTL** to minimize GitHub API rate limiting and boost performance.
- **🍴 Fork Filtering:** Automatically ignores forked repositories by default, focusing your audit on original source code.
- **🔍 Deep Scan:** Checks every branch of every repository for `protected` status.
- **📟 Rich CLI Output:** Clearly distinguishes between Cache Hits and real-time API calls.
- **✅ Archived Safety:** Automatically skips archived repositories to keep results relevant.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- A GitHub [Personal Access Token (classic)](https://github.com/settings/tokens) with `repo` scope.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/ishandutta2007/find-unprotected-repo.git
cd find-unprotected-repo

# Install dependencies
pip install requests python-dotenv tqdm
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
ADMIN_TOKEN=your_github_personal_access_token
```

---

## 🛠️ Usage

Simply run the script to start the audit:

```bash
python find_unprotected_repos.py
```

### ⚙️ Command Line Options

| Option | Description | Default |
| :--- | :--- | :--- |
| `--ignore-forks` | Whether to skip forked repositories. Use `False` to include them. | `True` |

**Example: Include forks in the audit**
```bash
python find_unprotected_repos.py --ignore-forks False
```

### ⚙️ How it works
1. **Fetch:** Retrieves all your repositories.
2. **Filter:** Skips forks (default) and archived repos.
3. **Audit:** Checks branch protection status.
4. **Cache:** Stores results in `api_cache.json` for 25 hours.

### 🧩 Logic Details
- **Cache TTL:** `25 hours`. If data is older, a fresh API call is made.

---

## 📊 Sample Output

```text
Scanning repositories: 100%|██████████| 150/150 [00:45<00:00,  3.33repo/s]
https://github.com/user/unsecured-repo
https://github.com/user/another-unprotected-project
```

---

## 🛡️ Security & Privacy
- **Local Cache:** All API data is stored locally in `api_cache.json`.
- **Token Safety:** Your `ADMIN_TOKEN` is loaded from `.env` and never logged or cached.

---

## 🤝 Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

---

<div align="center">
  <sub>Built with ❤️ for a safer GitHub ecosystem.</sub>
</div>

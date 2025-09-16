# Repository Secret Scanner

This directory contains scripts to scan your GitHub repositories for accidentally committed secrets using gitleaks.

## 🚨 Important Security Note

**Before running these scripts, ensure you have the necessary permissions to clone and scan these repositories.**

## Prerequisites

### Required Tools

1. **gitleaks** - Secret detection tool
   ```bash
   # macOS
   brew install gitleaks
   
   # Or download from: https://github.com/gitleaks/gitleaks/releases
   ```

2. **git** - Version control system
   ```bash
   # Usually pre-installed, or install from: https://git-scm.com/downloads
   ```

3. **jq** (for bash script) - JSON processor
   ```bash
   # macOS
   brew install jq
   ```

## Available Scripts

### 1. Bash Script (`scan_repos.sh`)
- **Features**: Comprehensive scanning with colored output, detailed reporting
- **Requirements**: bash, gitleaks, git, jq
- **Usage**: `./scan_repos.sh`

### 2. Python Script (`scan_repos.py`)
- **Features**: Cross-platform, detailed error handling, JSON processing
- **Requirements**: Python 3.6+, gitleaks, git
- **Usage**: `python3 scan_repos.py`

## Repositories Being Scanned

The scripts will scan the following repositories:

1. https://github.com/AlwaysUbaid/AlgoHL
2. https://github.com/AlwaysUbaid/hummingbot-ubaid
3. https://github.com/AlwaysUbaid/MarketMakingMegaMachine
4. https://github.com/AlwaysUbaid/market-making-gabrielee5
5. https://github.com/AlwaysUbaid/avail-dune-analytics
6. https://github.com/AlwaysUbaid/HyperCore-Wallet-Tracker

## What Gets Detected

Gitleaks will scan for various types of secrets including:

- **API Keys**: AWS, Google Cloud, Azure, etc.
- **Tokens**: GitHub, GitLab, Slack, Discord, etc.
- **Database Credentials**: Connection strings, passwords
- **Private Keys**: SSH keys, certificates
- **Other Secrets**: Passwords, API secrets, etc.

## Running the Scan

### Option 1: Bash Script
```bash
cd /Users/ubaid/gitleaks
./scan_repos.sh
```

### Option 2: Python Script
```bash
cd /Users/ubaid/gitleaks
python3 scan_repos.py
```

## Output

The scripts will:

1. **Clone each repository** to a temporary directory
2. **Scan for secrets** using gitleaks
3. **Generate detailed reports** in JSON format
4. **Provide a summary** of findings
5. **Create a final report** with all results

### Sample Output

```
🔍 Gitleaks Repository Scanner
================================
Scanning 6 repositories for secrets...

📁 Scanning: AlgoHL
✅ Clean: AlgoHL (no secrets found)

📁 Scanning: hummingbot-ubaid
🚨 SECRETS FOUND: hummingbot-ubaid (3 findings)
   📄 Report saved to: /tmp/gitleaks_scan_xxx/hummingbot-ubaid_gitleaks_report.json
   🔍 Findings summary:
   • aws-access-key: AWS Access Key (File: config.py, Line: 15)
   • github-pat: GitHub Personal Access Token (File: .env, Line: 3)
   • generic-api-key: Generic API Key (File: secrets.json, Line: 8)

📊 SCAN SUMMARY
===============
Total Repositories: 6
Successfully Scanned: 6
Repositories with Secrets: 1
Total Secret Findings: 3
```

## Understanding Results

### Clean Repository ✅
- No secrets detected
- Repository is safe

### Secrets Found 🚨
- **Immediate Action Required**:
  1. Review the detailed JSON report
  2. Determine if findings are real secrets or false positives
  3. If real secrets are found:
     - **Rotate/revoke** the compromised credentials immediately
     - **Remove secrets** from git history
     - **Update** your secrets management practices

## Report Files

After scanning, you'll find:

- `{repo_name}_gitleaks_report.json` - Detailed findings for each repo
- `final_report.txt` - Summary report
- All files are saved in a temporary directory

## Security Best Practices

1. **Never commit real secrets** to version control
2. **Use environment variables** for configuration
3. **Implement pre-commit hooks** with gitleaks
4. **Regular scanning** of repositories
5. **Rotate credentials** if secrets are found

## Troubleshooting

### Common Issues

1. **"gitleaks not found"**
   - Install gitleaks: `brew install gitleaks`

2. **"jq not found"** (bash script only)
   - Install jq: `brew install jq`

3. **"Permission denied" cloning repos**
   - Ensure you have access to the repositories
   - Check your GitHub authentication

4. **Timeout errors**
   - Large repositories may take time to clone
   - Check your internet connection

### Getting Help

- Check gitleaks documentation: https://github.com/gitleaks/gitleaks
- Review the generated JSON reports for detailed findings
- Consider running gitleaks manually on individual repos for debugging

## Next Steps

After running the scan:

1. **Review all findings** carefully
2. **Take immediate action** on any real secrets found
3. **Set up prevention** measures:
   - Pre-commit hooks
   - CI/CD integration
   - Regular scanning schedule
4. **Update your workflow** to prevent future secret commits

---

**Remember**: Security is an ongoing process. Regular scanning and good practices are essential for maintaining repository security.

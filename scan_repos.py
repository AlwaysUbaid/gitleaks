#!/usr/bin/env python3
"""
Gitleaks Repository Scanner
Scans multiple GitHub repositories for accidentally committed secrets
"""

import os
import sys
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Tuple

# Color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

# Repository URLs to scan
REPOSITORIES = [
    "https://github.com/AlwaysUbaid/AlgoHL",
    "https://github.com/AlwaysUbaid/hummingbot-ubaid", 
    "https://github.com/AlwaysUbaid/MarketMakingMegaMachine",
    "https://github.com/AlwaysUbaid/market-making-gabrielee5",
    "https://github.com/AlwaysUbaid/avail-dune-analytics",
    "https://github.com/AlwaysUbaid/HyperCore-Wallet-Tracker"
]

class GitleaksScanner:
    def __init__(self):
        self.temp_dir = None
        self.results = []
        self.total_findings = 0
        self.repos_with_secrets = 0
        
    def check_dependencies(self) -> bool:
        """Check if required tools are installed"""
        required_tools = ['gitleaks', 'git']
        missing_tools = []
        
        for tool in required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"{Colors.RED}❌ Missing required tools: {', '.join(missing_tools)}{Colors.NC}")
            print(f"{Colors.YELLOW}Please install missing tools:{Colors.NC}")
            for tool in missing_tools:
                if tool == 'gitleaks':
                    print("  macOS: brew install gitleaks")
                    print("  Or download from: https://github.com/gitleaks/gitleaks/releases")
                elif tool == 'git':
                    print("  Install Git from: https://git-scm.com/downloads")
            return False
        
        return True
    
    def setup_temp_directory(self):
        """Create temporary directory for cloning repositories"""
        self.temp_dir = tempfile.mkdtemp(prefix="gitleaks_scan_")
        print(f"{Colors.BLUE}📁 Temporary directory: {self.temp_dir}{Colors.NC}")
    
    def clone_repository(self, repo_url: str) -> Tuple[bool, str]:
        """Clone a repository to temporary directory"""
        repo_name = repo_url.split('/')[-1]
        repo_path = os.path.join(self.temp_dir, repo_name)
        
        try:
            # Clone with depth 1 for faster cloning
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, repo_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return True, repo_path
            else:
                print(f"{Colors.RED}❌ Failed to clone {repo_name}: {result.stderr}{Colors.NC}")
                return False, ""
                
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}❌ Timeout cloning {repo_name}{Colors.NC}")
            return False, ""
        except Exception as e:
            print(f"{Colors.RED}❌ Error cloning {repo_name}: {str(e)}{Colors.NC}")
            return False, ""
    
    def scan_repository(self, repo_path: str, repo_url: str) -> Dict:
        """Scan a single repository with gitleaks"""
        repo_name = os.path.basename(repo_path)
        report_file = os.path.join(self.temp_dir, f"{repo_name}_report.json")
        
        print(f"{Colors.YELLOW}📁 Scanning: {repo_name}{Colors.NC}")
        
        try:
            # Run gitleaks scan
            result = subprocess.run([
                'gitleaks', 'git',
                '--report-path', report_file,
                '--report-format', 'json',
                '--no-banner',
                repo_path
            ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
            
            # Check if report was created and has content
            findings = []
            findings_count = 0
            
            if os.path.exists(report_file) and os.path.getsize(report_file) > 0:
                try:
                    with open(report_file, 'r') as f:
                        findings = json.load(f)
                    findings_count = len(findings)
                except json.JSONDecodeError:
                    findings_count = 0
            
            result_data = {
                'repo_name': repo_name,
                'repo_url': repo_url,
                'repo_path': repo_path,
                'report_file': report_file,
                'findings': findings,
                'findings_count': findings_count,
                'success': True,
                'error': None
            }
            
            if findings_count > 0:
                print(f"{Colors.RED}🚨 SECRETS FOUND: {repo_name} ({findings_count} findings){Colors.NC}")
                print(f"{Colors.RED}   📄 Report: {report_file}{Colors.NC}")
                
                # Show summary of findings
                print(f"{Colors.RED}   🔍 Findings summary:{Colors.NC}")
                for finding in findings[:5]:  # Show first 5 findings
                    rule_id = finding.get('ruleID', 'Unknown')
                    description = finding.get('description', 'No description')
                    file_path = finding.get('file', 'Unknown file')
                    line = finding.get('startLine', 'Unknown line')
                    print(f"   • {rule_id}: {description} (File: {file_path}, Line: {line})")
                
                if findings_count > 5:
                    print(f"   • ... and {findings_count - 5} more findings")
                
                self.repos_with_secrets += 1
                self.total_findings += findings_count
            else:
                print(f"{Colors.GREEN}✅ Clean: {repo_name} (no secrets found){Colors.NC}")
            
            return result_data
            
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout scanning {repo_name}"
            print(f"{Colors.RED}❌ {error_msg}{Colors.NC}")
            return {
                'repo_name': repo_name,
                'repo_url': repo_url,
                'repo_path': repo_path,
                'report_file': report_file,
                'findings': [],
                'findings_count': 0,
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Error scanning {repo_name}: {str(e)}"
            print(f"{Colors.RED}❌ {error_msg}{Colors.NC}")
            return {
                'repo_name': repo_name,
                'repo_url': repo_url,
                'repo_path': repo_path,
                'report_file': report_file,
                'findings': [],
                'findings_count': 0,
                'success': False,
                'error': error_msg
            }
    
    def generate_final_report(self):
        """Generate a comprehensive final report"""
        report_file = os.path.join(self.temp_dir, "final_report.txt")
        
        with open(report_file, 'w') as f:
            f.write("GITLEAKS SCAN FINAL REPORT\n")
            f.write("=========================\n")
            f.write(f"Scan Date: {self.get_timestamp()}\n")
            f.write(f"Total Repositories: {len(REPOSITORIES)}\n")
            f.write(f"Successfully Scanned: {len([r for r in self.results if r['success']])}\n")
            f.write(f"Repositories with Secrets: {self.repos_with_secrets}\n")
            f.write(f"Total Secret Findings: {self.total_findings}\n\n")
            
            if self.repos_with_secrets > 0:
                f.write("🚨 REPOSITORIES WITH SECRETS FOUND:\n")
                f.write("===================================\n\n")
                
                for result in self.results:
                    if result['findings_count'] > 0:
                        f.write(f"Repository: {result['repo_name']}\n")
                        f.write(f"URL: {result['repo_url']}\n")
                        f.write(f"Findings: {result['findings_count']}\n")
                        f.write(f"Report: {result['report_file']}\n")
                        f.write("---\n\n")
            else:
                f.write("✅ ALL REPOSITORIES ARE CLEAN!\n")
                f.write("No secrets were found in any of the scanned repositories.\n")
        
        print(f"\n{Colors.BLUE}📋 Final report saved to: {report_file}{Colors.NC}")
        return report_file
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def cleanup(self, keep_files: bool = False):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            if keep_files:
                print(f"{Colors.BLUE}📁 Temporary files kept in: {self.temp_dir}{Colors.NC}")
            else:
                print(f"{Colors.YELLOW}🧹 Cleaning up temporary files...{Colors.NC}")
                shutil.rmtree(self.temp_dir)
                print(f"{Colors.GREEN}✅ Cleanup complete!{Colors.NC}")
    
    def run_scan(self):
        """Main method to run the complete scan"""
        print(f"{Colors.BLUE}🔍 Gitleaks Repository Scanner{Colors.NC}")
        print(f"{Colors.BLUE}================================{Colors.NC}")
        print(f"Scanning {len(REPOSITORIES)} repositories for secrets...")
        print()
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Setup
        self.setup_temp_directory()
        
        # Scan each repository
        print(f"{Colors.BLUE}Starting repository scans...{Colors.NC}")
        print()
        
        for repo_url in REPOSITORIES:
            # Clone repository
            success, repo_path = self.clone_repository(repo_url)
            if not success:
                continue
            
            # Scan repository
            result = self.scan_repository(repo_path, repo_url)
            self.results.append(result)
            print()
        
        # Generate final report
        self.generate_final_report()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print scan summary"""
        print(f"{Colors.BLUE}📊 SCAN SUMMARY{Colors.NC}")
        print(f"{Colors.BLUE}==============={Colors.NC}")
        print(f"Total Repositories: {len(REPOSITORIES)}")
        print(f"Successfully Scanned: {len([r for r in self.results if r['success']])}")
        print(f"Repositories with Secrets: {self.repos_with_secrets}")
        print(f"Total Secret Findings: {self.total_findings}")
        print()
        
        if self.repos_with_secrets == 0:
            print(f"{Colors.GREEN}🎉 CONGRATULATIONS! All your repositories are clean!{Colors.NC}")
            print(f"{Colors.GREEN}No secrets were found in any of the scanned repositories.{Colors.NC}")
        else:
            print(f"{Colors.RED}⚠️  WARNING: Secrets were found in {self.repos_with_secrets} repository(ies)!{Colors.NC}")
            print(f"{Colors.RED}Please review the detailed reports and take immediate action.{Colors.NC}")
            print()
            print(f"{Colors.YELLOW}🔧 Recommended Actions:{Colors.NC}")
            print("1. Review each finding in the detailed reports")
            print("2. Determine if the secrets are real or false positives")
            print("3. If real secrets are found:")
            print("   - Rotate/revoke the compromised credentials immediately")
            print("   - Remove the secrets from git history (git filter-branch or BFG)")
            print("   - Update your secrets management practices")
            print("4. Consider setting up gitleaks as a pre-commit hook")

def main():
    """Main entry point"""
    scanner = GitleaksScanner()
    
    try:
        success = scanner.run_scan()
        
        if success:
            # Ask if user wants to keep temp files
            print()
            keep_files = input("Do you want to keep the temporary files for review? (y/n): ").lower().startswith('y')
            scanner.cleanup(keep_files=keep_files)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Scan interrupted by user{Colors.NC}")
        scanner.cleanup()
        return 1
    except Exception as e:
        print(f"{Colors.RED}❌ Unexpected error: {str(e)}{Colors.NC}")
        scanner.cleanup()
        return 1

if __name__ == "__main__":
    sys.exit(main())

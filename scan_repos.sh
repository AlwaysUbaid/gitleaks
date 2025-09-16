#!/bin/bash

# Gitleaks Repository Scanner
# This script scans multiple GitHub repositories for accidentally committed secrets
# Author: AI Assistant
# Date: $(date)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPOS=(
    "https://github.com/AlwaysUbaid/AlgoHL"
    "https://github.com/AlwaysUbaid/hummingbot-ubaid"
    "https://github.com/AlwaysUbaid/MarketMakingMegaMachine"
    "https://github.com/AlwaysUbaid/market-making-gabrielee5"
    "https://github.com/AlwaysUbaid/avail-dune-analytics"
    "https://github.com/AlwaysUbaid/HyperCore-Wallet-Tracker"
)

# Create temporary directory for cloning repos
TEMP_DIR="/tmp/gitleaks_scan_$(date +%s)"
mkdir -p "$TEMP_DIR"

# Results tracking
TOTAL_REPOS=${#REPOS[@]}
SCANNED_REPOS=0
REPOS_WITH_SECRETS=0
TOTAL_FINDINGS=0

echo -e "${BLUE}🔍 Gitleaks Repository Scanner${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "Scanning ${TOTAL_REPOS} repositories for secrets..."
echo -e "Temporary directory: ${TEMP_DIR}"
echo ""

# Function to print status
print_status() {
    local status=$1
    local repo_name=$2
    local findings=$3
    
    case $status in
        "scanning")
            echo -e "${YELLOW}📁 Scanning: ${repo_name}${NC}"
            ;;
        "clean")
            echo -e "${GREEN}✅ Clean: ${repo_name} (no secrets found)${NC}"
            ;;
        "secrets_found")
            echo -e "${RED}🚨 SECRETS FOUND: ${repo_name} (${findings} findings)${NC}"
            ;;
        "error")
            echo -e "${RED}❌ Error: ${repo_name}${NC}"
            ;;
    esac
}

# Function to scan a single repository
scan_repo() {
    local repo_url=$1
    local repo_name=$(basename "$repo_url")
    local repo_dir="$TEMP_DIR/$repo_name"
    
    print_status "scanning" "$repo_name"
    
    # Clone the repository
    if ! git clone --depth 1 "$repo_url" "$repo_dir" 2>/dev/null; then
        print_status "error" "$repo_name"
        return 1
    fi
    
    # Run gitleaks scan
    cd "$repo_dir"
    
    # Create a report file for this repo
    local report_file="$TEMP_DIR/${repo_name}_gitleaks_report.json"
    
    # Run gitleaks with JSON output
    if gitleaks git --report-path "$report_file" --report-format json --no-banner . 2>/dev/null; then
        # Check if any findings were reported
        if [ -f "$report_file" ] && [ -s "$report_file" ]; then
            local findings_count=$(jq length "$report_file" 2>/dev/null || echo "0")
            if [ "$findings_count" -gt 0 ]; then
                print_status "secrets_found" "$repo_name" "$findings_count"
                echo -e "${RED}   📄 Report saved to: ${report_file}${NC}"
                
                # Show summary of findings
                echo -e "${RED}   🔍 Findings summary:${NC}"
                jq -r '.[] | "   • \(.ruleID): \(.description) (File: \(.file), Line: \(.startLine))"' "$report_file" 2>/dev/null || echo "   • Unable to parse findings"
                
                ((REPOS_WITH_SECRETS++))
                ((TOTAL_FINDINGS += findings_count))
            else
                print_status "clean" "$repo_name"
            fi
        else
            print_status "clean" "$repo_name"
        fi
    else
        print_status "error" "$repo_name"
        return 1
    fi
    
    ((SCANNED_REPOS++))
    cd - > /dev/null
}

# Function to generate final report
generate_final_report() {
    local final_report="$TEMP_DIR/final_report.txt"
    
    echo "GITLEAKS SCAN FINAL REPORT" > "$final_report"
    echo "=========================" >> "$final_report"
    echo "Scan Date: $(date)" >> "$final_report"
    echo "Total Repositories: $TOTAL_REPOS" >> "$final_report"
    echo "Successfully Scanned: $SCANNED_REPOS" >> "$final_report"
    echo "Repositories with Secrets: $REPOS_WITH_SECRETS" >> "$final_report"
    echo "Total Secret Findings: $TOTAL_FINDINGS" >> "$final_report"
    echo "" >> "$final_report"
    
    if [ $REPOS_WITH_SECRETS -gt 0 ]; then
        echo "🚨 REPOSITORIES WITH SECRETS FOUND:" >> "$final_report"
        echo "===================================" >> "$final_report"
        
        for repo_url in "${REPOS[@]}"; do
            local repo_name=$(basename "$repo_url")
            local report_file="$TEMP_DIR/${repo_name}_gitleaks_report.json"
            
            if [ -f "$report_file" ] && [ -s "$report_file" ]; then
                local findings_count=$(jq length "$report_file" 2>/dev/null || echo "0")
                if [ "$findings_count" -gt 0 ]; then
                    echo "" >> "$final_report"
                    echo "Repository: $repo_name" >> "$final_report"
                    echo "URL: $repo_url" >> "$final_report"
                    echo "Findings: $findings_count" >> "$final_report"
                    echo "Report: $report_file" >> "$final_report"
                    echo "---" >> "$final_report"
                fi
            fi
        done
    else
        echo "✅ ALL REPOSITORIES ARE CLEAN!" >> "$final_report"
        echo "No secrets were found in any of the scanned repositories." >> "$final_report"
    fi
    
    echo ""
    echo -e "${BLUE}📋 Final report saved to: ${final_report}${NC}"
}

# Main execution
echo -e "${BLUE}Starting repository scans...${NC}"
echo ""

# Check if gitleaks is installed
if ! command -v gitleaks &> /dev/null; then
    echo -e "${RED}❌ Error: gitleaks is not installed or not in PATH${NC}"
    echo -e "${YELLOW}Please install gitleaks first:${NC}"
    echo "  macOS: brew install gitleaks"
    echo "  Or download from: https://github.com/gitleaks/gitleaks/releases"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ Error: jq is not installed or not in PATH${NC}"
    echo -e "${YELLOW}Please install jq first:${NC}"
    echo "  macOS: brew install jq"
    exit 1
fi

# Scan each repository
for repo_url in "${REPOS[@]}"; do
    scan_repo "$repo_url"
    echo ""
done

# Generate final report
generate_final_report

# Print summary
echo -e "${BLUE}📊 SCAN SUMMARY${NC}"
echo -e "${BLUE}===============${NC}"
echo -e "Total Repositories: ${TOTAL_REPOS}"
echo -e "Successfully Scanned: ${SCANNED_REPOS}"
echo -e "Repositories with Secrets: ${REPOS_WITH_SECRETS}"
echo -e "Total Secret Findings: ${TOTAL_FINDINGS}"
echo ""

if [ $REPOS_WITH_SECRETS -eq 0 ]; then
    echo -e "${GREEN}🎉 CONGRATULATIONS! All your repositories are clean!${NC}"
    echo -e "${GREEN}No secrets were found in any of the scanned repositories.${NC}"
else
    echo -e "${RED}⚠️  WARNING: Secrets were found in ${REPOS_WITH_SECRETS} repository(ies)!${NC}"
    echo -e "${RED}Please review the detailed reports and take immediate action.${NC}"
    echo ""
    echo -e "${YELLOW}🔧 Recommended Actions:${NC}"
    echo "1. Review each finding in the detailed reports"
    echo "2. Determine if the secrets are real or false positives"
    echo "3. If real secrets are found:"
    echo "   - Rotate/revoke the compromised credentials immediately"
    echo "   - Remove the secrets from git history (git filter-branch or BFG)"
    echo "   - Update your secrets management practices"
    echo "4. Consider setting up gitleaks as a pre-commit hook"
fi

echo ""
echo -e "${BLUE}📁 All reports and temporary files are saved in: ${TEMP_DIR}${NC}"
echo -e "${YELLOW}💡 Tip: You can review individual reports or clean up the temp directory when done.${NC}"

# Ask if user wants to clean up temp directory
echo ""
read -p "Do you want to keep the temporary files for review? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🧹 Cleaning up temporary files...${NC}"
    rm -rf "$TEMP_DIR"
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
else
    echo -e "${BLUE}📁 Temporary files kept in: ${TEMP_DIR}${NC}"
fi

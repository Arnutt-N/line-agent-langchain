#!/usr/bin/env python3
"""
Security validation script to check for secrets before git operations.
Run this before any git add/commit operations.
"""

import re
import os
import sys
import glob
from pathlib import Path

# Secret patterns to detect
SECRET_PATTERNS = [
    r'AIzaSy[A-Za-z0-9_-]{33}',  # Google API keys
    r'sk-[A-Za-z0-9]{32,}',      # OpenAI API keys
    r'xoxb-[A-Za-z0-9-]+',       # Slack Bot tokens
    r'[A-Fa-f0-9]{32}',          # 32-char hex (like LINE secrets)
    r'(api_key|API_KEY|secret|SECRET|token|TOKEN|password|PASSWORD)\s*[:=]\s*[^\s\n]{10,}',
]

# Files to ignore
IGNORE_PATTERNS = [
    '.git/',
    '__pycache__/',
    'node_modules/',
    '.venv/',
    'env/',
    'venv/',
    '.secrets.baseline',
    'validate-commit.py',  # This file itself
    '.claude/',
    'projectLogMD/',
    'scripts/debugging/',
    'scripts/testing/',
    'scripts/checks/',
]

def should_ignore_file(filepath):
    """Check if file should be ignored."""
    for pattern in IGNORE_PATTERNS:
        if pattern in filepath:
            return True
    return False

def scan_file_for_secrets(filepath):
    """Scan a single file for potential secrets."""
    if should_ignore_file(filepath):
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except (UnicodeDecodeError, IOError):
        return []  # Skip binary or unreadable files
    
    secrets_found = []
    for pattern in SECRET_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            secrets_found.append({
                'file': filepath,
                'line': line_num,
                'pattern': pattern,
                'match': match.group()[:20] + '...' if len(match.group()) > 20 else match.group()
            })
    
    return secrets_found

def scan_directory(directory='.'):
    """Scan entire directory for secrets."""
    all_secrets = []
    
    for root, dirs, files in os.walk(directory):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if not any(ignore in os.path.join(root, d) for ignore in IGNORE_PATTERNS)]
        
        for file in files:
            filepath = os.path.join(root, file)
            secrets = scan_file_for_secrets(filepath)
            all_secrets.extend(secrets)
    
    return all_secrets

def check_dangerous_files():
    """Check for files that should never be committed."""
    dangerous_patterns = [
        'phase_*_complete.md',
        'phase_*_report.md',
        '*SECURITY_INCIDENT*',
        '*.env',
        'secrets.json',
        'config.json',
        'credentials.json',
    ]
    
    dangerous_files = []
    for pattern in dangerous_patterns:
        matches = glob.glob(pattern, recursive=True)
        dangerous_files.extend(matches)
    
    return dangerous_files

def main():
    """Main validation function."""
    print("Scanning for secrets and dangerous files...")
    
    # Check for secrets
    secrets = scan_directory()
    
    # Check for dangerous files
    dangerous_files = check_dangerous_files()
    
    if secrets:
        print("SECRETS DETECTED:")
        for secret in secrets:
            print(f"  BLOCKED: {secret['file']}:{secret['line']} - {secret['match']}")
        print()
    
    if dangerous_files:
        print("DANGEROUS FILES DETECTED:")
        for file in dangerous_files:
            print(f"  BLOCKED: {file}")
        print()
    
    if secrets or dangerous_files:
        print("VALIDATION FAILED: Cannot proceed with git operation")
        print("Please remove secrets and dangerous files before committing.")
        return 1
    else:
        print("VALIDATION PASSED: No secrets or dangerous files detected")
        return 0

if __name__ == "__main__":
    sys.exit(main())
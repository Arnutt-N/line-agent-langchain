#!/usr/bin/env python3
"""Quick validation - check only staged/changed files."""

import subprocess
import sys

def get_staged_files():
    """Get list of staged files for commit."""
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True)
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except:
        return []

def main():
    staged_files = get_staged_files()
    
    if not staged_files:
        print("No staged files to validate")
        return 0
    
    # Check for dangerous files
    dangerous_patterns = ['phase_', 'SECURITY', '.env']
    dangerous_files = [f for f in staged_files if any(p in f for p in dangerous_patterns)]
    
    if dangerous_files:
        print("DANGEROUS FILES IN STAGING:")
        for f in dangerous_files:
            print(f"  BLOCKED: {f}")
        return 1
    
    print(f"VALIDATION PASSED: {len(staged_files)} files checked")
    return 0

if __name__ == "__main__":
    sys.exit(main())
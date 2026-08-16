#!/bin/bash
# Audit frontend dependencies for outdated and vulnerable packages.

set -e

cd "$(dirname "$0")/.."

echo "=== Outdated Packages ==="
pnpm outdated || true

echo ""
echo "=== Security Audit ==="
pnpm audit --json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'vulnerabilities' in data:
    for pkg, info in data['vulnerabilities'].items():
        print(f'- {pkg}: {info.get(\"severity\", \"unknown\")} - {info.get(\"title\", \"\")}')
else:
    print('No vulnerabilities found')
" || echo "Audit not available"

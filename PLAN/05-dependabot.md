# Phase 5 — Implementation Tasks

## Execution Order

```
5.1 Dependabot config (backend)
5.2 Dependabot config (frontend)
5.3 Automated PR handling
5.4 Security scanning (Trivy/Snyk)
5.5 Version bump automation
5.6 Dependency audit dashboard
```

---

## 5.1 — Dependabot Config (Backend)

**File:** `.github/dependabot.yml`

```yaml
version: 2
updates:
  # Python backend
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "UTC"
    open-pull-requests-limit: 10
    reviewers:
      - "hollowmedusa-team"
    labels:
      - "dependencies"
      - "backend"
    commit-message:
      prefix: "deps"
      include: "scope"
    # Group related updates
    groups:
      dev-dependencies:
        patterns:
          - "*dev*"
          - "*test*"
          - "*lint*"
        update-types:
          - "minor"
          - "patch"
      runtime-dependencies:
        patterns:
          - "*"
        update-types:
          - "minor"
          - "patch"
```

**Verification:**
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/dependabot.yml'))"
```

---

## 5.2 — Dependabot Config (Frontend)

**File:** `.github/dependabot.yml` (continued)

```yaml
  # Node.js frontend
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "UTC"
    open-pull-requests-limit: 10
    reviewers:
      - "hollowmedusa-team"
    labels:
      - "dependencies"
      - "frontend"
    commit-message:
      prefix: "deps"
      include: "scope"
    # Group React ecosystem
    groups:
      react-ecosystem:
        patterns:
          - "react*"
          - "react-dom"
          - "react-router*"
          - "reactflow"
        update-types:
          - "minor"
          - "patch"
      editor-components:
        patterns:
          - "@monaco-editor*"
          - "@tanstack*"
        update-types:
          - "minor"
          - "patch"
      dev-dependencies:
        patterns:
          - "*dev*"
          - "*test*"
          - "*lint*"
        update-types:
          - "minor"
          - "patch"
```

---

## 5.3 — Automated PR Handling

**Files:**
- `.github/workflows/dependabot-automerge.yml` — Auto-merge safe updates
- `.github/workflows/dependabot-test.yml` — Run tests on Dependabot PRs

**Auto-merge workflow:**
```yaml
# .github/workflows/dependabot-automerge.yml
name: Dependabot Auto-Merge

on:
  pull_request:
    labels: ['dependencies']

permissions:
  contents: write
  pull-requests: write

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'
    steps:
      - name: Check test results
        uses: actions/github-script@v7
        with:
          script: |
            const pr = await github.rest.pulls.get({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: context.issue.number
            });
            
            const checks = await github.rest.checks.listForRef({
              owner: context.repo.owner,
              repo: context.repo.repo,
              ref: pr.data.head.sha
            });
            
            const allPassed = checks.data.check_runs.every(
              run => run.conclusion === 'success'
            );
            
            if (allPassed) {
              await github.rest.pulls.update({
                owner: context.repo.owner,
                repo: context.repo.repo,
                pull_number: context.issue.number,
                auto_merge: {
                  enabled: true,
                  merge_method: 'squash'
                }
              });
            }
```

**Test workflow:**
```yaml
# .github/workflows/dependabot-test.yml
name: Dependabot PR Tests

on:
  pull_request:
    paths:
      - 'backend/**'
      - 'frontend/**'

jobs:
  backend-tests:
    if: contains(github.event.pull_request.labels.*.name, 'dependencies')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: cd backend && pip install -e ".[dev]"
      - run: cd backend && ruff check src/ tests/
      - run: cd backend && pytest tests/ -v

  frontend-tests:
    if: contains(github.event.pull_request.labels.*.name, 'dependencies')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      - run: cd frontend && pnpm install --frozen-lockfile
      - run: cd frontend && pnpm lint
      - run: cd frontend && pnpm typecheck
      - run: cd frontend && pnpm build
```

---

## 5.4 — Security Scanning

**Files:**
- `.github/workflows/security-scan.yml` — Trivy vulnerability scan
- `.github/workflows/secret-scan.yml` — Secret detection

**Trivy scan:**
```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  schedule:
    - cron: '0 6 * * 1'  # Monday at 6 AM
  pull_request:
    paths:
      - '**/requirements*.txt'
      - '**/pyproject.toml'
      - '**/package*.json'

jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
```

**Secret scan:**
```yaml
# .github/workflows/secret-scan.yml
name: Secret Scan

on:
  pull_request:

jobs:
  detect-secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Detect secrets
        uses: dennis714/detect-secrets-action@main
        with:
          baseline: '.secrets.baseline'
```

---

## 5.5 — Version Bump Automation

**Files:**
- `.github/workflows/version-bump.yml` — Automated version updates
- `backend/src/hollowmedusa/__version__.py` — Version file
- `frontend/package.json` — Version field

**Version bump workflow:**
```yaml
# .github/workflows/version-bump.yml
name: Version Bump

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'New version (e.g., 1.2.0)'
        required: true
      part:
        description: 'Version part to bump'
        required: false
        default: 'patch'
        type: choice
        options:
          - major
          - minor
          - patch

jobs:
  bump-version:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Get current version
        id: current
        run: |
          BACKEND_VERSION=$(grep 'version' backend/pyproject.toml | head -1 | cut -d'"' -f2)
          FRONTEND_VERSION=$(grep '"version"' frontend/package.json | cut -d'"' -f4)
          echo "backend_version=$BACKEND_VERSION" >> $GITHUB_OUTPUT
          echo "frontend_version=$FRONTEND_VERSION" >> $GITHUB_OUTPUT
      
      - name: Bump versions
        run: |
          NEW_VERSION="${{ inputs.version }}"
          sed -i "s/version = \".*\"/version = \"$NEW_VERSION\"/" backend/pyproject.toml
          sed -i "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" frontend/package.json
      
      - name: Create commit
        run: |
          git config user.name "Version Bot"
          git config user.email "bot@hollowmedusa.dev"
          git add backend/pyproject.toml frontend/package.json
          git commit -m "chore: bump version to ${{ inputs.version }}"
          git push
```

---

## 5.6 — Dependency Audit Dashboard

**Files:**
- `backend/scripts/audit.py` — Dependency audit script
- `frontend/scripts/audit.sh` — Frontend audit script
- `docs/dependency-policy.md` — Dependency update policy

**Audit script:**
```python
#!/usr/bin/env python3
"""Audit Python dependencies for outdated and vulnerable packages."""
import subprocess
import json
import sys

def run_audit():
    # Get outdated packages
    outdated = subprocess.run(
        ["pip", "list", "--outdated", "--format=json"],
        capture_output=True,
        text=True,
    )
    
    # Get security advisory
    security = subprocess.run(
        ["pip", "audit"],
        capture_output=True,
        text=True,
    )
    
    print("=== Outdated Packages ===")
    try:
        packages = json.loads(outdated.stdout)
        for pkg in packages:
            print(f"- {pkg['name']}: {pkg['version']} -> {pkg['latest_version']}")
    except json.JSONDecodeError:
        print(outdated.stdout)
    
    print("\n=== Security Advisories ===")
    print(security.stdout)
    
    return security.returncode == 0

if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)
```

**Audit policy:**
```markdown
# Dependency Update Policy

## Update Cadence
- **Minor/Patch**: Automated via Dependabot, merged weekly
- **Major**: Manual review required, tested in staging first

## Security Vulnerabilities
- **Critical/High**: Immediate update, CI blocked until fixed
- **Medium**: Update within 1 week
- **Low**: Update within 1 month

## Review Process
1. Dependabot creates PR
2. CI runs full test suite
3. Security scan passes
4. Auto-merge for minor/patch
5. Manual approval for major updates

## Exceptions
- Breaking changes require manual review
- Deprecated packages need migration plan
- License changes need legal approval
```

---

## Checklist

- [ ] `5.1` Dependabot config (backend pip)
- [ ] `5.2` Dependabot config (frontend npm)
- [ ] `5.3` Automated PR handling (auto-merge + tests)
- [ ] `5.4` Security scanning (Trivy + secret scan)
- [ ] `5.5` Version bump automation
- [ ] `5.6` Dependency audit dashboard

## Deliverable

Fully automated dependency management with security scanning.

```bash
# Trigger Dependabot manually
gh dependabot open-merge-request --repo your-org/hollowmedusa

# Run audit locally
cd backend && python scripts/audit.py
cd frontend && bash scripts/audit.sh
```

## CI Update

Add to `.github/workflows/ci.yml`:
```yaml
- name: Run security scan
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    severity: 'CRITICAL,HIGH'
```

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

## Version Bumping

- **Patch** (1.0.0 → 1.0.1): Automated on merge
- **Minor** (1.0.0 → 1.1.0): Manual workflow dispatch
- **Major** (1.0.0 → 2.0.0): Manual with changelog review

## Audit Schedule

- **Weekly**: Automated Trivy scan (Monday 6 AM UTC)
- **On PR**: Security scan for dependency changes
- **Monthly**: Manual audit report review

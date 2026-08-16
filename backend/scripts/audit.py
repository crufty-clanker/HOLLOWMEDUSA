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

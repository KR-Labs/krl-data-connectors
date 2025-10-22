#!/usr/bin/env python3
# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Check that source files include proper trademark notices.
"""

import argparse
import sys
from pathlib import Path
from typing import List


TRADEMARK_PATTERNS = [
    "KR-Labs™",
    "KR-Labs is a trademark",
    "Quipu Research Labs, LLC",
]

EXCLUDED_DIRS = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "htmlcov",
    ".coverage",
    "dist",
    "build",
    "*.egg-info",
    "backups",
}

EXCLUDED_FILES = {
    ".gitignore",
    ".pre-commit-config.yaml",
    ".gitleaks.toml",
    "LICENSE",
    "CHANGELOG.md",
    "pyproject.toml",
    "setup.cfg",
    "pytest.ini",
    "requirements.txt",
    "requirements_*.txt",
}

# Only check key documentation files and source files
FILE_EXTENSIONS = {".py", ".md"}
KEY_FILES = {"README.md", "CONTRIBUTING.md", "SECURITY.md"}


def should_check_file(file_path: Path) -> bool:
    """Determine if a file should be checked for trademark notices."""
    # Skip excluded directories
    for part in file_path.parts:
        if part in EXCLUDED_DIRS or part.startswith("."):
            return False

    # Skip excluded files
    if file_path.name in EXCLUDED_FILES:
        return False

    # Check key files
    if file_path.name in KEY_FILES:
        return True

    # Only check Python files for trademark
    if file_path.suffix == ".py":
        return True

    return False


def check_trademark(file_path: Path) -> bool:
    """Check if a file contains a trademark notice."""
    try:
        content = file_path.read_text(encoding="utf-8")
        # Check if any trademark pattern exists in the first 50 lines
        first_lines = "\n".join(content.split("\n")[:50])
        return any(pattern in first_lines for pattern in TRADEMARK_PATTERNS)
    except Exception as e:
        print(f"⚠️  Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return True  # Don't fail on read errors


def find_files_missing_trademark(root_path: Path) -> List[Path]:
    """Find all files that are missing trademark notices."""
    missing_trademark = []

    for file_path in root_path.rglob("*"):
        if file_path.is_file() and should_check_file(file_path):
            if not check_trademark(file_path):
                missing_trademark.append(file_path)

    return missing_trademark


def main():
    parser = argparse.ArgumentParser(
        description="Check trademark notices in source files"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("."),
        help="Root path to check (default: current directory)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose output",
    )
    args = parser.parse_args()

    root_path = args.path.resolve()
    if args.verbose:
        print(f"🔍 Checking trademark notices in: {root_path}")

    missing = find_files_missing_trademark(root_path)

    if missing:
        print(f"❌ Found {len(missing)} file(s) missing trademark notices:\n")
        for file_path in sorted(missing):
            rel_path = file_path.relative_to(root_path)
            print(f"  - {rel_path}")
        print(
            "\n💡 Tip: Add trademark notice to file headers:\n"
            "KR-Labs™ is a trademark of Quipu Research Labs, LLC,\n"
            "a subsidiary of Sudiata Giddasira, Inc."
        )
        sys.exit(1)
    else:
        print("✅ All checked files have trademark notices!")
        sys.exit(0)


if __name__ == "__main__":
    main()

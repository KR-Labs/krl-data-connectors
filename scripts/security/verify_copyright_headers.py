#!/usr/bin/env python3
# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Verify that all source files have proper copyright headers.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple


COPYRIGHT_PATTERNS = [
    "© 2025 KR-Labs. All rights reserved.",
    "© 2025 KR-Labs",
    "Copyright (c) 2025 KR-Labs",
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
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "pytest.ini",
    "requirements.txt",
    "requirements_*.txt",
}

FILE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs"}


def should_check_file(file_path: Path) -> bool:
    """Determine if a file should be checked for copyright headers."""
    # Skip excluded directories
    for part in file_path.parts:
        if part in EXCLUDED_DIRS or part.startswith("."):
            return False

    # Skip excluded files
    if file_path.name in EXCLUDED_FILES:
        return False

    # Skip wildcard patterns
    for pattern in EXCLUDED_FILES:
        if "*" in pattern and file_path.name.endswith(pattern.replace("*", "")):
            return False

    # Only check specific file types
    if file_path.suffix not in FILE_EXTENSIONS:
        return False

    return True


def check_copyright(file_path: Path) -> bool:
    """Check if a file contains a copyright header."""
    try:
        content = file_path.read_text(encoding="utf-8")
        # Check if any copyright pattern exists in the first 50 lines
        first_lines = "\n".join(content.split("\n")[:50])
        return any(pattern in first_lines for pattern in COPYRIGHT_PATTERNS)
    except Exception as e:
        print(f"⚠️  Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return True  # Don't fail on read errors


def find_files_missing_copyright(root_path: Path) -> List[Path]:
    """Find all files that are missing copyright headers."""
    missing_copyright = []

    for file_path in root_path.rglob("*"):
        if file_path.is_file() and should_check_file(file_path):
            if not check_copyright(file_path):
                missing_copyright.append(file_path)

    return missing_copyright


def main():
    parser = argparse.ArgumentParser(
        description="Verify copyright headers in source files"
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
        print(f"🔍 Checking copyright headers in: {root_path}")

    missing = find_files_missing_copyright(root_path)

    if missing:
        print(f"❌ Found {len(missing)} file(s) missing copyright headers:\n")
        for file_path in sorted(missing):
            rel_path = file_path.relative_to(root_path)
            print(f"  - {rel_path}")
        print(
            "\n💡 Tip: Run scripts/security/add_copyright_headers.py to add headers automatically"
        )
        sys.exit(1)
    else:
        print("✅ All source files have copyright headers!")
        sys.exit(0)


if __name__ == "__main__":
    main()

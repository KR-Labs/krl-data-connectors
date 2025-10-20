#!/usr/bin/env python3
"""
inject_watermark.py
Inject build watermark into Python package for tracking and tamper detection.

Usage:
    python inject_watermark.py --build-id RUN_ID --commit-sha SHA --repo REPO_NAME

Copyright (c) 2025 KR-Labs Foundation
Licensed under the MIT License
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


def generate_watermark(
    build_id: str,
    commit_sha: str,
    repo: str,
    version: Optional[str] = None,
) -> Dict:
    """Generate watermark dictionary with build metadata."""
    watermark = {
        "build_id": build_id,
        "build_timestamp": datetime.utcnow().isoformat() + "Z",
        "commit_sha": commit_sha,
        "repository": repo,
        "builder": "github-actions",
        "version": version or "unknown",
        "checksum": None,  # Computed after initial injection
    }
    return watermark


def compute_package_hash(src_dir: Path, exclude_file: Optional[str] = None) -> str:
    """
    Compute SHA256 hash of all Python files in package.
    
    Args:
        src_dir: Source directory to hash
        exclude_file: File to exclude from hash (e.g., __init__.py being modified)
    """
    hasher = hashlib.sha256()
    
    py_files = sorted(src_dir.rglob("*.py"))
    
    for pyfile in py_files:
        if exclude_file and pyfile.name == exclude_file:
            continue
        
        try:
            with open(pyfile, "rb") as f:
                hasher.update(f.read())
        except Exception as e:
            print(f"Warning: Could not hash {pyfile}: {e}", file=sys.stderr)
    
    return hasher.hexdigest()


def find_package_root(src_dir: Path) -> Optional[Path]:
    """
    Find the root __init__.py of the main package.
    Looks for the first __init__.py in src_dir structure.
    """
    # Common patterns: src/package_name/__init__.py
    for init_file in src_dir.rglob("__init__.py"):
        # Skip test directories
        if "test" in str(init_file).lower():
            continue
        # Return the first valid __init__.py found
        return init_file
    
    return None


def inject_watermark_code(init_file: Path, watermark: Dict) -> None:
    """
    Inject watermark code into __init__.py.
    Appends to end of file to avoid breaking imports.
    """
    watermark_code = f'''

# ============================================================================
# Build Watermark - DO NOT REMOVE
# This watermark is used for build tracking and tamper detection
# ============================================================================
__watermark__ = {json.dumps(watermark, indent=4)}
'''
    
    try:
        with open(init_file, "a", encoding="utf-8") as f:
            f.write(watermark_code)
        print(f"✓ Watermark injected into {init_file}")
    except Exception as e:
        print(f"✗ Error injecting watermark: {e}", file=sys.stderr)
        raise


def read_version(src_dir: Path) -> Optional[str]:
    """
    Try to read version from __version__.py or __init__.py.
    """
    # Check for __version__.py
    version_files = list(src_dir.rglob("__version__.py"))
    if version_files:
        try:
            with open(version_files[0], "r", encoding="utf-8") as f:
                content = f.read()
                for line in content.split("\n"):
                    if line.startswith("__version__"):
                        # Extract version string
                        parts = line.split("=")
                        if len(parts) == 2:
                            version = parts[1].strip().strip('"').strip("'")
                            return version
        except Exception:
            pass
    
    return None


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Inject build watermark into Python package"
    )
    parser.add_argument(
        "--build-id",
        required=True,
        help="GitHub Actions run ID or unique build identifier"
    )
    parser.add_argument(
        "--commit-sha",
        required=True,
        help="Git commit SHA"
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Repository name (e.g., KR-Labs/krl-open-core)"
    )
    parser.add_argument(
        "--src-dir",
        type=Path,
        default=Path("src"),
        help="Source directory containing package (default: src)"
    )
    parser.add_argument(
        "--version",
        help="Package version (auto-detected if not specified)"
    )
    parser.add_argument(
        "--compute-checksum",
        action="store_true",
        help="Compute package checksum (slower but more secure)"
    )
    
    args = parser.parse_args()
    
    src_dir = args.src_dir.resolve()
    
    # Validate source directory
    if not src_dir.exists():
        print(f"Error: Source directory not found: {src_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Find package __init__.py
    init_file = find_package_root(src_dir)
    if not init_file:
        print(f"Error: Could not find package __init__.py in {src_dir}", file=sys.stderr)
        print("Searched pattern: src/*/__init__.py", file=sys.stderr)
        sys.exit(1)
    
    print(f"Package root: {init_file}")
    
    # Auto-detect version if not provided
    version = args.version
    if not version:
        version = read_version(src_dir)
        if version:
            print(f"Detected version: {version}")
        else:
            print("Warning: Could not detect version, using 'unknown'")
    
    # Generate watermark
    watermark = generate_watermark(
        build_id=args.build_id,
        commit_sha=args.commit_sha,
        repo=args.repo,
        version=version,
    )
    
    # Compute checksum if requested
    if args.compute_checksum:
        print("Computing package checksum...")
        package_hash = compute_package_hash(src_dir, exclude_file="__init__.py")
        watermark["checksum"] = f"sha256:{package_hash}"
        print(f"Package checksum: {package_hash[:16]}...")
    else:
        watermark["checksum"] = "not_computed"
    
    # Inject watermark
    print("Injecting watermark...")
    inject_watermark_code(init_file, watermark)
    
    # Summary
    print()
    print("=" * 60)
    print("WATERMARK INJECTION COMPLETE")
    print("=" * 60)
    print(f"Build ID:      {watermark['build_id']}")
    print(f"Commit SHA:    {watermark['commit_sha'][:8]}...")
    print(f"Repository:    {watermark['repository']}")
    print(f"Version:       {watermark['version']}")
    print(f"Timestamp:     {watermark['build_timestamp']}")
    if args.compute_checksum:
        print(f"Checksum:      {package_hash[:16]}...")
    print()
    print("✓ Watermark successfully injected")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

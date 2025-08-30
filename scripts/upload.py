#!/usr/bin/env python3

"""MYCC Package Upload Script.

Uploads built packages to conda repository using rattler-build upload.
Supports the simplified MYCC architecture with basic package variant.
"""

import os
import sys
import argparse
import subprocess
from typing import List
from pathlib import Path
from dataclasses import dataclass

try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm is not available
    def tqdm(iterable, **kwargs):
        del kwargs  # Unused parameter
        return iterable


@dataclass
class Config:
    server_url: str = "https://prefix.dev"
    channel: str = "meta-forge"
    api_key: str = ""
    output_path: Path = Path("./output")

    def __post_init__(self):
        # Override with environment variables
        self.server_url = os.getenv("PREFIX_SERVER_URL", self.server_url)
        self.channel = os.getenv("PREFIX_CHANNEL", self.channel)
        self.api_key = os.getenv("PREFIX_API_KEY", self.api_key)


class PackageUploader:
    def __init__(self, config: Config):
        self.config = config

    def check_rattler_build(self) -> bool:
        """Check if rattler-build command is available."""
        try:
            subprocess.run(["rattler-build", "--help"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def find_packages(self, prefix: str = "*") -> List[Path]:
        """Find all conda packages that match the prefix."""
        packages = []
        skip_dirs = {"bld", "src_cache", "test"}

        # Find packages in platform subdirectories (e.g., linux-64/, osx-arm64/, noarch/)
        for subdir in self.config.output_path.iterdir():
            if subdir.is_dir() and subdir.name not in skip_dirs:
                for file in subdir.iterdir():
                    if file.name.endswith(".conda"):
                        # Check if filename matches prefix pattern
                        if prefix == "*":
                            packages.append(file)
                        elif prefix == "mycc-":
                            # For basic packages, include only mycc- (simplified architecture)
                            if file.name.startswith("mycc-") and not file.name.startswith("mycc-full-"):
                                packages.append(file)
                        elif file.name.startswith(prefix):
                            packages.append(file)

        # Then find packages directly in the path (if any)
        for file in self.config.output_path.iterdir():
            if file.name.endswith(".conda"):
                # Check if filename matches prefix pattern
                if prefix == "*":
                    packages.append(file)
                elif prefix == "mycc-":
                    # For basic packages, include only mycc- (simplified architecture)
                    if file.name.startswith("mycc-") and not file.name.startswith("mycc-full-"):
                        packages.append(file)
                elif file.name.startswith(prefix):
                    packages.append(file)

        return sorted(set(packages))  # Remove duplicates and sort

    def upload_packages(self, packages: List[Path], delete_after: bool = False) -> None:
        """Upload packages to prefix.dev channel."""
        print(f"Found {len(packages)} package(s) to upload:")
        for pkg in packages:
            print(f"  {pkg.parent.name}/{pkg.name}")

        print(f"\nUploading to {self.config.server_url} channel '{self.config.channel}'...")

        for fp in tqdm(packages, desc="Uploading packages"):
            cmds = [
                "rattler-build",
                "upload",
                "prefix",
                "-c",
                self.config.channel,
                "--color=always",
            ]

            # Add API key if available
            if self.config.api_key:
                cmds.append(f"--api-key={self.config.api_key}")

            # Add server URL if not default
            if self.config.server_url != "https://prefix.dev":
                cmds.extend(["--url", self.config.server_url])

            # Add package file
            cmds.append(str(fp))

            print(f"\nUploading {fp.parent.name}/{fp.name}...")
            result = subprocess.run(cmds)

            if result.returncode == 0:
                print(f"✅ Successfully uploaded {fp.name}")
                if delete_after:
                    fp.unlink()
                    print(f"🗑️  Deleted local file {fp.name}")
            else:
                print(f"❌ Failed to upload {fp.name}")
                sys.exit(1)

        print(f"\n🎉 All packages uploaded successfully!")
        print(f"📦 Packages available at: {self.config.server_url}/{self.config.channel}")


def main():
    parser = argparse.ArgumentParser(
        description="Upload MYCC packages to conda repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables:
  PREFIX_SERVER_URL   Server URL (default: https://prefix.dev)
  PREFIX_CHANNEL      Channel name (default: meta-forge)
  PREFIX_API_KEY      API key for authentication

Examples:
  %(prog)s                    # Upload all packages
  %(prog)s --type basic       # Upload basic packages only (mycc-)
  %(prog)s --delete           # Delete local files after upload
  %(prog)s --dry-run          # Show what would be uploaded
  PREFIX_CHANNEL=my-channel %(prog)s  # Use custom channel
        """,
    )

    parser.add_argument(
        "--delete", "-d", action="store_true", help="Delete local package files after successful upload"
    )

    parser.add_argument(
        "--type",
        choices=["basic", "all"],
        default="all",
        help="Package type to upload: 'basic' for mycc packages only, 'all' for all packages (default: all)",
    )

    parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded without actually uploading")

    args = parser.parse_args()

    # Initialize config and uploader
    config = Config()
    uploader = PackageUploader(config)

    # Check prerequisites
    if not uploader.check_rattler_build():
        print("❌ rattler-build command not found. Please install rattler-build first:")
        print("  pip install rattler-build")
        print("  or use: pixi add rattler-build")
        sys.exit(1)

    # Determine package prefix based on type
    prefix_map = {"basic": "mycc-", "all": "*"}
    prefix = prefix_map[args.type]

    # Find packages
    packages = uploader.find_packages(prefix)

    if not packages:
        sys.exit(1)

    if args.dry_run:
        print(f"\n🔍 Dry run - would upload {len(packages)} package(s):")
        for pkg in packages:
            print(f"  {pkg.parent.name}/{pkg.name}")
        print(f"\nTarget: {config.server_url}/{config.channel}")
        return

    # Confirm upload
    print(f"\n⚠️  About to upload {len(packages)} package(s) to {config.server_url}/{config.channel}")
    response = input("Continue? (y/N): ").strip().lower()

    if not response.startswith("y"):
        print("🚫 Upload cancelled")
        return

    # Upload packages
    uploader.upload_packages(packages, delete_after=args.delete)


if __name__ == "__main__":
    main()

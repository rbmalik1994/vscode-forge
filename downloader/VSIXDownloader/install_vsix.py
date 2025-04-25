#!/usr/bin/env python3
"""
install_vsix.py: Install VS Code extensions from .vsix files.
"""

import os
import argparse
import subprocess
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(
        description='Install VS Code extensions from .vsix files.')
    parser.add_argument(
        '--vsix-dir', '-d',
        default=str(Path(__file__).parent / 'vsix_files'),
        help='Directory containing .vsix files to install.')
    parser.add_argument(
        '--extension', '-e',
        help='Specific extension ID to install (e.g., "publisher.name").')
    parser.add_argument(
        '--install-all', '-a',
        action='store_true',
        help='Install all .vsix files in the directory.')
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available .vsix files without installing.')
    args = parser.parse_args()

    vsix_dir = Path(args.vsix_dir)
    if not vsix_dir.exists():
        print(f"Error: Directory '{vsix_dir}' does not exist.")
        return 1

    # Get all .vsix files in the directory
    vsix_files = list(vsix_dir.glob('*.vsix'))
    
    if not vsix_files:
        print(f"No .vsix files found in '{vsix_dir}'.")
        return 1

    # List mode - just show available .vsix files
    if args.list:
        print(f"Available .vsix files in '{vsix_dir}':")
        for vsix_file in sorted(vsix_files):
            extension_id = vsix_file.stem  # Remove .vsix extension
            print(f"  {extension_id}")
        return 0

    # Filter by extension ID if specified
    if args.extension:
        matching_files = [f for f in vsix_files if args.extension in f.stem]
        if not matching_files:
            print(f"No .vsix files found matching '{args.extension}'.")
            return 1
        vsix_files = matching_files

    # Unless install_all is set, confirm with the user
    if not args.install_all and not args.extension:
        print(f"Found {len(vsix_files)} .vsix files. Use --install-all to install all, or --extension to specify one.")
        print("Use --list to see available extensions.")
        return 0

    # Install the extensions
    success_count = 0
    error_count = 0
    
    for vsix_file in vsix_files:
        print(f"Installing: {vsix_file.stem}")
        try:
            # Use VS Code CLI to install the extension
            result = subprocess.run(
                ['code', '--install-extension', str(vsix_file), '--force'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully installed {vsix_file.stem}")
                success_count += 1
            else:
                print(f"❌ Failed to install {vsix_file.stem}: {result.stderr.strip()}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Error installing {vsix_file.stem}: {str(e)}")
            error_count += 1

    # Print summary
    print(f"\nInstallation summary:")
    print(f"  Total: {len(vsix_files)}")
    print(f"  Success: {success_count}")
    print(f"  Failed: {error_count}")

    return 0 if error_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
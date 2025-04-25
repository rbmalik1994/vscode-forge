#!/usr/bin/env python3
"""
download_vsix.py: Backup installed VS Code extensions into .vsix files.
"""

import os
import zipfile
import argparse
from pathlib import Path
import subprocess
import requests
import json


def main():
    parser = argparse.ArgumentParser(
        description='Backup installed VS Code extensions into .vsix files.')
    parser.add_argument(
        '--extensions-dir', '-e',
        default=str(Path(__file__).parent /  'extensions'),
        help='Path to the VS Code extensions directory.')
    parser.add_argument(
        '--output-dir', '-o',
        default=str(Path(__file__).parent)+'/vsix_files',
        help='Directory to save .vsix files.')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get list of installed extensions via code CLI
    try:
        result = subprocess.run(['code', '--list-extensions'], capture_output=True, text=True, check=True)
        extensions = result.stdout.strip().splitlines()
        print(extensions)
    except Exception as e:
        print(f'Error listing extensions: {e}')
        return 1

    count = 0
    for ext in extensions:
        if '.' not in ext:
            print(f'Skipping invalid extension identifier: {ext}')
            continue
        print(f'Processing {ext}')
        
        publisher, name = ext.split('.', 1)
        vsix_name = f"{ext}.vsix"
        dest_file = output_dir / vsix_name
        print(f'Downloading {ext} -> {dest_file}')
        
        # New approach using the official marketplace API
        # Construct the request payload to get extension details
        post_url = "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json;api-version=7.1-preview.1',
            'User-Agent': 'Mozilla/5.0 VSCode Extension Downloader'
        }
        
        payload = {
            "filters": [
                {
                    "criteria": [
                        {"filterType": 7, "value": ext}
                    ]
                }
            ],
            "flags": 2151
        }
        
        try:
            # Get extension metadata first
            response = requests.post(post_url, headers=headers, data=json.dumps(payload))
            if response.status_code != 200:
                print(f'Failed to get metadata for {ext}: HTTP {response.status_code}')
                continue
                
            data = response.json()
            if not data.get('results') or not data['results'][0].get('extensions'):
                print(f'No results found for {ext}')
                continue
                
            extension_data = data['results'][0]['extensions'][0]
            
            # Find the VSIX package from the extension assets
            vsix_asset = None
            for asset in extension_data.get('versions', [{}])[0].get('files', []):
                if asset.get('assetType') == 'Microsoft.VisualStudio.Services.VSIXPackage':
                    vsix_asset = asset
                    break
            
            if not vsix_asset:
                print(f'Could not find VSIX asset for {ext}')
                continue
                
            # Download the VSIX file
            download_url = vsix_asset.get('source')
            if not download_url:
                print(f'No download URL for {ext}')
                continue
                
            download_resp = requests.get(download_url, allow_redirects=True)
            if download_resp.status_code == 200:
                with open(dest_file, 'wb') as f:
                    f.write(download_resp.content)
                count += 1
                print(f'Successfully downloaded {ext}')
            else:
                print(f'Failed to download {ext}: HTTP {download_resp.status_code}')
                
        except Exception as e:
            print(f'Error downloading {ext}: {str(e)}')

    print(f'Done. Downloaded {count} extensions into {output_dir}')
    return 0


if __name__ == '__main__':
    exit(main())

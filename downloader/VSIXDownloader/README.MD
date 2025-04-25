# VSIX Downloader

This tool backs up all installed VS Code extensions into `.vsix` files by zipping each extension's directory.

## Usage

```bash
# Navigate to the VSIXDownloader directory
cd downloader/VSIXDownloader

# Run the script (defaults to ~/.vscode/extensions and ./extensions output)
python3 download_vsix.py

# Or specify custom directories:
python3 download_vsix.py -e /path/to/.vscode/extensions -o /path/to/output_dir
```

Generated `.vsix` files will be placed in the specified output directory.


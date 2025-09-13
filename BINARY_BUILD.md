# Building a Standalone Binary for hcp-doctor

You can build a single-file executable (no Python or venv required) using PyInstaller.

## Prerequisites
- Python 3.8+ (for building)
- [PyInstaller](https://pyinstaller.org/) (install with `pip install pyinstaller`)

## Build Steps (macOS/Linux)

```sh
chmod +x build_binary.sh
./build_binary.sh
```

The binary will be created at `dist/hcp-doctor`.

## Build Steps (Windows)

Use the following command in Command Prompt or PowerShell:

```
pyinstaller --onefile -n hcp-doctor -p hashicorp_doctor hashicorp_doctor/cli.py
```

## Notes
- The binary is platform-specific. Build on each OS for that OS.
- All Python dependencies are bundled inside the binary.
- No need for users to install Python or create a virtual environment.

## Advanced: Customizing the Build
- Edit `pyinstaller.spec` for advanced options (hidden imports, data files, etc).

## Troubleshooting
- If you add new dependencies, re-run the build script.
- For issues, see the [PyInstaller docs](https://pyinstaller.org/en/stable/).

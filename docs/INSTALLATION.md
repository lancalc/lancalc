# Installation Guide

## Prerequisites

Python 3.9+ is required.

## Installation Methods

### Default Installation (with GUI)

```bash
pip3 install lancalc
```

### CLI-only / Headless Installation

For environments without GUI support (servers, CI/CD, headless systems):

```bash
# Install package without dependencies, then only required CLI deps
pip3 install --no-deps lancalc
pip3 install -r requirements.txt
```

### Installation without GUI Dependencies

```bash
# Install with nogui extras (excludes PyQt5)
pip3 install 'lancalc[nogui]'
```

### Installation from GitHub

```bash
# With GUI (default)
pip3 install 'git+https://github.com/lancalc/lancalc.git'

# CLI-only / headless
pip3 install --no-deps 'git+https://github.com/lancalc/lancalc.git'
pip3 install -r requirements.txt

# Without GUI dependencies
pip3 install 'git+https://github.com/lancalc/lancalc.git#egg=lancalc[nogui]'
```

## Troubleshooting

### Missing pip

If pip is missing:

```bash
curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py
```

### Command Not Found

If the `lancalc` command is not found after installation, add the local packages path to PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

To permanently add to PATH, add this line to your `~/.bashrc` or `~/.zshrc`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### GUI Issues on Linux

On Linux, PyQt5 may require system Qt libraries (xcb plugin). If GUI fails to start:

1. Ensure a desktop environment is available
2. Try installing system packages:
   ```bash
   # Debian/Ubuntu
   sudo apt install python3-pyqt5
   
   # Fedora
   sudo dnf install python3-qt5
   
   # Arch
   sudo pacman -S python-pyqt5
   ```
3. Or use the CLI-only installation steps above

### CI/Headless Environments

In CI/headless environments, prefer the CLI-only steps above to skip GUI dependencies.

## Uninstallation

```bash
pip3 uninstall -y lancalc
```

## Development Installation

See [Development Guide](DEVELOPMENT.md) for detailed development setup instructions.

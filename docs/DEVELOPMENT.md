# Development Guide

## Prerequisites

Python 3.9+ is required. GUI development requires PyQt5 (installed by default).

## Installation for Development

Clone the repository and install in development mode:

```bash
git clone https://github.com/lancalc/lancalc.git
cd lancalc
```

## Development Setup

### Production (CLI only)
```bash
pip3 install -r requirements.txt
```

### Editable install with GUI (default)
```bash
pip3 install -e .
```

### Editable install without GUI
```bash
pip3 install --no-deps -e .
pip3 install -r requirements.txt
```

### Full dev setup (with GUI)
```bash
pip3 install -e '.[dev]'
```

### Dev without GUI
```bash
pip3 install --no-deps -e .
pip3 install -r requirements.txt
pip3 install pytest pytest-qt pre-commit flake8
```

### Reinstall 
```bash
pip3 install -e . --force-reinstall
```

## Running from Source

```bash
# GUI (requires PyQt5)
python3 lancalc/main.py

# CLI
python3 -m lancalc 192.168.1.1/24
```

## Development Tools

```bash
pip3 install pre-commit flake8 pytest pytest-qt
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

## Running Tests

```bash
pytest -v
```

## Test Build

```bash
pip3 install -e .
~/.local/bin/lancalc
```

### Test Build Linux
```bash
pip3 install git+file://$(pwd) 
export PATH="$HOME/.local/bin:$PATH" 
lancalc
```

### Test Build Windows
```powershell
pip3 install "git+file://$(Get-Location)"
lancalc
```

## Project Structure

```
lancalc/
├── lancalc/           # Main package
│   ├── __init__.py    # Package initialization
│   ├── __main__.py    # Entry point for python -m lancalc
│   ├── main.py        # Main application logic
│   ├── cli.py         # Command-line interface
│   ├── gui.py         # Graphical user interface
│   ├── core.py        # Core network calculation logic
│   └── adapters.py    # Network interface detection
├── docs/              # Documentation
├── test_lancalc.py    # Test suite
├── pyproject.toml     # Project configuration
├── requirements.txt   # Runtime dependencies
└── requirements-dev.txt # Development dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Testing

The project uses pytest for testing. Key test categories:

- **Core functionality**: Network calculations, CIDR parsing, validation
- **CLI functionality**: JSON and text output, special ranges
- **GUI functionality**: Window operations, clipboard, error handling
- **Special network ranges**: Loopback, link-local, multicast, etc.
- **Edge cases**: Various network configurations and error conditions
- **Integration tests**: Network interface detection, external IP retrieval

### Running Specific Tests

```bash
# Run only CLI tests
pytest test_lancalc.py -k "cli" -v

# Run only GUI tests
pytest test_lancalc.py -k "gui" -v

# Run only core tests
pytest test_lancalc.py -k "core" -v
```

### GUI Testing

GUI tests require a display environment. In CI, they run with `xvfb-run` (virtual framebuffer).

## Code Style

The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **Pre-commit** for automated checks

Run code quality checks:

```bash
pre-commit run --all-files
```

## Building and Distribution

### Build Package
```bash
python -m build
```

### Install from Local Build
```bash
pip install dist/lancalc-*.whl
```

## Troubleshooting

### GUI Issues in Development

If GUI tests fail in development:

1. Ensure PyQt5 is installed: `pip install PyQt5`
2. Check display environment: `echo $DISPLAY`
3. For headless environments, use `xvfb-run` for testing

### Import Issues

If you encounter import errors:

1. Ensure you're in the correct virtual environment
2. Reinstall in editable mode: `pip install -e . --force-reinstall`
3. Check Python path: `python -c "import sys; print(sys.path)"`

## Release Process

1. Update version in `lancalc/__init__.py`
2. Update `CHANGELOG.md`
3. Create and push a tag
4. GitHub Actions will automatically build and publish to PyPI

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

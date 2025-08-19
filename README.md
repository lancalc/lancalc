# LanCalc

[![CI](https://github.com/lancalc/lancalc/actions/workflows/ci.yml/badge.svg)](https://github.com/lancalc/lancalc/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/lancalc.svg)](https://pypi.org/project/lancalc/)
[![Python](https://img.shields.io/pypi/pyversions/lancalc.svg)](https://pypi.org/project/lancalc/)

LanCalc is a desktop application built with PyQt5, designed to calculate network configurations for Windows, macOS, and Linux systems.

![image](https://github.com/user-attachments/assets/a7d1779f-d138-4819-84c6-4df876efc292)

[Download](https://github.com/lancalc/lancalc/releases)

It provides a user-friendly interface to compute essential network parameters such as network address, broadcast address, the minimum and maximum host addresses, and the number of hosts within a given subnet. 

Support IPv4 address formats, subnet masks and prefixes. This tool is particularly useful for network administrators and IT professionals who require quick calculations of network parameters.

## Quick Start

### Installation

Python 3.9+ is required.

```bash
# Default (with GUI)
pip3 install lancalc

# CLI-only / headless
pip3 install 'lancalc[nogui]'

# From GitHub
pip3 install 'git+https://github.com/lancalc/lancalc.git'
```

For detailed installation instructions and troubleshooting, see [Installation Guide](docs/INSTALLATION.md).

### Basic Usage

**GUI Mode:**
```bash
lancalc
```

**CLI Mode:**
```bash
# Basic subnet calculation
lancalc 192.168.1.1/24

# JSON output for scripting
lancalc 192.168.1.1/24 --json

# Show current network interface
lancalc --internal

# Show external IP
lancalc --external
```

### Examples

**Basic calculation:**
```bash
$ lancalc 192.168.1.1/24
Network: 192.168.1.0
Prefix: /24
Netmask: 255.255.255.0
Broadcast: 192.168.1.255
Hostmin: 192.168.1.1
Hostmax: 192.168.1.254
Hosts: 254
```

**JSON output:**
```bash
$ lancalc 192.168.1.1/24 --json
{
  "network": "192.168.1.0",
  "prefix": "/24",
  "netmask": "255.255.255.0",
  "broadcast": "192.168.1.255",
  "hostmin": "192.168.1.1",
  "hostmax": "192.168.1.254",
  "hosts": "254"
}
```

**Special networks:**
```bash
lancalc 192.168.1.100/31  # Point-to-point (RFC 3021)
lancalc 192.168.1.1/32    # Single host
lancalc 127.0.0.1/8       # Loopback range
```

## Features

- **Dual Interface**: GUI and CLI modes
- **JSON Output**: Machine-readable format for scripting
- **Special Ranges**: Automatic detection of RFC-defined special IPv4 ranges
- **Cross-platform**: Windows, macOS, and Linux support
- **Network Detection**: Auto-detection of current network interface
- **External IP**: Public IP address detection

## Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed installation instructions and troubleshooting
- **[Usage Guide](docs/USAGE.md)** - Complete usage examples and special features
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing and development setup
- **[FAQ](docs/FAQ.md)** - Frequently asked questions
- **[RFC Documentation](docs/RFC.md)** - Special IPv4 ranges and RFC compliance
- **[Changelog](docs/CHANGELOG.md)** - Version history and release notes

## Special IPv4 Ranges

LanCalc automatically detects and handles special IPv4 address ranges according to RFC specifications:

- **127.0.0.0/8** - Loopback addresses (RFC 3330)
- **169.254.0.0/16** - Link-local addresses (RFC 3927)
- **224.0.0.0/4** - Multicast addresses (RFC 5771)
- **0.0.0.0/8** - Unspecified addresses (RFC 1122)
- **255.255.255.255/32** - Limited broadcast (RFC 919)

For detailed information about special ranges and RFC compliance, see [RFC Documentation](docs/RFC.md).

## Development

For development setup and contributing guidelines, see [Development Guide](docs/DEVELOPMENT.md).

## License

Distributed under the MIT License. See LICENSE for more information.

## Contact

[GitHub](https://github.com/lancalc/lancalc) [Telegram](https://t.me/wachawo)

# Frequently Asked Questions (FAQ)

## General Questions

### What is LanCalc?

LanCalc is a desktop application for calculating network configurations. It provides both a graphical user interface (GUI) and command-line interface (CLI) for computing essential network parameters such as network address, broadcast address, host ranges, and subnet information.

### What platforms does LanCalc support?

LanCalc supports Windows, macOS, and Linux systems. It requires Python 3.9 or higher.

### Is LanCalc free to use?

Yes, LanCalc is open-source software distributed under the MIT License.

## Installation Questions

### Why can't I find the `lancalc` command after installation?

This usually happens because the local packages directory isn't in your PATH. Add it with:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

For permanent addition, add this line to your `~/.bashrc` or `~/.zshrc`.

### Can I install LanCalc without GUI dependencies?

Yes, you can install the CLI-only version:

```bash
pip3 install 'lancalc[nogui]'
```

This excludes PyQt5 and is useful for servers or headless environments.

### I'm getting GUI errors on Linux. What should I do?

Try installing system Qt libraries:

```bash
# Debian/Ubuntu
sudo apt install python3-pyqt5

# Fedora
sudo dnf install python3-qt5

# Arch
sudo pacman -S python-pyqt5
```

If GUI still doesn't work, use the CLI-only installation.

## Usage Questions

### How do I calculate a basic subnet?

```bash
lancalc 192.168.1.1/24
```

### How do I get JSON output for scripting?

```bash
lancalc 192.168.1.1/24 --json
```

### How do I find my current network interface information?

```bash
lancalc --internal
# or
lancalc -i
```

### How do I find my external/public IP address?

```bash
lancalc --external
# or
lancalc -e
```

### Can I use both internal and external IP detection at once?

Yes:

```bash
lancalc -i -e
```

## Special Network Questions

### What does the asterisk (*) mean in the output?

The asterisk indicates special network types or ranges:

- **/31 networks**: Show `2*` - both addresses are usable (RFC 3021)
- **/32 networks**: Show `1*` - single host network
- **Special ranges**: Host fields show `*` for non-routable addresses

### What are special IPv4 ranges?

Special ranges are non-routable address spaces defined by RFCs:

- **127.0.0.0/8**: Loopback addresses
- **169.254.0.0/16**: Link-local addresses
- **224.0.0.0/4**: Multicast addresses
- **0.0.0.0/8**: Unspecified addresses
- **255.255.255.255/32**: Limited broadcast address

### Why do /31 networks show "2*" hosts?

According to RFC 3021, /31 networks can use both addresses for point-to-point links. The asterisk indicates this special behavior.

### Are /31 networks supported by all devices?

No, some older devices or specific vendors may not support /31 networks. Check your device documentation.

## Technical Questions

### What's the difference between text and JSON output?

- **Text output**: Human-readable format, good for manual review
- **JSON output**: Machine-readable format, good for scripting and automation

### Does LanCalc support IPv6?

Currently, LanCalc supports IPv4 only. IPv6 support is planned for future versions.

### How accurate are the calculations?

LanCalc follows RFC specifications exactly. All calculations are based on standard networking protocols and RFC documents.

### Can I use LanCalc in scripts?

Yes, the JSON output is designed for scripting:

```bash
#!/bin/bash
result=$(lancalc 192.168.1.1/24 --json)
network=$(echo "$result" | jq -r '.network')
echo "Network: $network"
```

## Troubleshooting

### The GUI won't start. What should I do?

1. Check if you're in a headless environment (SSH, CI/CD)
2. Try CLI mode: `lancalc 192.168.1.1/24`
3. Install system Qt libraries (see installation FAQ)
4. Use CLI-only installation

### I'm getting import errors. What's wrong?

1. Ensure you're using Python 3.9+
2. Check your virtual environment
3. Reinstall: `pip install -e . --force-reinstall`

### JSON output is missing fields. Is this normal?

No, JSON output should always include all fields. If fields are missing, it might be a bug. Please report it.

### Can I contribute to LanCalc?

Yes! See the [Development Guide](DEVELOPMENT.md) for contribution guidelines.

## Performance Questions

### How fast is LanCalc?

LanCalc is designed for speed. Most calculations complete in milliseconds, even for large subnets.

### Does LanCalc work offline?

Yes, all network calculations work offline. Only external IP detection requires internet connectivity.

### How much memory does LanCalc use?

LanCalc is lightweight, typically using less than 50MB of memory.

## Support

### Where can I get help?

- [GitHub Issues](https://github.com/lancalc/lancalc/issues)
- [Documentation](https://github.com/lancalc/lancalc#readme)
- [Telegram](https://t.me/wachawo)

### How do I report a bug?

Please use the [GitHub Issues](https://github.com/lancalc/lancalc/issues) page and include:

1. Your operating system and Python version
2. Steps to reproduce the issue
3. Expected vs actual behavior
4. Any error messages

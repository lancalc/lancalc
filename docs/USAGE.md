# Usage Guide

## Running the Application

### GUI Mode

After installation (default with GUI), launch the application with the command:

```bash
lancalc
```

LanCalc auto-detects the environment. If GUI dependencies are unavailable or you are in a headless session, the launcher falls back to CLI help. In such cases, use the CLI examples below.

### CLI Mode

LanCalc also supports command-line interface for automation and scripting:

```bash
# Basic usage
lancalc 192.168.1.1/24

# JSON output for parsing
lancalc 192.168.1.1/24 --json

# Examples
lancalc 10.0.0.1/8
lancalc 172.16.0.1/16
lancalc 192.168.1.100/31  # Point-to-point network
lancalc 192.168.1.1/32    # Single host
```

You can also run via module:

```bash
python3 -m lancalc 192.168.1.1/24 --json
```

## Command Line Interface

### Basic Usage

```bash
# Basic subnet calculation
lancalc 192.168.1.1/24

# JSON output
lancalc 192.168.1.1/24 --json

# Show internal/private IP address
lancalc --internal
lancalc -i

# Show external/public IP address
lancalc --external
lancalc -e

# Use multiple info flags simultaneously
lancalc -i -e
lancalc -i -e --json

# Show version
lancalc --version
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

**Interface information:**
```bash
$ lancalc -i
Address: 10.16.69.146
Prefix: /24

$ lancalc -i --json
{"address": "10.16.69.146", "prefix": "/24"}
```

**External IP detection:**
```bash
$ lancalc -e
External IP: 216.66.18.3

$ lancalc -e --json
{"external_ip": "216.66.18.3"}
```

**Multiple info flags:**
```bash
$ lancalc -i -e
Address: 10.16.69.146
Prefix: /24

External IP: 216.66.18.3

$ lancalc -i -e --json
{"address": "10.16.69.146", "prefix": "/24"}

{"external_ip": "216.66.18.3"}
```

## Output Format

### Text Mode (default)

```
Network: 192.168.1.0
Prefix: /24
Netmask: 255.255.255.0
Broadcast: 192.168.1.255
Hostmin: 192.168.1.1
Hostmax: 192.168.1.254
Hosts: 254
```

### JSON Mode (`--json`)

```json
{
  "network": "192.168.1.0",
  "prefix": "/24",
  "netmask": "255.255.255.0",
  "broadcast": "192.168.1.255",
  "hostmin": "192.168.1.1",
  "hostmax": "192.168.1.254",
  "hosts": "254",
  "comment": ""
}
```

### JSON Fields

The JSON output includes the following fields:

- **`comment`**: Description and RFC reference for special ranges (empty for normal unicast addresses)
- **`hosts`**: Number of available host addresses in the specified subnet

These fields are always present, making the JSON output format consistent regardless of address type.

## Special IPv4 Ranges

LanCalc automatically detects and handles special IPv4 address ranges according to RFC specifications. For these ranges, host-related fields show "*" and a message field indicates the range type with RFC reference.

### Supported Special Ranges

| Range | Type | RFC | Description |
|-------|------|-----|-------------|
| **127.0.0.0/8** | Loopback | [RFC 3330](RFC.md#rfc-3330---loopback-addresses) | Loopback addresses - not routable on the Internet |
| **169.254.0.0/16** | Link-local | [RFC 3927](RFC.md#rfc-3927---link-local-addresses) | Link-local addresses - not routable |
| **224.0.0.0/4** | Multicast | [RFC 5771](RFC.md#rfc-5771---multicast-addresses) | Multicast addresses - not for host addressing |
| **0.0.0.0/8** | Unspecified | [RFC 1122](RFC.md#rfc-1122---unspecified-addresses) | Unspecified addresses - not for host addressing |
| **255.255.255.255/32** | Broadcast | [RFC 919](RFC.md#rfc-919---broadcast-address) | Limited broadcast address - not for host addressing |

### Special Range Behavior

When you enter an address from a special range:

**CLI Text Mode:**
```bash
lancalc 127.0.0.1/8
```
```
Network: 127.0.0.0
Prefix: /8
Netmask: 255.0.0.0
Broadcast: *
Hostmin: 127.0.0.1
Hostmax: 127.255.255.254
Hosts: 16777214
Comment: RFC 3330 Loopback (https://github.com/lancalc/lancalc/blob/main/docs/RFC.md#rfc-3330---loopback-addresses)
```

**CLI JSON Mode:**
```bash
lancalc 224.0.0.1/4 --json
```
```json
{
  "network": "224.0.0.0",
  "prefix": "/4",
  "netmask": "240.0.0.0",
  "broadcast": "*",
  "hostmin": "*",
  "hostmax": "*",
  "hosts": "*",
  "comment": "RFC 5771 Multicast (https://github.com/lancalc/lancalc/blob/main/docs/RFC.md#rfc-5771---multicast-addresses)"
}
```

**GUI Mode:**
- Host fields (Hostmin, Hostmax, Broadcast, Hosts) show "*"
- Status bar displays the special range message instead of version
- No special styling or warnings needed

## Special Network Types

- **/31 networks**: Show `2*` in Hosts field - both addresses are usable (RFC 3021)
- **/32 networks**: Show `1*` in Hosts field - single host network
- The asterisk (*) indicates special network types where all addresses are usable

For detailed information about /31 networks, see [RFC 3021 Documentation](RFC.md#rfc-3021---using-31-bit-prefixes-on-ipv4-point-to-point-links).

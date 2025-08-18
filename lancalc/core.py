#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core functionality for LanCalc - IPv4 subnet calculations.
"""
import ipaddress
import logging
import socket
import subprocess
import sys
import platform
import re
import traceback
import typing

logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stderr)
    ],
    level=logging.WARNING,
    format='%(asctime)s.%(msecs)03d [%(levelname)s]: (%(name)s.%(funcName)s) - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

REPO_URL = "https://github.com/lancalc/lancalc"


def get_ip() -> str:
    """Return the primary local IPv4 address without external libs."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception as e:
        logger.error(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
        # Fallback: hostname resolution (may return 127.0.0.1 in some setups)
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception as e:
            logger.error(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
            return "127.0.0.1"
    finally:
        s.close()


def validate_ip(ip: str) -> None:
    """Validate IPv4 address format or raise ValueError."""
    try:
        ipaddress.IPv4Address(ip)
    except ipaddress.AddressValueError as exc:
        raise ValueError(f"Invalid IP address: {ip}") from exc


def validate_prefix(prefix: str) -> int:
    """Validate CIDR prefix (0-32). Return int or raise ValueError."""
    try:
        prefix_int = int(prefix)
    except ValueError as exc:
        raise ValueError(f"Invalid prefix: {prefix}") from exc
    if 0 <= prefix_int <= 32:
        return prefix_int
    raise ValueError(f"Invalid prefix: {prefix}")


def _get_cidr_windows(ip: str) -> int:
    """Get CIDR for IP on Windows using ipconfig."""
    try:
        result = subprocess.run(
            ["ipconfig"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.split("\n")
            for i, line in enumerate(lines):
                if ip in line:
                    # Look for subnet mask in next few lines
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if "Subnet Mask" in lines[j]:
                            mask_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", lines[j])
                            if mask_match:
                                try:
                                    return cidr_from_netmask(mask_match.group(1))
                                except ValueError:
                                    pass
    except Exception as e:
        logger.error(f"Windows CIDR detection failed: {type(e).__name__} {str(e)}")
    return 24


def _get_cidr_macos(ip: str) -> int:
    """Get CIDR for IP on macOS using ifconfig."""
    try:
        result = subprocess.run(
            ["ifconfig"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.split("\n")
            for i, line in enumerate(lines):
                if ip in line:
                    # Look for netmask in next few lines
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if "netmask" in lines[j]:
                            mask_match = re.search(
                                r"netmask (\d+\.\d+\.\d+\.\d+)", lines[j]
                            )
                            if mask_match:
                                try:
                                    return cidr_from_netmask(mask_match.group(1))
                                except ValueError:
                                    pass
    except Exception as e:
        logger.error(f"macOS CIDR detection failed: {type(e).__name__} {str(e)}")
    return 24


def _get_cidr_linux(ip: str) -> int:
    """Get CIDR for IP on Linux using ip route."""
    try:
        # First try to get the route for the specific IP
        result = subprocess.run(
            ["ip", "route", "get", ip], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            # Parse output like: "192.168.1.100 via 192.168.1.1 dev eth0 src 192.168.1.100 uid 1000"
            for line in result.stdout.split("\n"):
                if "src" in line and ip in line:
                    # Extract the route prefix from the routing table
                    route_result = subprocess.run(
                        ["ip", "route", "show"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if route_result.returncode == 0:
                        for route_line in route_result.stdout.split("\n"):
                            if (route_line.strip() and ip.split(".")[:3] == route_line.split()[0].split(".")[:3]):
                                # Found matching route, extract CIDR
                                cidr_match = re.search(r"/(\d+)", route_line)
                                if cidr_match:
                                    return int(cidr_match.group(1))

        # Fallback: try to find the default route and use its CIDR
        route_result = subprocess.run(
            ["ip", "route", "show"], capture_output=True, text=True, timeout=10
        )
        if route_result.returncode == 0:
            for route_line in route_result.stdout.split("\n"):
                if route_line.strip() and "default" in route_line:
                    # Look for the next hop IP to determine the network
                    parts = route_line.split()
                    for i, part in enumerate(parts):
                        if part == "via" and i + 1 < len(parts):
                            gateway_ip = parts[i + 1]
                            # Try to find a route for the gateway's network
                            for other_line in route_result.stdout.split("\n"):
                                if (other_line.strip() and gateway_ip.split(".")[:3] == other_line.split()[0].split(".")[:3]):
                                    cidr_match = re.search(r"/(\d+)", other_line)
                                    if cidr_match:
                                        return int(cidr_match.group(1))
                            break
    except Exception as e:
        logger.error(f"Linux CIDR detection failed: {type(e).__name__} {str(e)}")
    return 24


def get_cidr(ip: str) -> int:
    """Best-effort CIDR detection using system tools; defaults to /24."""
    system = platform.system()
    try:
        if system == "Windows":
            return _get_cidr_windows(ip)
        elif system == "Darwin":
            return _get_cidr_macos(ip)
        else:
            return _get_cidr_linux(ip)
    except Exception as e:
        logger.error(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
        return 24


def parse_cidr(cidr: str) -> typing.Tuple[str, int]:
    """Parse CIDR notation (e.g., '192.168.1.1/24') into (ip, prefix)."""
    if "/" not in cidr:
        raise ValueError("Missing '/' separator")

    parts = cidr.split("/", 1)
    if len(parts) != 2:
        raise ValueError("Invalid CIDR format")

    ip, prefix_str = parts

    # validate_ip raises on error
    validate_ip(ip)

    prefix_int = validate_prefix(prefix_str)

    return ip.strip(), prefix_int


def cidr_from_netmask(mask: str) -> int:
    """Convert netmask to CIDR prefix."""
    try:
        parts = [int(x) for x in mask.split(".")]
        if len(parts) != 4:
            raise ValueError(f"Invalid netmask format: {mask}")

        # Validate netmask (must be consecutive 1s followed by 0s)
        binary = "".join(f"{p:08b}" for p in parts)
        if "01" in binary:  # Check for 1s after 0s
            raise ValueError(f"Invalid netmask: {mask}")

        return sum(bin(p).count("1") for p in parts)
    except Exception as e:
        logger.error(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
        raise ValueError(f"Invalid netmask: {mask}") from e


def is_special_range(ip: str, prefix: int) -> bool:
    """Check if IP/prefix combination is in a special IPv4 range."""
    try:
        network = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
        # network_addr = str(network.network_address)

        # RFC 3330 - Special Use IPv4 Addresses
        special_ranges = [
            ("0.0.0.0", 8),  # This network
            ("127.0.0.0", 8),  # Loopback
            ("169.254.0.0", 16),  # Link-local
            ("224.0.0.0", 4),  # Multicast
            ("240.0.0.0", 4),  # Reserved
            ("255.255.255.255", 32),  # Broadcast
        ]

        for special_ip, special_prefix in special_ranges:
            special_network = ipaddress.IPv4Network(
                f"{special_ip}/{special_prefix}", strict=False
            )
            if network.subnet_of(special_network):
                return True

        return False
    except Exception:
        return False


def classify_ipv4_range(ip: str, prefix: int) -> str:
    """Classify IPv4 range and return description."""
    try:
        network = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
        network_addr = str(network.network_address)

        # RFC 3330 - Special Use IPv4 Addresses
        if network_addr == "0.0.0.0" and prefix == 8:
            return f"RFC 1122 Unspecified ({REPO_URL}/blob/main/docs/RFC.md#rfc-1122---unspecified-addresses)"
        elif network_addr.startswith("127."):
            return f"RFC 3330 Loopback ({REPO_URL}/blob/main/docs/RFC.md#rfc-3330---loopback-addresses)"
        elif network_addr.startswith("169.254."):
            return f"RFC 3927 Link-local ({REPO_URL}/blob/main/docs/RFC.md#rfc-3927---link-local-addresses)"
        elif network_addr.startswith("224.") or (
            network_addr.startswith("239.") and prefix == 32
        ):
            return f"RFC 5771 Multicast ({REPO_URL}/blob/main/docs/RFC.md#rfc-5771---multicast-addresses)"
        elif network_addr.startswith("240."):
            return f"RFC 3330 Reserved ({REPO_URL}/blob/main/docs/RFC.md#rfc-3330---reserved-addresses)"
        elif network_addr == "255.255.255.255":
            return f"RFC 919 Broadcast ({REPO_URL}/blob/main/docs/RFC.md#rfc-919---broadcast-address)"
        else:
            return ""
    except Exception:
        return ""


def compute(ip: str, prefix: int) -> typing.Dict[str, str]:
    """Compute subnet information for given IP and prefix."""
    try:
        # Validate inputs
        validate_ip(ip)  # Raises ValueError if invalid
        validate_prefix(str(prefix))  # Raises ValueError if invalid

        # Create network object
        network = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
        network_addr = str(network.network_address)

        # Check if it's a special range
        is_special = is_special_range(ip, prefix)
        comment = classify_ipv4_range(ip, prefix) if is_special else ""

        # Calculate results
        if is_special:
            # Special handling for different special ranges
            if network_addr.startswith("127."):
                # Loopback: show actual host range
                result = {
                    "network": str(network.network_address),
                    "prefix": f"/{prefix}",
                    "netmask": str(network.netmask),
                    "broadcast": "*",
                    "hostmin": str(network.network_address + 1),
                    "hostmax": str(network.broadcast_address - 1),
                    "hosts": str(network.num_addresses - 2),
                    "comment": comment,
                    "type": "info",
                }
            else:
                # Other special ranges: show * for host fields
                result = {
                    "network": str(network.network_address),
                    "prefix": f"/{prefix}",
                    "netmask": str(network.netmask),
                    "broadcast": "*",
                    "hostmin": "*",
                    "hostmax": "*",
                    "hosts": "*",
                    "comment": comment,
                    "type": "info",
                }
        else:
            # Normal networks including /31 and /32 specifics
            if prefix == 31:
                hostmin = str(network.network_address)
                hostmax = str(network.broadcast_address)
                hosts = "2*"
            elif prefix == 32:
                hostmin = str(network.network_address)
                hostmax = str(network.network_address)
                hosts = "1*"
            else:
                hostmin = str(network.network_address + 1)
                hostmax = str(network.broadcast_address - 1)
                hosts = str(network.num_addresses - 2)

            result = {
                "network": str(network.network_address),
                "prefix": f"/{prefix}",
                "netmask": str(network.netmask),
                "broadcast": str(network.broadcast_address),
                "hostmin": hostmin,
                "hostmax": hostmax,
                "hosts": hosts,
                "comment": comment,
                "type": "normal",
            }

        return result

    except Exception as e:
        logger.error(
            f"Error in compute: {type(e).__name__} {str(e)}\n{traceback.format_exc()}"
        )
        raise


def compute_from_cidr(cidr: str) -> typing.Dict[str, str]:
    """Compute subnet information from CIDR notation."""
    ip, prefix = parse_cidr(cidr)
    return compute(ip, prefix)


def main():
    pass


if __name__ == '__main__':
    main()

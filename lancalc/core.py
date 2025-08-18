#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core functionality for LanCalc - IPv4 subnet calculations.
"""
import ipaddress
import logging
import socket
import sys
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

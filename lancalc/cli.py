#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-line interface for LanCalc.
"""

import json
import sys
import typing

# Import modules
try:
    from . import core, gui
    import lancalc
    VERSION = lancalc.__version__
except ImportError:
    import core
    import gui
    VERSION = "0.0.0"


def print_result_stdout(res: typing.Dict[str, str]) -> None:
    """Print result to stdout in human-readable format."""
    for k in ("network", "prefix", "netmask", "broadcast", "hostmin", "hostmax", "hosts"):
        print(f"{k.capitalize()}: {res[k]}")

    # Print comment if present for special ranges
    if res.get("comment"):
        print(f"Comment: {res['comment']}")


def print_result_json(res: typing.Dict[str, str]) -> None:
    """Print result as valid JSON to stdout."""
    # Filter out type and empty comment fields for cleaner JSON output
    filtered_res = res.copy()
    if filtered_res.get("comment") == "":
        filtered_res.pop("comment", None)
    filtered_res.pop("type", None)
    print(json.dumps(filtered_res))


def print_interface_info(json_output: bool = False) -> None:
    """Print information about detected network interfaces."""
    try:
        ip = core.get_ip()
        cidr = gui.get_cidr(ip)

        if json_output:
            interface_info = {
                "address": ip,
                "prefix": f"/{cidr}",
            }
            print(json.dumps(interface_info))
        else:
            print(f"Address: {ip}")
            print(f"Prefix: /{cidr}")

    except Exception as e:
        error_msg = f"Failed to detect network interface: {e}"
        if json_output:
            print(json.dumps({"error": error_msg}))
        else:
            print(error_msg, file=sys.stderr)


def run_cli(address: str, json_output: bool = False) -> int:
    """
    Run CLI mode with given address.

    Args:
        address: IPv4 address in CIDR notation
        json_output: Whether to output JSON format

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        result = core.compute_from_cidr(address)

        if json_output:
            print_result_json(result)
        else:
            print_result_stdout(result)

        return 0

    except ValueError as e:
        # Log validation errors to stderr only
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def main(argv: typing.Optional[list] = None) -> int:
    """
    Main CLI entry point.

    Args:
        argv: Command line arguments (uses sys.argv if None)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    import argparse

    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        prog="lancalc",
        description="LanCalc: IPv4 subnet calculator",
        epilog="Examples:\n  --help 192.168.1.1/24\n  --help 10.0.0.1/8 --json\n  --help --help",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "address",
        nargs="?",
        help="IPv4 address in CIDR notation (e.g., 192.168.1.1/24)"
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Output result in JSON format"
    )
    parser.add_argument("--version", "-v", action="version", version=f"LanCalc {VERSION}")
    parser.add_argument(
        "--interface",
        "-i",
        action="store_true",
        help="Show detected network interface information"
    )

    args = parser.parse_args(argv)

    # If interface info is requested
    if args.interface:
        print_interface_info(args.json)
        return 0

    # If address is provided, process it
    if args.address:
        return run_cli(args.address, args.json)

    # For CLI mode without address, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

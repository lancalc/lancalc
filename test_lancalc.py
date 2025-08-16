#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import os
import pytest
import sys
import subprocess
from lancalc.main import compute, compute_from_cidr, validate_ip, validate_prefix, parse_cidr
from lancalc.main import LanCalc, calc_network, print_result_json

# Check if we're in CI environment


def is_ci_environment():
    """Check if running in CI environment."""
    return os.environ.get('CI') == 'true' or os.environ.get('GITHUB_ACTIONS') == 'true'


# Configure logging for tests
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stderr)],
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d [%(levelname)s]: (%(name)s.%(funcName)s) - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Test data: (ip, prefix, expected values in output fields)
test_cases = [
    ("192.168.1.10", "24", {
        'network': '192.168.1.0',
        'prefix': '/24',
        'netmask': '255.255.255.0',
        'broadcast': '192.168.1.255',
        'hostmin': '192.168.1.1',
        'hostmax': '192.168.1.254',
        'hosts': '254',
        'ip_color': 'black'
    }),
    ("10.0.0.1", "8", {
        'network': '10.0.0.0',
        'prefix': '/8',
        'netmask': '255.0.0.0',
        'broadcast': '10.255.255.255',
        'hostmin': '10.0.0.1',
        'hostmax': '10.255.255.254',
        'hosts': '16777214',
        'ip_color': 'black'
    }),
    ("172.16.5.4", "16", {
        'network': '172.16.0.0',
        'prefix': '/16',
        'netmask': '255.255.0.0',
        'broadcast': '172.16.255.255',
        'hostmin': '172.16.0.1',
        'hostmax': '172.16.255.254',
        'hosts': '65534',
        'ip_color': 'black'
    }),
    ("192.168.2.1", "32", {
        'network': '192.168.2.1',
        'prefix': '/32',
        'netmask': '255.255.255.255',
        'broadcast': '192.168.2.1',
        'hostmin': '192.168.2.1',
        'hostmax': '192.168.2.1',
        'hosts': '1*',
        'ip_color': 'black'
    }),
    ("192.168.3.1/24", "", {
        'network': '192.168.3.0',
        'prefix': '/24',
        'netmask': '255.255.255.0',
        'broadcast': '192.168.3.255',
        'hostmin': '192.168.3.1',
        'hostmax': '192.168.3.254',
        'hosts': '254',
        'ip_color': 'black'
    }),
    ("10.0.0.1/8", "", {
        'network': '10.0.0.0',
        'prefix': '/8',
        'netmask': '255.0.0.0',
        'broadcast': '10.255.255.255',
        'hostmin': '10.0.0.1',
        'hostmax': '10.255.255.254',
        'hosts': '16777214',
        'ip_color': 'black'
    }),
    ("172.16.0.1/16", "", {
        'network': '172.16.0.0',
        'prefix': '/16',
        'netmask': '255.255.0.0',
        'broadcast': '172.16.255.255',
        'hostmin': '172.16.0.1',
        'hostmax': '172.16.255.254',
        'hosts': '65534',
        'ip_color': 'black'
    }),
    ("256.256.256.256", "24", {
        'network': '',
        'prefix': '',
        'netmask': '',
        'broadcast': '',
        'hostmin': '',
        'hostmax': '',
        'hosts': '',
        'ip_color': 'red'
    })
]


@pytest.fixture
def app(qtbot):
    test_app = LanCalc()
    qtbot.addWidget(test_app)
    return test_app


@pytest.mark.parametrize("ip,prefix,expected", test_cases)
@pytest.mark.skipif(is_ci_environment(), reason="GUI tests skipped in CI")
def test_lancalc_calculate(app, ip, prefix, expected):
    """Test network calculation through GUI"""
    # Set IP
    app.ip_input.setText(ip)
    # If prefix is embedded in input (CIDR), simulate GUI behavior
    if prefix == "" and "/" in ip:
        app.apply_cidr_from_text(ip)
    # Set prefix in combobox if not CIDR
    else:
        for i in range(app.network_selector.count()):
            if app.network_selector.itemText(i).startswith(prefix + "/"):
                app.network_selector.setCurrentIndex(i)
                break
    # Call calculate
    app.calculate_network()
    # Check outputs
    assert app.network_output.text() == expected['network']
    assert app.prefix_output.text() == expected['prefix']
    assert app.netmask_output.text() == expected['netmask']
    assert app.broadcast_output.text() == expected['broadcast']
    assert app.hostmin_output.text() == expected['hostmin']
    assert app.hostmax_output.text() == expected['hostmax']
    assert app.hosts_output.text() == expected['hosts']
    # Check color
    if expected['ip_color'] == 'red':
        assert 'red' in app.ip_input.styleSheet()
    else:
        assert 'color: black' in app.ip_input.styleSheet() or app.ip_input.styleSheet() == ''


@pytest.mark.skipif(is_ci_environment(), reason="GUI tests skipped in CI")
def test_invalid_cidr_handling(app):
    """Test handling of invalid CIDR values"""
    # Test with invalid CIDR (40) - this should fail validation
    app.ip_input.setText("192.168.1.1")
    # Try to set an invalid CIDR - since combobox only has 0-32, we'll test with a valid one
    # but the validation should catch it if we could set it
    app.calculate_network()
    # For now, just check that the app doesn't crash with invalid CIDR


@pytest.mark.skipif(is_ci_environment(), reason="GUI tests skipped in CI")
def test_window_launch(app):
    """Test basic window functionality"""
    assert app.isVisible() is False  # Window is not shown by default
    app.show()
    assert app.isVisible() is True
    assert app.windowTitle() == 'LanCalc'

# Tests for validation functions


@pytest.mark.skipif(is_ci_environment(), reason="GUI tests skipped in CI")
def test_validate_ip_address():
    """Test IP address validation"""
    app = LanCalc()

    # Valid IPs
    assert app.validate_ip_address("192.168.1.1")
    assert app.validate_ip_address("10.0.0.1")
    assert app.validate_ip_address("172.16.0.1")
    assert app.validate_ip_address("0.0.0.0")
    assert app.validate_ip_address("255.255.255.255")

    # Invalid IPs
    assert not app.validate_ip_address("256.256.256.256")
    assert not app.validate_ip_address("192.168.1.256")
    assert not app.validate_ip_address("192.168.1")
    assert not app.validate_ip_address("192.168.1.1.1")
    assert not app.validate_ip_address("")
    assert not app.validate_ip_address("invalid")


@pytest.mark.skipif(is_ci_environment(), reason="GUI tests skipped in CI")
def test_validate_cidr():
    """Test CIDR validation"""
    app = LanCalc()

    # Valid CIDRs
    for i in range(33):
        assert app.validate_cidr(str(i))

    # Invalid CIDRs
    assert not app.validate_cidr("-1")
    assert not app.validate_cidr("33")
    assert not app.validate_cidr("100")
    assert not app.validate_cidr("")
    assert not app.validate_cidr("invalid")


@pytest.mark.skipif(is_ci_environment(), reason="GUI tests skipped in CI")
def test_error_handling_in_gui(app):
    """Test error handling in GUI"""
    # Test with invalid IP
    app.ip_input.setText("invalid-ip")
    app.calculate_network()
    assert 'red' in app.ip_input.styleSheet()

    # Test with empty IP
    app.ip_input.setText("")
    app.calculate_network()
    assert 'red' in app.ip_input.styleSheet()


@pytest.mark.skipif(is_ci_environment(), reason="GUI tests skipped in CI")
def test_edge_cases():
    """Test edge cases for network calculations"""
    app = LanCalc()

    # Test /0 network
    app.ip_input.setText("0.0.0.0")
    for i in range(app.network_selector.count()):
        if app.network_selector.itemText(i).startswith("0/"):
            app.network_selector.setCurrentIndex(i)
            break
    app.calculate_network()
    assert app.network_output.text() == '0.0.0.0'
    assert app.prefix_output.text() == '/0'
    assert app.netmask_output.text() == '0.0.0.0'

    # Test /32 network (single host)
    app.ip_input.setText("192.168.1.1")
    for i in range(app.network_selector.count()):
        if app.network_selector.itemText(i).startswith("32/"):
            app.network_selector.setCurrentIndex(i)
            break
    app.calculate_network()
    assert app.network_output.text() == '192.168.1.1'
    assert app.prefix_output.text() == '/32'
    assert app.netmask_output.text() == '255.255.255.255'
    assert app.hosts_output.text() == '1*'


@pytest.mark.skipif(is_ci_environment(), reason="GUI tests skipped in CI")
def test_clipboard_functionality(qtbot):
    """Test clipboard auto-fill functionality"""
    from PyQt5.QtWidgets import QApplication

    app = LanCalc()
    qtbot.addWidget(app)

    # Clear the IP input first to simulate fallback scenario
    app.ip_input.clear()

    # Mock clipboard with valid IP
    clipboard = QApplication.clipboard()
    clipboard.setText("192.168.1.100/24")

    # Call check_clipboard
    app.check_clipboard()

    # Verify IP was filled
    assert app.ip_input.text() == "192.168.1.100"

    # Verify CIDR was set (24)
    assert app.network_selector.currentText().startswith("24/")

    # Test with invalid clipboard content
    clipboard.setText("invalid-ip")
    app.ip_input.clear()
    app.check_clipboard()
    assert app.ip_input.text() == ""  # Should not fill invalid IP


def test_json_output():
    """Test JSON output functionality"""
    # Test JSON output
    result = calc_network("192.168.1.1/24")

    # Verify result contains all required fields
    required_fields = ["Network", "Prefix", "Netmask", "Broadcast", "Hostmin", "Hostmax", "Hosts"]
    for field in required_fields:
        assert field in result

    # Verify JSON is valid
    json_str = json.dumps(result)
    parsed_json = json.loads(json_str)
    assert parsed_json == result

    # Test print_result_json function
    print_result_json(result)  # This should not raise any exceptions


def test_cli_json_output():
    """Test CLI JSON output via subprocess"""
    # Test JSON output via CLI
    result = subprocess.run(
        [sys.executable, "-m", "lancalc.main", "192.168.1.1/24", "--json"],
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )

    assert result.returncode == 0
    assert result.stdout.strip()

    # Parse JSON output
    json_data = json.loads(result.stdout.strip())
    assert "Network" in json_data
    assert "Prefix" in json_data
    assert "Netmask" in json_data
    assert "Broadcast" in json_data
    assert "Hostmin" in json_data
    assert "Hostmax" in json_data
    assert "Hosts" in json_data

    # Verify values
    assert json_data["Network"] == "192.168.1.0"
    assert json_data["Prefix"] == "/24"
    assert json_data["Netmask"] == "255.255.255.0"


def test_cli_text_output():
    """Test CLI text output via subprocess"""
    # Test text output via CLI
    result = subprocess.run(
        [sys.executable, "-m", "lancalc.main", "192.168.1.1/24"],
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )

    assert result.returncode == 0
    assert result.stdout.strip()

    # Verify text output format
    output_lines = result.stdout.strip().split('\n')
    assert len(output_lines) == 7  # 7 fields

    # Check that each line has the format "Field: Value"
    for line in output_lines:
        assert ': ' in line
        field, value = line.split(': ', 1)
        assert field in ["Network", "Prefix", "Netmask", "Broadcast", "Hostmin", "Hostmax", "Hosts"]


# Core calculation tests (moved from test_calc.py)


class TestCoreCalculations:
    """Test core network calculation functions."""

    def test_compute_basic(self):
        """Test basic network computation."""
        result = compute("192.168.1.1", 24)
        assert result["Network"] == "192.168.1.0"
        assert result["Prefix"] == "/24"
        assert result["Netmask"] == "255.255.255.0"
        assert result["Broadcast"] == "192.168.1.255"
        assert result["Hostmin"] == "192.168.1.1"
        assert result["Hostmax"] == "192.168.1.254"
        assert result["Hosts"] == "254"

    def test_compute_slash_8(self):
        """Test /8 network."""
        result = compute("10.0.0.1", 8)
        assert result["Network"] == "10.0.0.0"
        assert result["Prefix"] == "/8"
        assert result["Netmask"] == "255.0.0.0"
        assert result["Broadcast"] == "10.255.255.255"
        assert result["Hostmin"] == "10.0.0.1"
        assert result["Hostmax"] == "10.255.255.254"
        assert result["Hosts"] == "16777214"

    def test_compute_slash_16(self):
        """Test /16 network."""
        result = compute("172.16.5.4", 16)
        assert result["Network"] == "172.16.0.0"
        assert result["Prefix"] == "/16"
        assert result["Netmask"] == "255.255.0.0"
        assert result["Broadcast"] == "172.16.255.255"
        assert result["Hostmin"] == "172.16.0.1"
        assert result["Hostmax"] == "172.16.255.254"
        assert result["Hosts"] == "65534"

    def test_compute_slash_31(self):
        """Test /31 network (point-to-point)."""
        result = compute("192.168.1.0", 31)
        assert result["Network"] == "192.168.1.0"
        assert result["Prefix"] == "/31"
        assert result["Netmask"] == "255.255.255.254"
        assert result["Broadcast"] == "192.168.1.1"
        assert result["Hostmin"] == "192.168.1.0"
        assert result["Hostmax"] == "192.168.1.1"
        assert result["Hosts"] == "2*"

    def test_compute_slash_32(self):
        """Test /32 network (single host)."""
        result = compute("192.168.2.1", 32)
        assert result["Network"] == "192.168.2.1"
        assert result["Prefix"] == "/32"
        assert result["Netmask"] == "255.255.255.255"
        assert result["Broadcast"] == "192.168.2.1"
        assert result["Hostmin"] == "192.168.2.1"
        assert result["Hostmax"] == "192.168.2.1"
        assert result["Hosts"] == "1*"

    def test_compute_slash_0(self):
        """Test /0 network (default route)."""
        result = compute("0.0.0.0", 0)
        assert result["Network"] == "0.0.0.0"
        assert result["Prefix"] == "/0"
        assert result["Netmask"] == "0.0.0.0"
        assert result["Broadcast"] == "255.255.255.255"
        assert result["Hostmin"] == "0.0.0.1"
        assert result["Hostmax"] == "255.255.255.254"
        assert result["Hosts"] == "4294967294"


class TestCIDRParsing:
    """Test CIDR parsing functions."""

    def test_parse_cidr_valid(self):
        """Test valid CIDR parsing."""
        ip, prefix = parse_cidr("192.168.1.1/24")
        assert ip == "192.168.1.1"
        assert prefix == 24

    def test_parse_cidr_invalid_format(self):
        """Test invalid CIDR format."""
        with pytest.raises(ValueError, match="Missing '/' separator"):
            parse_cidr("192.168.1.1")

        with pytest.raises(ValueError, match="Prefix part is empty"):
            parse_cidr("192.168.1.1/")

        with pytest.raises(ValueError, match="IP address part is empty"):
            parse_cidr("/24")

    def test_compute_from_cidr(self):
        """Test computation from CIDR string."""
        result = compute_from_cidr("192.168.1.1/24")
        assert result["Network"] == "192.168.1.0"
        assert result["Prefix"] == "/24"


class TestValidation:
    """Test validation functions."""

    def test_validate_ip_valid(self):
        """Test valid IP addresses."""
        validate_ip("192.168.1.1")
        validate_ip("10.0.0.1")
        validate_ip("172.16.0.1")
        validate_ip("0.0.0.0")
        validate_ip("255.255.255.255")

    def test_validate_ip_invalid(self):
        """Test invalid IP addresses."""
        with pytest.raises(ValueError):
            validate_ip("256.256.256.256")

        with pytest.raises(ValueError):
            validate_ip("192.168.1.256")

        with pytest.raises(ValueError):
            validate_ip("192.168.1")

        with pytest.raises(ValueError):
            validate_ip("192.168.1.1.1")

        with pytest.raises(ValueError):
            validate_ip("")

        with pytest.raises(ValueError):
            validate_ip("invalid")

    def test_validate_prefix_valid(self):
        """Test valid prefixes."""
        for i in range(33):
            assert validate_prefix(str(i)) == i

    def test_validate_prefix_invalid(self):
        """Test invalid prefixes."""
        with pytest.raises(ValueError):
            validate_prefix("-1")

        with pytest.raises(ValueError):
            validate_prefix("33")

        with pytest.raises(ValueError):
            validate_prefix("100")

        with pytest.raises(ValueError):
            validate_prefix("")

        with pytest.raises(ValueError):
            validate_prefix("invalid")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_edge_case_networks(self):
        """Test various edge case networks."""
        # Test networks with all zeros
        result = compute("0.0.0.0", 8)
        assert result["Network"] == "0.0.0.0"

        # Test networks with all ones
        result = compute("255.255.255.255", 32)
        assert result["Network"] == "255.255.255.255"

        # Test /30 network (4 addresses, 2 usable)
        result = compute("192.168.1.0", 30)
        assert result["Hosts"] == "2"
        assert result["Hostmin"] == "192.168.1.1"
        assert result["Hostmax"] == "192.168.1.2"

    def test_consistency_gui_cli(self):
        """Test that GUI and CLI would produce identical results."""
        test_cases = [
            ("192.168.1.1", 24),
            ("10.0.0.1", 8),
            ("172.16.5.4", 16),
            ("192.168.2.1", 32),
            ("192.168.3.0", 31),
            ("0.0.0.0", 0),
        ]

        for ip, prefix in test_cases:
            result = compute(ip, prefix)
            # Verify all required fields are present
            required_fields = ["Network", "Prefix", "Netmask", "Broadcast", "Hostmin", "Hostmax", "Hosts"]
            for field in required_fields:
                assert field in result
                assert result[field] != ""


class TestGoldenCases:
    """Golden tests for specific network scenarios."""

    def test_golden_standard_networks(self):
        """Test standard network configurations with known results"""
        golden_cases = [
            # (ip, prefix, expected_network, expected_broadcast, expected_hosts)
            ("192.168.1.1", 24, "192.168.1.0", "192.168.1.255", "254"),
            ("10.0.0.1", 8, "10.0.0.0", "10.255.255.255", "16777214"),
            ("172.16.0.1", 16, "172.16.0.0", "172.16.255.255", "65534"),
            ("192.168.1.1", 23, "192.168.0.0", "192.168.1.255", "510"),
            ("192.168.1.1", 25, "192.168.1.0", "192.168.1.127", "126"),
            ("192.168.1.1", 30, "192.168.1.0", "192.168.1.3", "2"),
            ("192.168.1.1", 31, "192.168.1.0", "192.168.1.1", "2*"),
            ("192.168.1.1", 32, "192.168.1.1", "192.168.1.1", "1*"),
        ]

        for ip, prefix, expected_network, expected_broadcast, expected_hosts in golden_cases:
            result = compute(ip, prefix)
            assert result["Network"] == expected_network, f"Failed for {ip}/{prefix}"
            assert result["Broadcast"] == expected_broadcast, f"Failed for {ip}/{prefix}"
            assert result["Hosts"] == expected_hosts, f"Failed for {ip}/{prefix}"

    def test_rfc_3021_compliance(self):
        """Test /31 networks according to RFC 3021 (point-to-point links)"""
        # RFC 3021: Using 31-Bit Prefixes on IPv4 Point-to-Point Links
        # For /31 networks, both addresses are usable for hosts

        result = compute("192.168.1.0", 31)
        assert result["Network"] == "192.168.1.0"
        assert result["Broadcast"] == "192.168.1.1"
        assert result["Hostmin"] == "192.168.1.0"  # First address usable
        assert result["Hostmax"] == "192.168.1.1"  # Second address usable
        assert result["Hosts"] == "2*"  # Both addresses usable

        result = compute("192.168.1.2", 31)
        assert result["Network"] == "192.168.1.2"
        assert result["Broadcast"] == "192.168.1.3"
        assert result["Hostmin"] == "192.168.1.2"
        assert result["Hostmax"] == "192.168.1.3"
        assert result["Hosts"] == "2*"

    def test_single_host_networks(self):
        """Test /32 networks (single host)"""
        result = compute("192.168.1.100", 32)
        assert result["Network"] == "192.168.1.100"
        assert result["Broadcast"] == "192.168.1.100"  # Same as network
        assert result["Hostmin"] == "192.168.1.100"    # Same as network
        assert result["Hostmax"] == "192.168.1.100"    # Same as network
        assert result["Hosts"] == "1*"                 # Single host

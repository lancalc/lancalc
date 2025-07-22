#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import iptools
import pytest
from ipaddress import IPv4Network
from main import LanCalc


def calculate_network_info(ip_addr, prefix):
    """
    Calculates network parameters by IP and prefix.
    Returns a dictionary with keys: network, prefix, netmask, broadcast, hostmin, hostmax, hosts
    """
    try:
        net = IPv4Network(f"{ip_addr}/{prefix}", strict=False)
        rang = iptools.IpRange(f'{ip_addr}/{prefix}')
        network = rang[0] if len(rang) > 0 else '-'
        broadcast = rang[-1] if len(rang) > 2 else '-'
        netmask = str(net.netmask)
        hostmin = rang[1] if len(rang) > 2 else rang[0]
        hostmax = rang[-2] if len(rang) > 2 else rang[-1]
        hosts = len(rang) - 2 if len(rang) > 2 else len(rang)
        hosts = str(hosts) if len(rang) > 2 else f"{hosts}*"
        return {
            'network': network,
            'prefix': f"/{prefix}",
            'netmask': netmask,
            'broadcast': broadcast,
            'hostmin': hostmin,
            'hostmax': hostmax,
            'hosts': hosts
        }
    except Exception as e:
        raise ValueError(str(e))


@pytest.mark.parametrize("ip,prefix,expected", [
    ("192.168.1.10", "24", {
        'network': '192.168.1.0',
        'prefix': '/24',
        'netmask': '255.255.255.0',
        'broadcast': '192.168.1.255',
        'hostmin': '192.168.1.1',
        'hostmax': '192.168.1.254',
        'hosts': '254'
    }),
    ("10.0.0.1", "8", {
        'network': '10.0.0.0',
        'prefix': '/8',
        'netmask': '255.0.0.0',
        'broadcast': '10.255.255.255',
        'hostmin': '10.0.0.1',
        'hostmax': '10.255.255.254',
        'hosts': '16777214'
    }),
    ("172.16.5.4", "16", {
        'network': '172.16.0.0',
        'prefix': '/16',
        'netmask': '255.255.0.0',
        'broadcast': '172.16.255.255',
        'hostmin': '172.16.0.1',
        'hostmax': '172.16.255.254',
        'hosts': '65534'
    }),
    ("192.168.1.1", "32", {
        'network': '192.168.1.1',
        'prefix': '/32',
        'netmask': '255.255.255.255',
        'broadcast': '-',
        'hostmin': '192.168.1.1',
        'hostmax': '192.168.1.1',
        'hosts': '1*'
    }),
])
def test_calculate_network_info(ip, prefix, expected):
    result = calculate_network_info(ip, prefix)
    for key in expected:
        assert result[key] == expected[key], f"{key}: {result[key]} != {expected[key]}"


def test_invalid_ip():
    with pytest.raises(ValueError):
        calculate_network_info("999.999.999.999", "24")


def test_invalid_prefix():
    with pytest.raises(ValueError):
        calculate_network_info("192.168.1.1", "40")

# --- GUI tests ---


@pytest.fixture
def app(qtbot):
    test_app = LanCalc()
    qtbot.addWidget(test_app)
    return test_app


def test_window_launch(app):
    assert app.isVisible() is False  # Window is not shown by default
    app.show()
    assert app.isVisible() is True
    assert app.windowTitle() == 'LanCalc'

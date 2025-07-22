#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from PyQt5.QtCore import Qt
from main import LanCalc

# Data for tests
test_cases = [
    ("192.168.1.1", "24", {
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
    ("172.16.0.1", "16", {
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
        'broadcast': '-',
        'hostmin': '192.168.2.1',
        'hostmax': '192.168.2.1',
        'hosts': '1*',
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
    }),
]

@pytest.fixture
def app(qtbot):
    test_app = LanCalc()
    qtbot.addWidget(test_app)
    return test_app

@pytest.mark.parametrize("ip,prefix,expected", test_cases)
def test_lancalc_calculate(app, ip, prefix, expected):
    # Set IP
    app.ip_input.setText(ip)
    # Set prefix in combobox
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
    color = app.ip_input.palette().color(app.ip_input.foregroundRole()).name()
    if expected['ip_color'] == 'red':
        assert 'red' in app.ip_input.styleSheet()
    else:
        assert 'color: black' in app.ip_input.styleSheet() or app.ip_input.styleSheet() == ''

def test_window_launch(app):
    assert app.isVisible() is False  # Window is not shown by default
    app.show()
    assert app.isVisible() is True
    assert app.windowTitle() == 'LanCalc'

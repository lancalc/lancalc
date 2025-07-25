#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import ipaddress
import iptools
import netifaces
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeyEvent

VERSION = '0.1.3'


class ClickToCopyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)  # Call base class to handle the event
        self.selectAll()                 # Select all text in the field
        QApplication.clipboard().setText(self.text())  # Copy text to clipboard


class IpInputLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def focusInEvent(self, event):
        self.setStyleSheet("color: black;")
        super().focusInEvent(event)


class LanCalc(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.check_clipboard()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        self.setWindowTitle('LanCalc')

        # Define the width for all input elements and font
        input_width = 200
        font = QFont('Ubuntu', 12)

        # Style for read-only fields
        readonly_style = "QLineEdit { background-color: #f0f0f0; color: #333; text-align: right; }"

        # IP Address Input
        ip_layout = QHBoxLayout()
        ip_label = QLabel("IP Address")
        ip_label.setFont(font)
        self.ip_input = IpInputLineEdit(self)
        self.ip_input.setFont(font)
        self.ip_input.setFixedWidth(input_width)
        self.ip_input.setAlignment(Qt.AlignRight)
        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(self.ip_input)
        main_layout.addLayout(ip_layout)

        # Network Mask Selector
        network_layout = QHBoxLayout()
        network_label = QLabel("Subnet")
        network_label.setFont(font)
        self.network_selector = QComboBox(self)
        self.network_selector.setFont(font)
        for cidr in range(33):
            mask = str(ipaddress.IPv4Network(f'0.0.0.0/{cidr}', strict=False).netmask)
            self.network_selector.addItem(f'{cidr}/{mask}')
        self.network_selector.setFixedWidth(input_width)
        network_layout.addWidget(network_label)
        network_layout.addWidget(self.network_selector)
        main_layout.addLayout(network_layout)

        # Set default values from system
        self.set_default_values()

        # Calculate Button
        self.calc_button = QPushButton('Calculate', self)
        self.calc_button.setFont(font)
        self.calc_button.clicked.connect(self.calculate_network)
        main_layout.addWidget(self.calc_button)

        # Output fields initialization
        self.network_output = ClickToCopyLineEdit(self)
        self.prefix_output = ClickToCopyLineEdit(self)
        self.netmask_output = ClickToCopyLineEdit(self)
        self.broadcast_output = ClickToCopyLineEdit(self)
        self.hostmin_output = ClickToCopyLineEdit(self)
        self.hostmax_output = ClickToCopyLineEdit(self)
        self.hosts_output = ClickToCopyLineEdit(self)

        # Apply read-only style and add output fields to the layout
        for field in [
                self.network_output,
                self.prefix_output,
                self.netmask_output,
                self.broadcast_output,
                self.hostmin_output,
                self.hostmax_output,
                self.hosts_output]:
            field.setReadOnly(True)
            field.setStyleSheet(readonly_style)
            field.setAlignment(Qt.AlignRight)  # Align text to the right
            field.setFont(font)
            field.setFixedWidth(input_width)  # Set fixed width to align with other input fields

        # Adding output fields to the layout
        self.add_output_field(main_layout, "Network", self.network_output)
        self.add_output_field(main_layout, "Prefix", self.prefix_output)
        self.add_output_field(main_layout, "Netmask", self.netmask_output)
        self.add_output_field(main_layout, "Broadcast", self.broadcast_output)
        self.add_output_field(main_layout, "Hostmin", self.hostmin_output)
        self.add_output_field(main_layout, "Hostmax", self.hostmax_output)
        self.add_output_field(main_layout, "Hosts", self.hosts_output)

        # add link to the repository
        self.link_label = QLabel(f'<a href="https://github.com/KPbICO6Ou/lancalc">LanCalc {VERSION}</a>')
        self.link_label.setOpenExternalLinks(True)
        self.link_label.setAlignment(Qt.AlignCenter)
        self.link_label.setFont(QFont('Ubuntu', 11))
        main_layout.addWidget(self.link_label)

        # Set Layout
        self.setLayout(main_layout)

    def check_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text()

        # Checking whether the clipboard contains an IP address with a mask
        match = re.match(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/(\d{1,2}))?$', clipboard_text)
        if match:
            ip_address = match.group(1)
            cidr = match.group(3)
            self.ip_input.setText(ip_address)
            if cidr:
                self.network_selector.setCurrentIndex(int(cidr))

    def set_default_values(self):
        try:
            gateways = netifaces.gateways()
            default_interface = gateways['default'][netifaces.AF_INET][1]
            addrs = netifaces.ifaddresses(default_interface)
            ip_info = addrs[netifaces.AF_INET][0]
            default_ip = ip_info['addr']
            netmask = ip_info['netmask']
            default_cidr = sum([bin(int(x)).count('1') for x in netmask.split('.')])

            self.ip_input.setText(default_ip)
            self.network_selector.setCurrentIndex(default_cidr)
        except Exception as e:
            print("Could not determine default network settings:", e)

    def add_output_field(self, layout, label_text, line_edit):
        field_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFont(QFont('Ubuntu', 13))
        line_edit.setReadOnly(True)
        field_layout.addWidget(label)
        field_layout.addWidget(line_edit)
        layout.addLayout(field_layout)

    def calculate_network(self, *args, **kwargs):
        try:
            self.ip_input.setStyleSheet("color: black;")
            ip_addr = self.ip_input.text()
            prefix, netmask = self.network_selector.currentText().split('/')
            rang = iptools.IpRange(f'{ip_addr}/{prefix}')
            self.network_output.setText(rang[0] if rang.__len__() > 0 else '-')
            self.broadcast_output.setText(rang[-1] if rang.__len__() > 2 else '-')
            self.prefix_output.setText(f"/{prefix}")
            self.netmask_output.setText(netmask)
            self.hostmin_output.setText(rang[1] if rang.__len__() > 2 else rang[0])
            self.hostmax_output.setText(rang[-2] if rang.__len__() > 2 else rang[-1])
            hosts = rang.__len__() - 2 if rang.__len__() > 2 else rang.__len__()
            hosts = str(hosts) if rang.__len__() > 2 else f"{hosts}*"
            self.hosts_output.setText(hosts)
        except (ValueError, TypeError):
            self.ip_input.setStyleSheet("color: red;")
            self.network_output.setText("")
            self.prefix_output.setText("")
            self.netmask_output.setText("")
            self.broadcast_output.setText("")
            self.hostmin_output.setText("")
            self.hostmax_output.setText("")
            self.hosts_output.setText("")

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return:
            self.calculate_network()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = LanCalc()
    ex.show()
    sys.exit(app.exec_())

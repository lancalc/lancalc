#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graphical user interface for LanCalc.
"""
import ipaddress
import logging
import traceback
import platform
import re
import subprocess
import sys

logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stderr)
    ],
    level=logging.WARNING,
    format='%(asctime)s.%(msecs)03d [%(levelname)s]: (%(name)s.%(funcName)s) - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Import modules
try:
    from . import core
    REPO_URL = core.REPO_URL
except ImportError:
    import core
    from core import REPO_URL

try:
    import lancalc
    VERSION = lancalc.__version__
except Exception:
    VERSION = "0.0.0"

# Try to import PyQt5
try:
    from PyQt5.QtWidgets import (
        QApplication,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QComboBox,
    )
    from PyQt5.QtCore import Qt, QEvent
    from PyQt5.QtGui import QFont, QKeyEvent

    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    logger.warning("PyQt5 not available - GUI mode disabled")

    # Mock classes for when GUI is not available
    class QKeyEvent:
        pass

    class QFont:
        def __init__(self, *args, **kwargs):
            pass

        Bold = 75


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
                            if (
                                route_line.strip()
                                and ip.split(".")[:3]
                                == route_line.split()[0].split(".")[:3]
                            ):
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
                                if (
                                    other_line.strip()
                                    and gateway_ip.split(".")[:3]
                                    == other_line.split()[0].split(".")[:3]
                                ):
                                    cidr_match = re.search(r"/(\d+)", other_line)
                                    if cidr_match:
                                        return int(cidr_match.group(1))
                            break
    except Exception as e:
        logger.error(f"Linux CIDR detection failed: {type(e).__name__} {str(e)}")
    return 24


class IpInputLineEdit(QLineEdit):
    """Custom QLineEdit for IP address input with validation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("192.168.1.1")
        # Remove textChanged connection - validation only on focus events

    def focusInEvent(self, event):
        """Reset styling when focus is gained."""
        super().focusInEvent(event)
        self.setStyleSheet("")  # Reset to normal color

    def focusOutEvent(self, event):
        """Validate when focus is lost."""
        super().focusOutEvent(event)
        # Validation will be handled by parent's eventFilter


class ClickToCopyLineEdit(QLineEdit):
    """QLineEdit that copies text to clipboard when clicked."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

    def mousePressEvent(self, event):
        """Copy text to clipboard when clicked."""
        super().mousePressEvent(event)
        if self.text():
            clipboard = QApplication.clipboard()
            clipboard.setText(self.text())


class LanCalcGUI(QWidget):
    def __init__(self):
        super().__init__()
        logger.info("Initializing LanCalc application")
        self.init_ui()
        self.check_clipboard()
        logger.info("LanCalc application initialized successfully")

    def init_ui(self):
        try:
            main_layout = QVBoxLayout()
            self.setWindowTitle("LanCalc")
            input_width = 200
            font = QFont("Ubuntu", 12)  # 12
            # Fallback font if Ubuntu is not available
            if not font.exactMatch():
                font = QFont("Arial", 12)
            readonly_style = "QLineEdit { background-color: #f0f0f0; color: #333; text-align: right; }"

            ip_layout = QHBoxLayout()
            ip_label = QLabel("IP Address")
            ip_label.setFont(font)
            self.ip_input = IpInputLineEdit(self)
            self.ip_input.setFont(font)
            self.ip_input.setFixedWidth(input_width)
            self.ip_input.setAlignment(Qt.AlignRight)
            ip_layout.addWidget(ip_label)
            ip_layout.addWidget(self.ip_input)
            # Defer parsing "IP/prefix" until focus is lost or Enter/Tab is pressed
            self.ip_input.installEventFilter(self)
            main_layout.addLayout(ip_layout)

            network_layout = QHBoxLayout()
            network_label = QLabel("Subnet")
            network_label.setFont(font)
            self.network_selector = QComboBox(self)
            self.network_selector.setFont(font)
            for cidr in range(33):
                mask = str(
                    ipaddress.IPv4Network(f"0.0.0.0/{cidr}", strict=False).netmask
                )
                self.network_selector.addItem(f"{cidr}/{mask}")
            self.network_selector.setFixedWidth(input_width)
            network_layout.addWidget(network_label)
            network_layout.addWidget(self.network_selector)
            main_layout.addLayout(network_layout)

            self.set_default_values()

            self.calc_button = QPushButton("Calculate", self)
            self.calc_button.setFont(font)
            self.calc_button.clicked.connect(self.calculate_network)
            main_layout.addWidget(self.calc_button)

            self.network_output = ClickToCopyLineEdit(self)
            self.prefix_output = ClickToCopyLineEdit(self)
            self.netmask_output = ClickToCopyLineEdit(self)
            self.broadcast_output = ClickToCopyLineEdit(self)
            self.hostmin_output = ClickToCopyLineEdit(self)
            self.hostmax_output = ClickToCopyLineEdit(self)
            self.hosts_output = ClickToCopyLineEdit(self)

            for field in [
                self.network_output,
                self.prefix_output,
                self.netmask_output,
                self.broadcast_output,
                self.hostmin_output,
                self.hostmax_output,
                self.hosts_output,
            ]:
                field.setReadOnly(True)
                field.setStyleSheet(readonly_style)
                field.setAlignment(Qt.AlignRight)
                field.setFont(font)
                field.setFixedWidth(input_width)

            self.add_output_field(main_layout, "Network", self.network_output)
            self.add_output_field(main_layout, "Prefix", self.prefix_output)
            self.add_output_field(main_layout, "Netmask", self.netmask_output)
            self.add_output_field(main_layout, "Broadcast", self.broadcast_output)
            self.add_output_field(main_layout, "Hostmin", self.hostmin_output)
            self.add_output_field(main_layout, "Hostmax", self.hostmax_output)
            self.add_output_field(main_layout, "Hosts", self.hosts_output)

            # Status bar at bottom - shows version or special range message
            self.status_label = QLabel(f'<a href="{REPO_URL}">LanCalc {VERSION}</a>')
            self.status_label.setOpenExternalLinks(True)
            self.status_label.setAlignment(Qt.AlignCenter)
            status_font = QFont("Ubuntu", 11)  # 11
            if not status_font.exactMatch():
                status_font = QFont("Arial", 11)
            self.status_label.setFont(status_font)
            main_layout.addWidget(self.status_label)

            self.setLayout(main_layout)

            # Perform initial calculation after all UI elements are created
            try:
                self.calculate_network()
            except Exception as e:
                logger.error(
                    f"Failed to perform initial calculation: {type(e).__name__} {str(e)}"
                )

        except Exception as e:
            logging.error(
                f"Failed to initialize UI: {type(e).__name__} {str(e)}\n{traceback.format_exc()}"
            )

    def apply_cidr_from_text(self, text: str) -> None:
        """Apply CIDR from the IP input when triggered (focus out or Enter/Tab).

        This handles cases where user enters "IP/prefix" in the IP field.
        """
        if "/" in text:
            try:
                ip, prefix_str = text.split("/", 1)
                try:
                    core.validate_ip(ip)
                    prefix = core.validate_prefix(prefix_str)
                    if 0 <= prefix <= 32:
                        self.ip_input.setText(ip)
                        self.network_selector.setCurrentIndex(prefix)
                        return
                except Exception:
                    pass  # Invalid IP or prefix, don't apply
            except Exception as e:
                logger.error(
                    f"Failed to parse IP/prefix from text: {type(e).__name__} {str(e)}"
                )

    def eventFilter(self, obj, event):
        """Event filter for IP input field."""
        if obj == self.ip_input and event.type() == QEvent.FocusOut:
            self.apply_cidr_from_text(self.ip_input.text())
        elif obj == self.ip_input and event.type() == QEvent.KeyPress:
            key_event = QKeyEvent(event)
            if key_event.key() in [Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab]:
                self.apply_cidr_from_text(self.ip_input.text())
        return super().eventFilter(obj, event)

    def set_default_values(self):
        """Set default values for the interface."""
        try:
            # Get local IP as default
            local_ip = core.get_ip()
            logger.info(f"Detected local IP: {local_ip}")

            try:
                core.validate_ip(local_ip)
                self.ip_input.setText(local_ip)
                logger.info(f"Set IP input to: {local_ip}")
            except Exception as e:
                self.ip_input.setText("192.168.1.1")
                logger.warning(
                    f"Invalid IP detected: {local_ip}, error: {e}, using fallback: 192.168.1.1"
                )

            # Set default CIDR (try to detect, fallback to /24)
            try:
                detected_cidr = get_cidr(self.ip_input.text())
                self.network_selector.setCurrentIndex(detected_cidr)
                logger.info(f"Set CIDR selector to: /{detected_cidr}")
            except Exception as e:
                self.network_selector.setCurrentIndex(24)  # Default to /24
                logger.warning(f"Failed to detect CIDR: {e}, using fallback: /24")

        except Exception as e:
            logger.error(f"Failed to set default values: {type(e).__name__} {str(e)}")
            self.ip_input.setText("192.168.1.1")
            self.network_selector.setCurrentIndex(24)

    def add_output_field(self, layout, label_text: str, field):
        """Add a labeled output field to the layout."""
        field_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFont(field.font())
        field_layout.addWidget(label)
        field_layout.addWidget(field)
        layout.addLayout(field_layout)

    # --- Validation helpers used by tests ---
    def validate_ip_address(self, ip: str) -> bool:
        try:
            core.validate_ip(ip)
            return True
        except Exception:
            return False

    def validate_cidr(self, cidr: str) -> bool:
        try:
            core.validate_prefix(cidr)
            return True
        except Exception:
            return False

    def check_clipboard(self):
        """Check clipboard for IP address and offer to use it."""
        try:
            clipboard = QApplication.clipboard()
            text = clipboard.text().strip()

            # Check if clipboard contains a valid IP
            try:
                core.validate_ip(text)
                is_valid_ip = True
            except Exception:
                is_valid_ip = False
            if is_valid_ip:
                # Don't auto-paste, just log for now
                logger.info(f"Clipboard contains valid IP: {text}")
            elif "/" in text:
                # Check if it's a valid CIDR
                try:
                    ip, prefix_str = text.split("/", 1)
                    try:
                        core.validate_ip(ip)
                        core.validate_prefix(prefix_str)
                        is_valid_cidr = True
                    except Exception:
                        is_valid_cidr = False
                    if is_valid_cidr:
                        logger.info(f"Clipboard contains valid CIDR: {text}")
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Failed to check clipboard: {type(e).__name__} {str(e)}")

    def calculate_network(self):
        """Calculate network information and update the display."""
        try:
            ip = self.ip_input.text().strip()
            logger.info(f"Calculating network for IP: {ip}")

            if not ip:
                self.ip_input.setStyleSheet("color: red;")
                self.status_label.setText("Wrong Address")
                # Clear output fields
                self.network_output.clear()
                self.prefix_output.clear()
                self.netmask_output.clear()
                self.broadcast_output.clear()
                self.hostmin_output.clear()
                self.hostmax_output.clear()
                self.hosts_output.clear()
                return

            try:
                core.validate_ip(ip)
            except Exception:
                self.ip_input.setStyleSheet("color: red;")
                self.status_label.setText("Wrong Address")
                # Clear output fields
                self.network_output.clear()
                self.prefix_output.clear()
                self.netmask_output.clear()
                self.broadcast_output.clear()
                self.hostmin_output.clear()
                self.hostmax_output.clear()
                self.hosts_output.clear()
                return

            # Get CIDR from selector
            cidr = self.network_selector.currentIndex()
            logger.info(f"Using CIDR: /{cidr}")

            # Calculate network information
            result = core.compute_from_cidr(f"{ip}/{cidr}")

            # Update output fields
            self.network_output.setText(result["network"])
            self.prefix_output.setText(result["prefix"])
            self.netmask_output.setText(result["netmask"])
            self.broadcast_output.setText(result["broadcast"])
            self.hostmin_output.setText(result["hostmin"])
            self.hostmax_output.setText(result["hostmax"])
            self.hosts_output.setText(result["hosts"])

            # Update status with special range info if present
            if result.get("comment"):
                # Check if comment contains RFC reference
                if "RFC" in result["comment"]:
                    # Extract the URL from the comment (it's already in the correct format)
                    import re

                    url_match = re.search(r"\((https://[^)]+)\)", result["comment"])
                    if url_match:
                        rfc_url = url_match.group(1)
                        # Extract text before the URL (e.g., "RFC 3330 Loopback" from "RFC 3330 Loopback (https://...)")
                        comment_text = result["comment"].split(" (")[0]
                        self.status_label.setText(
                            f'<a href="{rfc_url}">{comment_text}</a>'
                        )
                    else:
                        self.status_label.setText(result["comment"])
                else:
                    self.status_label.setText(result["comment"])
            else:
                try:
                    import lancalc
                    version = lancalc.__version__
                except Exception:
                    version = "0.0.0"
                self.status_label.setText(f'<a href="{REPO_URL}">LanCalc {version}</a>')

            # Clear error styling
            self.ip_input.setStyleSheet("")

        except Exception as e:
            logger.error(
                f"Calculation failed: {type(e).__name__} {str(e)}\n{traceback.format_exc()}"
            )
            self.status_label.setText("Calculation Error")


def run_gui() -> int:
    """
    Run GUI mode.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        if not GUI_AVAILABLE:
            print("GUI not available - PyQt5 not installed", file=sys.stderr)
            return 1

        app = QApplication(sys.argv)
        window = LanCalcGUI()
        window.show()
        return app.exec_()
    except Exception as e:
        logger.error(
            f"GUI failed: {type(e).__name__} {str(e)}\n{traceback.format_exc()}"
        )
        return 1


def main() -> int:
    """Alias for run_gui for backward compatibility."""
    return run_gui()


if __name__ == "__main__":
    sys.exit(main())

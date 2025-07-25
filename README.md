LanCalc is a desktop application built with PyQt5, designed to calculate network configurations for Windows and Linux systems.

![image](https://github.com/user-attachments/assets/99458a02-5df0-4b0c-8948-4ad49d678d73)

[Download](https://github.com/lancalc/lancalc/releases)

It provides a user-friendly interface to compute essential network parameters such as network address, broadcast address, the minimum and maximum host addresses, and the number of hosts within a given subnet. 

Support IPv4 address formats, subnet masks and prefixes. This tool is particularly useful for network administrators and IT professionals who require quick calculations of network parameters.

License

Distributed under the MIT License. See LICENSE for more information.

## Dependencies
Python 3.7+ is required, along with the following libraries:

```bash
pip3 install -r requirements.txt
```

## Running the Application

```bash
python3 main.py
```

## For Developers

```bash
pip3 install pre-commit flake8 pytest pytest-qt
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

## Contact

[GitHub](https://github.com/lancalc/lancalc) [Telegram](https://t.me/wachawo) 

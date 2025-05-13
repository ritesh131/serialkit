# serialkit

A Python toolkit for serial and USB communication, offering dynamic configuration and command-based interaction with hardware devices. `serialkit` is designed for developers working with serial ports, IoT devices, microcontrollers, and USB-to-serial adapters, providing a robust and flexible interface for sending commands and reading responses.

## Features
- **Dynamic Configuration**: Customize baud rate, parity, stop bits, and more.
- **Command-Based Interaction**: Send commands to devices and parse responses with custom functions.
- **Thread-Safe**: Safe for concurrent use with built-in locking.
- **Error Handling**: Comprehensive exception handling for reliable operation.
- **Obfuscated Code**: Distributed as obfuscated code to protect intellectual property.

## Installation

### Prerequisites
- Python 3.6 or higher
- A virtual environment (recommended)
- `pyserial` library (installed automatically)

### Steps
1. Activate your virtual environment (if using one):
   ```bash
   source env/bin/activate  # Linux/macOS
   env\Scripts\activate     # Windows
   ```
2. Install `serialkit` via PyPI:
   ```bash
   pip install serialkit
   ```
3. Verify installation:
   ```python
   python -c "import serialkit; print(serialkit.__version__)"
   ```
   Output: `0.2.0`

## Usage

### Basic Connection
Connect to a serial port and read raw data:
```python
from serialkit import SerialFetcher
import logging

try:
    # List available ports
    ports = SerialFetcher.list_ports()
    print(f"Available ports: {ports}")

    # Initialize and connect
    fetcher = SerialFetcher(port="/dev/ttyACM0", baudrate=9600, log_level=logging.DEBUG)
    fetcher.connect()

    # Read data
    data = fetcher.read_data(size=1024)
    print(f"Received: {data}")

    fetcher.disconnect()
except Exception as e:
    print(f"Error: {e}")
```

### Command-Based Interaction
Send commands to a device and parse the response:
```python
from serialkit import SerialFetcher
import logging

def parse_response(data: bytes) -> list:
    """Parse response by splitting into lines."""
    try:
        return data.decode('utf-8').strip().split('\n')
    except UnicodeDecodeError:
        return []

try:
    fetcher = SerialFetcher(port="/dev/ttyACM0", baudrate=9600, log_level=logging.DEBUG)
    fetcher.connect()

    # Send a command
    response = fetcher.send_command("STATUS\n", parse_response=parse_response)
    print(f"Response: {response}")

    fetcher.disconnect()
except Exception as e:
    print(f"Error: {e}")
```

### Advanced Example: Custom Response Parsing
Parse key-value pairs from a device’s response:
```python
from serialkit import SerialFetcher
import logging

def parse_key_value(data: bytes) -> dict:
    """Parse response as key-value pairs."""
    try:
        text = data.decode('utf-8')
        return dict(line.split('=') for line in text.strip().split('\n') if '=' in line)
    except UnicodeDecodeError:
        return {}

try:
    fetcher = SerialFetcher(port="/dev/ttyACM0", baudrate=115200, log_level=logging.DEBUG)
    fetcher.connect()

    # Send multiple commands
    commands = ["CONFIG\n", "INFO\n"]
    for cmd in commands:
        response = fetcher.send_command(cmd, parse_response=parse_key_value)
        print(f"Command: {cmd.strip()}, Response: {response}")

    fetcher.disconnect()
except Exception as e:
    print(f"Error: {e}")
```

## License
`serialkit` is distributed under a proprietary license. You may use it for personal or commercial projects but may not modify, reverse-engineer, or redistribute it. The library is provided as obfuscated code to protect the source code. See [LICENSE.txt](LICENSE.txt) for full details.

## Obfuscation
To protect intellectual property, `serialkit` is distributed as obfuscated code using PyArmor. Source code is not provided, and reverse-engineering is prohibited under the license terms.

## Testing
To test `serialkit` locally:
1. **Unit Tests**: Run included tests with `pytest`:
   ```bash
   pytest tests/test_serialkit.py -v
   ```
2. **Hardware Testing**: Use a serial device (e.g., `/dev/ttyACM0` on Linux):
   - Ensure your user is in the `dialout` group:
     ```bash
     sudo usermod -a -G dialout $USER
     ```
     Log out and back in to apply.
   - Test with the usage examples above.
3. **Virtual Ports**: Simulate a device with `socat` (Linux/macOS):
   ```bash
   socat -d -d pty,raw,echo=0 pty,raw,echo=0
   ```
   Use the advanced example with ports like `/dev/pts/2` and `/dev/pts/3`.

## Contributing
Contributions are not accepted, as the source code is proprietary and obfuscated. For bug reports or feature requests, contact the author at [bajpairitesh878@gmail.com].

## Contact
- Author: Ritesh Bajpai
- Email: [bajpairitesh878@gmail.com]
- GitHub: [https://github.com/yourusername/serialkit]

## Notes
- Ensure the correct baud rate and port for your device (e.g., `115200` for some microcontrollers).
- Debug with `log_level=logging.DEBUG` for detailed logs.
- Check PyPI for the latest version: [https://pypi.org/project/serialkit/](https://pypi.org/project/serialkit/)
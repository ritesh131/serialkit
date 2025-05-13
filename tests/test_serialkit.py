import pytest
import serial
from serialkit import SerialFetcher, SerialFetchError
from unittest.mock import Mock, patch
import threading
import logging

# Set up logging for debugging tests (optional)
logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def serialkiter():
    """Fixture to create a SerialFetcher instance with default settings.

    Yields a SerialFetcher object and ensures disconnection after each test.
    """
    fetcher = SerialFetcher(port="COM1", baudrate=9600, timeout=0.1)
    yield fetcher
    if fetcher.is_connected:
        fetcher.disconnect()

def test_list_ports():
    """Test listing available serial ports.

    Verifies that list_ports() returns a list, which may be empty or contain port names.
    """
    ports = SerialFetcher.list_ports()
    assert isinstance(ports, list), "list_ports() must return a list"

def test_connect_success(serialkiter):
    """Test successful connection to a serial port.

    Mocks serial.Serial to simulate a successful connection and verifies
    that is_connected is True and the correct parameters are passed.
    """
    with patch("serial.Serial") as mock_serial:
        serialkiter.connect()
        assert serialkiter.is_connected, "is_connected should be True after connect"
        mock_serial.assert_called_once_with(
            port="COM1",
            baudrate=9600,
            timeout=0.1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )

def test_connect_failure(serialkiter):
    """Test handling of connection failure.

    Simulates a SerialException during connection and checks if SerialFetchError is raised.
    """
    with patch("serial.Serial", side_effect=serial.SerialException("Port not found")):
        with pytest.raises(SerialFetchError, match="Failed to connect"):
            serialkiter.connect()
        assert not serialkiter.is_connected, "is_connected should be False after failure"

def test_connect_already_connected(serialkiter):
    """Test connecting when already connected.

    Ensures that attempting to connect again raises SerialFetchError.
    """
    with patch("serial.Serial") as mock_serial:
        serialkiter.connect()
        with pytest.raises(SerialFetchError, match="Already connected"):
            serialkiter.connect()

def test_disconnect_success(serialkiter):
    """Test successful disconnection.

    Verifies that disconnect() sets is_connected to False and closes the serial connection.
    """
    with patch("serial.Serial") as mock_serial:
        mock_instance = mock_serial.return_value
        serialkiter.connect()
        serialkiter.disconnect()
        assert not serialkiter.is_connected, "is_connected should be False after disconnect"
        mock_instance.close.assert_called_once()

def test_disconnect_not_connected(serialkiter):
    """Test disconnecting when not connected.

    Ensures that disconnect() on a non-connected instance does not raise errors.
    """
    serialkiter.disconnect()  # Should not raise
    assert not serialkiter.is_connected, "is_connected should remain False"

def test_read_data_not_connected(serialkiter):
    """Test reading data when not connected.

    Verifies that read_data() raises SerialFetchError if not connected.
    """
    with pytest.raises(SerialFetchError, match="Not connected"):
        serialkiter.read_data(size=1024)

def test_read_data_success(serialkiter):
    """Test reading data from a connected serial port.

    Mocks a successful read and verifies the returned data.
    """
    with patch("serial.Serial") as mock_serial:
        mock_instance = mock_serial.return_value
        mock_instance.read.return_value = b"DATA\n"
        serialkiter.connect()
        data = serialkiter.read_data(size=1024)
        assert data == b"DATA\n", "read_data should return the mocked data"
        mock_instance.read.assert_called_once_with(1024)

def test_read_data_timeout(serialkiter):
    """Test reading data with a timeout.

    Simulates a timeout (empty read) and verifies that empty data is returned.
    """
    with patch("serial.Serial") as mock_serial:
        mock_instance = mock_serial.return_value
        mock_instance.read.return_value = b""
        serialkiter.connect()
        data = serialkiter.read_data(size=1024)
        assert data == b"", "read_data should return empty bytes on timeout"

def test_send_command_success(serialkiter):
    """Test sending a command and receiving a response.

    Mocks a successful command-response cycle and verifies the response.
    """
    with patch("serial.Serial") as mock_serial:
        mock_instance = mock_serial.return_value
        mock_instance.read.return_value = b"OK\n"
        serialkiter.connect()
        response = serialkiter.send_command("TEST\n")
        assert response == b"OK\n", "send_command should return the mocked response"
        mock_instance.write.assert_called_once_with(b"TEST\n")
        mock_instance.read.assert_called_once()

def test_send_command_with_parser(serialkiter):
    """Test sending a command with a custom response parser.

    Verifies that the parser is applied to the response correctly.
    """
    def parse_response(data: bytes) -> list:
        return data.decode('utf-8').strip().split('\n')

    with patch("serial.Serial") as mock_serial:
        mock_instance = mock_serial.return_value
        mock_instance.read.return_value = b"LINE1\nLINE2\n"
        serialkiter.connect()
        response = serialkiter.send_command("INFO\n", parse_response=parse_response)
        assert response == ["LINE1", "LINE2"], "send_command should return parsed response"
        mock_instance.write.assert_called_once_with(b"INFO\n")

def test_send_command_not_connected(serialkiter):
    """Test sending a command when not connected.

    Verifies that send_command() raises SerialFetchError if not connected.
    """
    with pytest.raises(SerialFetchError, match="Not connected"):
        serialkiter.send_command("TEST\n")

def test_send_command_failure(serialkiter):
    """Test handling of command failure.

    Simulates a SerialException during write and checks if SerialFetchError is raised.
    """
    with patch("serial.Serial") as mock_serial:
        mock_instance = mock_serial.return_value
        mock_instance.write.side_effect = serial.SerialException("Write error")
        serialkiter.connect()
        with pytest.raises(SerialFetchError, match="Error in command-response"):
            serialkiter.send_command("TEST\n")

def test_thread_safety_send_command(serialkiter):
    """Test thread safety of send_command.

    Simulates multiple threads sending commands concurrently to ensure thread-safe operation.
    """
    def send_command_task(fetcher, cmd):
        response = fetcher.send_command(cmd)
        return response

    with patch("serial.Serial") as mock_serial:
        mock_instance = mock_serial.return_value
        mock_instance.read.side_effect = [b"OK1\n", b"OK2\n"]
        serialkiter.connect()

        threads = []
        commands = ["CMD1\n", "CMD2\n"]
        for cmd in commands:
            thread = threading.Thread(target=send_command_task, args=(serialkiter, cmd))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert mock_instance.write.call_count == 2, "All commands should be sent"
        assert mock_instance.read.call_count == 2, "All responses should be read"

def test_invalid_baudrate():
    """Test initialization with an invalid baud rate.

    Verifies that an invalid baud rate raises SerialFetchError.
    """
    with pytest.raises(SerialFetchError, match="Invalid baudrate"):
        SerialFetcher(port="COM1", baudrate=-1)

def test_logging_enabled():
    """Test that logging is enabled and functional.

    Verifies that debug logging messages are generated during connect.
    """
    with patch("serial.Serial") as mock_serial:
        with patch("logging.Logger.debug") as mock_logger:
            fetcher = SerialFetcher(port="COM1", baudrate=9600, log_level=logging.DEBUG)
            fetcher.connect()
            assert mock_logger.called, "Logger should be called for debugging"

def test_get_config(serialkiter):
    """Test retrieving the current serial configuration.

    Verifies that get_config() returns the correct settings.
    """
    config = serialkiter.get_config()
    expected = {
        "port": "COM1",
        "baudrate": 9600,
        "timeout": 0.1,
        "parity": serial.PARITY_NONE,
        "stopbits": serial.STOPBITS_ONE,
        "bytesize": serial.EIGHTBITS
    }
    assert config == expected, "get_config should return the correct configuration"

def test_flush_success(serialkiter):
    """Test flushing input and output buffers.

    Verifies that flush() calls flushInput and flushOutput on the serial object.
    """
    with patch("serial.Serial") as mock_serial:
        mock_instance = mock_serial.return_value
        serialkiter.connect()
        serialkiter.flush()
        mock_instance.flushInput.assert_called_once()
        mock_instance.flushOutput.assert_called_once()

def test_flush_not_connected(serialkiter):
    """Test flushing when not connected.

    Verifies that flush() raises SerialFetchError if not connected.
    """
    with pytest.raises(SerialFetchError, match="Not connected"):
        serialkiter.flush()

def test_help_method(serialkiter):
    """Test the __help__ method.

    Verifies that __help__ returns a non-empty string with usage information.
    """
    help_text = serialkiter.__help__()
    assert isinstance(help_text, str), "__help__ should return a string"
    assert len(help_text) > 0, "__help__ should not be empty"
    assert "SerialFetcher" in help_text, "__help__ should mention SerialFetcher"

def test_dir_method(serialkiter):
    """Test the __dir__ method.

    Verifies that __dir__ returns a list of public methods and attributes.
    """
    dir_list = dir(serialkiter)
    expected = [
        'port', 'baudrate', 'timeout', 'parity', 'stopbits', 'bytesize',
        'is_connected', 'log_level', 'list_ports', 'connect', 'disconnect',
        'read_data', 'send_command', 'get_config', 'flush', '__help__', '__dir__'
    ]
    assert sorted(dir_list) == sorted(expected), "__dir__ should return public attributes and methods"
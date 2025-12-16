from __future__ import annotations

from typing import TYPE_CHECKING
import json
import re
import struct

from open_in_mpv.main import get_mpv_path, main, spawn
import pytest

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture


def test_get_mpv_path_default() -> None:
    """Test get_mpv_path returns 'mpv' by default."""
    result = get_mpv_path()
    assert result == 'mpv'


def test_get_mpv_path_windows_frozen_exists(mocker: MockerFixture) -> None:
    """Test get_mpv_path on Windows with PyInstaller bundle and mpv.exe exists."""
    mocker.patch('open_in_mpv.main.IS_WIN', new=True)
    mocker.patch('open_in_mpv.main.sys.frozen', new=True, create=True)
    mock_path = mocker.patch('open_in_mpv.main.Path')
    mock_path.return_value.parent.__truediv__.return_value.exists.return_value = True
    mock_path.return_value.parent.__truediv__.return_value.__str__.return_value = (
        'C:\\test\\mpv.exe')
    mocker.patch('open_in_mpv.main.sys.executable', 'C:\\test\\open-in-mpv.exe')

    result = get_mpv_path()
    assert result == 'C:\\test\\mpv.exe'


def test_get_mpv_path_windows_frozen_not_exists(mocker: MockerFixture) -> None:
    """Test get_mpv_path on Windows with PyInstaller bundle but mpv.exe doesn't exist."""
    mocker.patch('open_in_mpv.main.IS_WIN', new=True)
    mocker.patch('open_in_mpv.main.sys.frozen', new=True, create=True)
    mock_path = mocker.patch('open_in_mpv.main.Path')
    mock_path.return_value.parent.__truediv__.return_value.exists.return_value = False
    mocker.patch('open_in_mpv.main.sys.executable', 'C:\\test\\open-in-mpv.exe')

    result = get_mpv_path()
    assert result == 'mpv'


def test_get_mpv_path_windows_not_frozen(mocker: MockerFixture) -> None:
    """Test get_mpv_path on Windows but not in PyInstaller bundle."""
    mocker.patch('open_in_mpv.main.IS_WIN', new=True)
    # Don't set sys.frozen, so getattr returns False
    result = get_mpv_path()
    assert result == 'mpv'


def test_main_version(runner: CliRunner) -> None:
    result = runner.invoke(main, '--version')
    assert result.exit_code == 0
    assert re.match(r'^\d+\.\d+\.\d+', result.output.strip())


def test_main_version_alt(runner: CliRunner) -> None:
    result = runner.invoke(main, '-V')
    assert result.exit_code == 0
    assert re.match(r'^\d+\.\d+\.\d+', result.output.strip())


def test_main_shows_disclaimer(runner: CliRunner) -> None:
    result = runner.invoke(main, '-h')
    assert result.exit_code == 0
    assert ('This script is intended to be used with the Chrome extension. There is no CLI '
            'interface for general use.') in result.output


def test_main_init(runner: CliRunner) -> None:
    result = runner.invoke(main, ['chrome://aaa', '-'], input=b'\x0e\x00\x00\x00{"init": true}')
    assert result.exit_code == 0
    try:
        struct.unpack('@i', result.stdout_bytes[:4])
    except struct.error:
        pytest.fail('Failed to unpack size from stdout')
    data = json.loads(result.stdout_bytes[4:].decode())
    assert isinstance(data, dict)
    assert 'version' in data
    assert 'logPath' in data
    assert 'socketPath' in data


def test_main_no_url(runner: CliRunner) -> None:
    result = runner.invoke(main, ['chrome://aaa', '-'], input=b'\x02\x00\x00\x00{}')
    assert result.exit_code != 0


def test_main_bad_url(runner: CliRunner) -> None:
    result = runner.invoke(main, ['chrome://aaa', '-'], input=b'\x0e\x00\x00\x00{"url": "bad"}')
    assert result.exit_code != 0


def test_main(runner: CliRunner, mocker: MockerFixture) -> None:
    mpv_socket_path = mocker.patch('open_in_mpv.main.MPV_SOCKET')
    mpv_socket_path.exists.return_value = False
    mock_os = mocker.patch('open_in_mpv.main.os')
    mock_os.fork.side_effect = [1, 1]
    mock_os.environ.copy.return_value = {'PATH': '/usr/bin'}
    mocker.patch('open_in_mpv.main.sp.run')
    result = runner.invoke(main, ['chrome://aaa', '-'],
                           input=b'\x1e\x00\x00\x00{"url": "https://example.com"}')
    assert result.exit_code == 0


def test_main_os_fork_fail(runner: CliRunner, mocker: MockerFixture) -> None:
    mpv_socket_path = mocker.patch('open_in_mpv.main.MPV_SOCKET')
    mpv_socket_path.exists.return_value = False
    mock_os = mocker.patch('open_in_mpv.main.os')
    mock_os.environ.copy.return_value = {'PATH': '/usr/bin'}
    mock_os.fork.side_effect = OSError
    result = runner.invoke(main, ['chrome://aaa', '-'],
                           input=b'\x1e\x00\x00\x00{"url": "https://example.com"}')
    assert result.exit_code == 1


def test_main_os_fork_fail_2(runner: CliRunner, mocker: MockerFixture) -> None:
    mpv_socket_path = mocker.patch('open_in_mpv.main.MPV_SOCKET')
    mpv_socket_path.exists.return_value = False
    mock_os = mocker.patch('open_in_mpv.main.os')
    mock_os.environ.copy.return_value = {'PATH': '/usr/bin'}
    mock_os.fork.side_effect = [0, OSError]
    result = runner.invoke(main, ['chrome://aaa', '-'],
                           input=b'\x1e\x00\x00\x00{"url": "https://example.com"}')
    assert result.exit_code == 1


def test_main_os_fork_ok(runner: CliRunner, mocker: MockerFixture) -> None:
    mpv_socket_path = mocker.patch('open_in_mpv.main.MPV_SOCKET')
    mpv_socket_path.exists.return_value = False
    mocker.patch('open_in_mpv.main.socket.socket')
    mock_os = mocker.patch('open_in_mpv.main.os')
    mock_os.environ.copy.return_value = {'PATH': '/usr/bin'}
    mock_os.fork.side_effect = [0, 0]
    mocker.patch('open_in_mpv.main.sp.run')
    result = runner.invoke(main, ['chrome://aaa', '-'],
                           input=b'\x1e\x00\x00\x00{"url": "https://example.com"}')
    assert result.exit_code == 0


def test_main_socket_failure(runner: CliRunner, mocker: MockerFixture) -> None:
    mpv_socket_path = mocker.patch('open_in_mpv.main.MPV_SOCKET')
    mpv_socket_path.exists.return_value = False
    mock_socket = mocker.patch('open_in_mpv.main.socket.socket')
    mock_os = mocker.patch('open_in_mpv.main.os')
    mock_os.environ.copy.return_value = {'PATH': '/usr/bin'}
    mock_os.fork.side_effect = [1, 0, 0, 0]
    mock_socket.return_value.connect.side_effect = OSError
    mocker.patch('open_in_mpv.main.sp.run')
    result = runner.invoke(main, ['chrome://aaa', '-'],
                           input=b'\x1e\x00\x00\x00{"url": "https://example.com"}')
    assert result.exit_code == 0


def test_main_single_instance(runner: CliRunner, mocker: MockerFixture) -> None:
    mock_json_dumps = mocker.patch('open_in_mpv.main.json.dumps')
    mock_json_dumps.return_value = '{"command": ["loadfile", "https://example.com"]}'
    mock_socket = mocker.patch('open_in_mpv.main.socket.socket')
    mpv_socket_path = mocker.patch('open_in_mpv.main.MPV_SOCKET')
    mpv_socket_path.exists.return_value = True
    mock_os = mocker.patch('open_in_mpv.main.os')
    mock_os.environ.copy.return_value = {'PATH': '/usr/bin'}
    mock_os.fork.side_effect = [0, 0, 1, 1]
    mocker.patch('open_in_mpv.main.sp.run')
    result = runner.invoke(main, ['chrome://aaa', '-'],
                           input=b'\x1e\x00\x00\x00{"url": "https://example.com"}')
    assert result.exit_code == 0
    assert mock_socket.return_value.connect.call_count == 1
    assert mock_socket.return_value.send.call_count == 1
    assert mock_json_dumps.call_count == 2


def test_main_single_instance_connection_refused(runner: CliRunner, mocker: MockerFixture) -> None:
    mock_socket = mocker.patch('open_in_mpv.main.socket.socket')
    mpv_socket_path = mocker.patch('open_in_mpv.main.MPV_SOCKET')
    mpv_socket_path.exists.return_value = True
    mock_socket.return_value.send.side_effect = OSError
    mock_os = mocker.patch('open_in_mpv.main.os')
    mock_os.environ.copy.return_value = {'PATH': '/usr/bin'}
    mock_os.fork.side_effect = [0, 0, 0, 0]
    run = mocker.patch('open_in_mpv.main.sp.run')
    result = runner.invoke(main, ['chrome://aaa', '-'],
                           input=b'\x1e\x00\x00\x00{"url": "https://example.com"}')
    assert result.exit_code == 0
    assert run.call_count == 1
    assert mock_socket.return_value.connect.call_count == 1
    assert mock_socket.return_value.send.call_count == 1
    assert mock_os._exit.call_count == 2  # noqa: SLF001


def test_main_single_instance_macports(runner: CliRunner, mocker: MockerFixture) -> None:
    mock_path = mocker.patch('open_in_mpv.main.Path')
    mock_path.return_value.is_dir.return_value = True
    mock_socket = mocker.patch('open_in_mpv.main.socket.socket')
    mpv_socket_path = mocker.patch('open_in_mpv.main.MPV_SOCKET')
    mpv_socket_path.exists.return_value = True
    mock_os = mocker.patch('open_in_mpv.main.os')
    mock_os.environ.copy.return_value = {'PATH': '/usr/bin'}
    mock_os.fork.side_effect = [0, 0, 1, 1]
    mocker.patch('open_in_mpv.main.sp.run')
    result = runner.invoke(main, ['chrome://aaa', '-'],
                           input=b'\x1e\x00\x00\x00{"url": "https://example.com"}')
    assert result.exit_code == 0
    assert mock_socket.return_value.connect.call_count == 1
    assert mock_socket.return_value.send.call_count == 1
    try:
        struct.unpack('@i', result.stdout_bytes[:4])
    except struct.error:
        pytest.fail('Failed to unpack size from stdout')
    data = json.loads(result.stdout_bytes[4:].decode())
    assert isinstance(data, dict)
    assert 'macports' in data
    assert data['macports'] is True


def test_main_spawn_exit_second_parent(mocker: MockerFixture) -> None:
    mock_os = mocker.patch('open_in_mpv.main.os')
    mock_os.fork.side_effect = [0, 1]
    mock_callable = mocker.Mock()
    with pytest.raises(SystemExit):
        spawn(mock_callable)
    assert mock_os._exit.call_count == 0  # noqa: SLF001


def test_main_debug_mode(runner: CliRunner, mocker: MockerFixture) -> None:
    """Test main with debug=True to cover debug paths."""
    mpv_socket_path = mocker.patch('open_in_mpv.main.MPV_SOCKET')
    mpv_socket_path.exists.return_value = False
    mock_os = mocker.patch('open_in_mpv.main.os')
    mock_os.fork.side_effect = [1, 1]
    mock_os.environ.copy.return_value = {'PATH': '/usr/bin'}
    mocker.patch('open_in_mpv.main.sp.run')
    result = runner.invoke(main, ['chrome://aaa', '-', '--debug'],
                           input=b'\x1e\x00\x00\x00{"url": "https://example.com"}')
    assert result.exit_code == 0


def test_mpv_and_cleanup_callback_windows(mocker: MockerFixture) -> None:
    """Test mpv_and_cleanup callback on Windows to cover Windows-specific paths."""
    from open_in_mpv.main import mpv_and_cleanup
    mocker.patch('open_in_mpv.main.IS_WIN', new=True)
    mock_path_open = mocker.patch('open_in_mpv.main.Path')
    mock_path_open.return_value.open.return_value.__enter__.return_value = mocker.Mock()
    mock_path_open.return_value.open.return_value.__exit__.return_value = None
    mock_get_mpv_path = mocker.patch('open_in_mpv.main.get_mpv_path')
    mock_get_mpv_path.return_value = 'C:\\test\\mpv.exe'
    mock_sp_run = mocker.patch('open_in_mpv.main.sp.run')
    mock_remove_socket = mocker.patch('open_in_mpv.main.remove_socket')
    mock_remove_socket.return_value = True

    callback = mpv_and_cleanup('https://example.com', {'PATH': '/usr/bin'}, debug=False)
    callback()

    # Verify sp.run was called
    assert mock_sp_run.call_count == 1
    args = mock_sp_run.call_args
    cmd_parts = args[0][0]
    # On Windows, should not have --gpu-api=opengl
    assert '--gpu-api=opengl' not in cmd_parts
    assert cmd_parts[0] == 'C:\\test\\mpv.exe'


def test_mpv_and_cleanup_callback_debug(mocker: MockerFixture) -> None:
    """Test mpv_and_cleanup callback with debug=True to cover debug paths."""
    from open_in_mpv.main import mpv_and_cleanup
    mock_path_open = mocker.patch('open_in_mpv.main.Path')
    mock_path_open.return_value.open.return_value.__enter__.return_value = mocker.Mock()
    mock_path_open.return_value.open.return_value.__exit__.return_value = None
    mock_get_mpv_path = mocker.patch('open_in_mpv.main.get_mpv_path')
    mock_get_mpv_path.return_value = 'mpv'
    mock_sp_run = mocker.patch('open_in_mpv.main.sp.run')
    mock_remove_socket = mocker.patch('open_in_mpv.main.remove_socket')
    mock_remove_socket.return_value = True

    callback = mpv_and_cleanup('https://example.com', {'PATH': '/usr/bin'}, debug=True)
    callback()

    # Verify sp.run was called with debug flags
    assert mock_sp_run.call_count == 1
    args = mock_sp_run.call_args
    cmd_parts = args[0][0]
    # In debug mode, should have -v and --log-file
    assert '-v' in cmd_parts
    assert any('--log-file=' in arg for arg in cmd_parts)

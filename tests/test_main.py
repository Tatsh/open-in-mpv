from __future__ import annotations

from typing import TYPE_CHECKING
import json
import re
import struct

from open_in_mpv.main import main, spawn
import pytest

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture


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

from __future__ import annotations

from typing import TYPE_CHECKING

from open_in_mpv.test_open import main

if TYPE_CHECKING:
    from click.testing import CliRunner, Result
    from pytest_mock import MockerFixture


def test_test_open_no_executable(mocker: MockerFixture, runner: CliRunner) -> None:
    mocker.patch('open_in_mpv.test_open.which', return_value=None)
    result = runner.invoke(main, ['http://example.com'])
    assert result.exit_code != 0


def test_test_open_debug_enabled(mocker: MockerFixture, runner: CliRunner) -> None:
    mock_which = mocker.patch('open_in_mpv.test_open.which', return_value='/usr/bin/open-in-mpv')
    mock_popen = mocker.patch('open_in_mpv.test_open.sp.Popen')
    mock_proc = mocker.MagicMock()
    mock_proc.__enter__.return_value.returncode = 0
    mock_popen.side_effect = [mock_proc, mock_proc]
    result = runner.invoke(main, ['http://example.com', '--debug'])
    assert result.exit_code == 0
    assert mock_which.called
    assert mock_popen.call_count == 2
    init_call = mock_popen.call_args_list[0]
    url_call = mock_popen.call_args_list[1]
    # Check the first call (init)
    init_args = init_call[0][0]
    assert init_args == ('/usr/bin/open-in-mpv', 'chrome://nothing', '-d')
    # Check the second call (url)
    url_args = url_call[0][0]
    assert url_args == ('/usr/bin/open-in-mpv', 'chrome://nothing', '-d')


def test_test_open_process_failure(mocker: MockerFixture, runner: CliRunner) -> None:
    mocker.patch('open_in_mpv.test_open.which', return_value='/usr/bin/open-in-mpv')
    mock_popen = mocker.patch('open_in_mpv.test_open.sp.Popen')
    mock_proc = mocker.MagicMock()
    mock_proc.communicate.return_value = (b'', b'')
    mock_proc.wait.return_value = 1
    mock_proc.returncode = 1
    mock_popen.return_value = mock_proc

    result: Result = runner.invoke(main, ['http://example.com'])

    assert result.exit_code != 0
    assert mock_popen.call_count == 2

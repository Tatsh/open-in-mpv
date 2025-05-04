from __future__ import annotations

from typing import TYPE_CHECKING

from open_in_mpv.uninstall import main
import open_in_mpv.uninstall

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture


def test_uninstall_linux_system_dirs_permission_error(mocker: MockerFixture,
                                                      runner: CliRunner) -> None:
    mocker.patch.object(open_in_mpv.uninstall, 'IS_LINUX', True)  # noqa: FBT003
    mocker.patch.object(open_in_mpv.uninstall, 'IS_MAC', False)  # noqa: FBT003
    mock_remove_from_all = mocker.patch('open_in_mpv.uninstall.remove_from_all')
    mocker.patch('open_in_mpv.uninstall.SYSTEM_HOSTS_DIRS', ['/etc/fake'])
    mocker.patch('open_in_mpv.uninstall.USER_HOSTS_DIRS', ['/home/user/fake'])
    mock_remove_from_all.side_effect = [PermissionError, None]

    result = runner.invoke(main, ['--debug'])

    assert 'To delete files installed in /etc, run this as root.' in result.output
    mock_remove_from_all.assert_any_call(['/etc/fake'])
    mock_remove_from_all.assert_any_call(['/home/user/fake'])


def test_uninstall_mac(mocker: MockerFixture, runner: CliRunner) -> None:
    mocker.patch.object(open_in_mpv.uninstall, 'IS_LINUX', False)  # noqa: FBT003
    mocker.patch.object(open_in_mpv.uninstall, 'IS_MAC', True)  # noqa: FBT003
    mocker.patch('open_in_mpv.uninstall.MAC_HOSTS_DIRS', ['/Library/fake'])
    mocker.patch('open_in_mpv.uninstall.Path')
    result = runner.invoke(main, ['--debug'])
    assert result.exit_code == 0


def test_uninstall_no_os(mocker: MockerFixture, runner: CliRunner) -> None:
    mocker.patch.object(open_in_mpv.uninstall, 'IS_LINUX', False)  # noqa: FBT003
    mocker.patch.object(open_in_mpv.uninstall, 'IS_MAC', False)  # noqa: FBT003
    mock_remove_from_all = mocker.patch('open_in_mpv.uninstall.remove_from_all')

    result = runner.invoke(main, ['--debug'])

    assert result.exit_code == 0
    mock_remove_from_all.assert_not_called()

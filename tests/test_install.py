from __future__ import annotations

from typing import TYPE_CHECKING

from open_in_mpv.install import main
import open_in_mpv.install
import pytest

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture


@pytest.fixture
def mock_dependencies(mocker: MockerFixture) -> None:
    mocker.patch('open_in_mpv.install.json.dump')
    mocker.patch('open_in_mpv.install.which', return_value='/usr/bin/open-in-mpv')
    mock_path = mocker.patch('open_in_mpv.install.Path')
    mock_path.return_value.exists.return_value = True
    mocker.patch('os.geteuid', return_value=0)


def test_install_no_action(runner: CliRunner, mock_dependencies: None) -> None:
    result = runner.invoke(main, [])
    assert result.exit_code != 0
    assert 'Need an action.' in result.output


def test_install_open_in_mpv_not_found(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch('open_in_mpv.install.which', return_value=None)
    result = runner.invoke(main, ['--system'])
    assert result.exit_code != 0
    assert 'open-in-mpv not found in PATH.' in result.output


def test_install_system_non_root_linux(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch('open_in_mpv.install.IS_LINUX', True)  # noqa: FBT003
    mocker.patch.object(open_in_mpv.install, 'IS_MAC', False)  # noqa: FBT003
    mocker.patch('os.geteuid', return_value=1000)
    result = runner.invoke(main, ['--system'])
    assert result.exit_code != 0
    assert 'Run this as root.' in result.output


def test_install_system_linux(runner: CliRunner, mocker: MockerFixture,
                              mock_dependencies: None) -> None:
    mocker.patch.object(open_in_mpv.install, 'IS_LINUX', True)  # noqa: FBT003
    mocker.patch.object(open_in_mpv.install, 'IS_MAC', False)  # noqa: FBT003
    result = runner.invoke(main, ['--system'])
    assert result.exit_code == 0


def test_install_user_linux(runner: CliRunner, mocker: MockerFixture,
                            mock_dependencies: None) -> None:
    mocker.patch.object(open_in_mpv.install, 'IS_LINUX', True)  # noqa: FBT003
    mocker.patch.object(open_in_mpv.install, 'IS_MAC', False)  # noqa: FBT003
    result = runner.invoke(main, ['--user'])
    assert result.exit_code == 0


def test_install_mac_system(runner: CliRunner, mocker: MockerFixture,
                            mock_dependencies: None) -> None:
    mocker.patch.object(open_in_mpv.install, 'IS_LINUX', False)  # noqa: FBT003
    mocker.patch.object(open_in_mpv.install, 'IS_MAC', True)  # noqa: FBT003
    result = runner.invoke(main, ['--system'])
    assert result.exit_code != 0


def test_install_mac_user(runner: CliRunner, mocker: MockerFixture,
                          mock_dependencies: None) -> None:
    mocker.patch.object(open_in_mpv.install, 'IS_LINUX', False)  # noqa: FBT003
    mocker.patch.object(open_in_mpv.install, 'IS_MAC', True)  # noqa: FBT003
    result = runner.invoke(main, ['--user'])
    assert result.exit_code == 0


def test_install_force_user_linux(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch.object(open_in_mpv.install, 'IS_LINUX', True)  # noqa: FBT003
    mocker.patch.object(open_in_mpv.install, 'IS_MAC', False)  # noqa: FBT003
    mocker.patch('open_in_mpv.install.json.dump')
    mocker.patch('open_in_mpv.install.which', return_value='/usr/bin/open-in-mpv')
    mock_path = mocker.patch('open_in_mpv.install.Path')
    mock_path.return_value.exists.return_value = False
    result = runner.invoke(main, ['--user', '--force'])
    assert result.exit_code == 0


def test_install_user_linux_2(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch.object(open_in_mpv.install, 'IS_LINUX', True)  # noqa: FBT003
    mocker.patch.object(open_in_mpv.install, 'IS_MAC', False)  # noqa: FBT003
    mocker.patch('open_in_mpv.install.json.dump')
    mocker.patch('open_in_mpv.install.which', return_value='/usr/bin/open-in-mpv')
    mock_path = mocker.patch('open_in_mpv.install.Path')
    mocker.patch('open_in_mpv.install.USER_HOSTS_DIRS', ['/home/user/fake', 'home/user/fake2'])
    mock_path.return_value.exists.side_effect = [False, True]
    result = runner.invoke(main, ['--user'])
    assert result.exit_code == 0

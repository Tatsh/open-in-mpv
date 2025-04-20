from __future__ import annotations

from typing import TYPE_CHECKING

from open_in_mpv.main import main

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture


def test_main(runner: CliRunner, mocker: MockerFixture) -> None:
    result = runner.invoke(main)
    assert result.exit_code == 0

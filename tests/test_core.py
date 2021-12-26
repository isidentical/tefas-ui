import importlib
from pathlib import Path

import pytest
from freezegun import freeze_time

import tefas_ui

FILES = Path(__file__).parent / "data"
INPUTS = FILES / "inputs"
OUTPUTS = FILES / "outputs"


@pytest.fixture
def command(capsys):
    def runner(*args):
        module = importlib.reload(tefas_ui)
        module.main(argv=[str(arg) for arg in args])
        return capsys.readouterr().out

    return runner


@freeze_time("2021-12-22")
@pytest.mark.parametrize(
    "format, currency, input_file_name, output_file_name",
    [
        ("teb", "try", "teb.txt", "teb_try.txt"),
        ("teb", "usd", "teb.txt", "teb_usd.txt"),
    ],
)
def test_basic_operations(
    command, format, currency, input_file_name, output_file_name
):
    input_file = INPUTS / input_file_name
    output_file = OUTPUTS / output_file_name

    result = command("--currency", currency, input_file, format)
    assert result == output_file.read_text()


@freeze_time("2021-12-25")
@pytest.mark.parametrize(
    "format, currency, input_file_name, output_file_name",
    [("teb", "try", "teb.txt", "teb_try_weekend.txt")],
)
def test_basic_operations_weekend(
    command, format, currency, input_file_name, output_file_name
):
    input_file = INPUTS / input_file_name
    output_file = OUTPUTS / output_file_name

    result = command("--currency", currency, input_file, format)
    assert result == output_file.read_text()

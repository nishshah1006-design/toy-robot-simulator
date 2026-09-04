import pytest

from robot_simulator.table import Table


def test_default_table_is_5x5():
    table = Table()
    assert table.width == 5
    assert table.height == 5


@pytest.mark.parametrize("x, y", [(0, 0), (4, 4), (0, 4), (4, 0), (2, 2)])
def test_on_table_positions(x, y):
    assert Table().is_on_table(x, y) is True


@pytest.mark.parametrize(
    "x, y",
    [(-1, 0), (0, -1), (5, 0), (0, 5), (5, 5), (-1, -1), (100, 100)],
)
def test_off_table_positions(x, y):
    assert Table().is_on_table(x, y) is False


def test_custom_dimensions():
    table = Table(width=3, height=2)
    assert table.is_on_table(2, 1) is True
    assert table.is_on_table(3, 1) is False
    assert table.is_on_table(2, 2) is False


@pytest.mark.parametrize("width, height", [(0, 5), (5, 0), (-1, 5), (5, -3)])
def test_invalid_dimensions_raise(width, height):
    with pytest.raises(ValueError):
        Table(width=width, height=height)

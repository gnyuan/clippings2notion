from pathlib import Path

from clippings2notion.reading import read_from_file


def test_read_from_file():
    test_clippings_file_path = (
        Path(__file__).parent.absolute() / "test_data/My Clippings.txt"
    )
    actual = read_from_file(test_clippings_file_path)
    assert 1==1

test_read_from_file()
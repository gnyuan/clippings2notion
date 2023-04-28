from pathlib import Path

from clippings2notion.parsing import parse_to_books_dict
from clippings2notion.reading import read_from_file


def test_parse_to_books_dict():
    test_clippings_file_path = (
        Path(__file__).parent.absolute() / "test_data/My Clippings.txt"
    )
    res = parse_to_books_dict(read_from_file(test_clippings_file_path))
    print(res)
    assert 1==1

test_parse_to_books_dict()

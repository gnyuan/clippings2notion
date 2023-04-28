import os
from typing import Dict

def read_from_file(clippings_file_path:str) -> str:
    try:
        with open(clippings_file_path, "r", encoding="utf-8-sig") as raw_clippings_file:
            raw_clippings_text = raw_clippings_file.read()
        raw_clippings_text = raw_clippings_text.replace(u"\ufeff", "").strip()
    except Exception as e:
        print(e)
        return ''
    return raw_clippings_text


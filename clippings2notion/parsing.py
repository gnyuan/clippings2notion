import os
from typing import Dict, List, Tuple
import re
import datetime as dt
from dateparser import parse

BOOKS_WO_AUTHORS = []

ACADEMIC_TITLES = [
    "A.A.",
    "A.S.",
    "A.A.A.",
    "A.A.S.",
    "A.B.",
    "A.D.N.",
    "A.M.",
    "A.M.T.",
    "C.E.",
    "Ch.E.",
    "D.A.",
    "D.A.S.",
    "D.B.A.",
    "D.C.",
    "D.D.",
    "D.Ed.",
    "D.L.S.",
    "D.M.D.",
    "D.M.S.",
    "D.P.A.",
    "D.P.H.",
    "D.R.E.",
    "D.S.W.",
    "D.Sc.",
    "D.V.M.",
    "Ed.D.",
    "Ed.S.",
    "E.E.",
    "E.M.",
    "E.Met.",
    "I.E.",
    "J.D.",
    "J.S.D.",
    "L.H.D.",
    "Litt.B.",
    "Litt.M.",
    "LL.B.",
    "LL.D.",
    "LL.M.",
    "M.A.",
    "M.Aero.E.",
    "M.B.A.",
    "M.C.S.",
    "M.D.",
    "M.Div.",
    "M.E.",
    "M.Ed.",
    "M.Eng.",
    "M.F.A.",
    "M.H.A.",
    "M.L.S.",
    "M.Mus.",
    "M.N.",
    "M.P.A.",
    "M.S.",
    "M.S.Ed.",
    "M.S.W.",
    "M.Th.",
    "Nuc.E.",
    "O.D.",
    "Pharm.D.",
    "Ph.B.",
    "Ph.D.",
    "S.B.",
    "Sc.D.",
    "S.J.D.",
    "S.Sc.D.",
    "Th.B.",
    "Th.D.",
    "Th.M.",
]

DELIMITERS = ["; ", " & ", " and "]


def parse_to_books_dict(raw_clippings_text: str) -> Dict:
    try:
        raw_clippings_list = raw_clippings_text.split("==========")
        print(f"Found {len(raw_clippings_list)} notes and highlights.\n")

        all_books = {}
        passed_clippings_count = 0

        for each_raw_clipping in raw_clippings_list:
            raw_clipping_list = each_raw_clipping.strip().split("\n")

            if _is_valid_clipping(raw_clipping_list):
                author, title = _parse_author_and_title(raw_clipping_list)
                page, location, date, is_note = _parse_page_location_date_and_note(
                    raw_clipping_list
                )
                highlight = raw_clipping_list[3]

                all_books = _add_parsed_items_to_all_books_dict(
                    all_books, title, author, highlight, page, location, date, is_note
                )
            else:
                passed_clippings_count += 1

            print(
                f"× Passed {passed_clippings_count} bookmarks or unsupported clippings.\n")
    except UnicodeEncodeError as e:
        print(e)
    return all_books


def _is_valid_clipping(raw_clipping_list: List) -> bool:
    return len(raw_clipping_list) >= 3


def _parse_author_and_title(raw_clipping_list: List) -> Tuple[str, str]:
    author, title = _parse_raw_author_and_title(raw_clipping_list)
    author, title = _deal_with_exceptions_in_author_name(author, title)
    title = _deal_with_exceptions_in_title(title)
    return author, title


def _parse_page_location_date_and_note(
    raw_clipping_list: List,
) -> Tuple[str, str, str, bool]:
    second_line = raw_clipping_list[1]
    second_line_as_list = second_line.strip().split(" | ")
    page = location = date = ""
    is_note = False

    for element in second_line_as_list:
        element = element.lower()
        if "note" in element or "笔记" in element:
            is_note = True
        if "page" in element:
            page = element[element.find("page"):].replace("page", "").strip()
        if "location" in element:
            location = (
                element[element.find("location"):].replace(
                    "location", "").strip()
            )
        if "位置" in element:
            location = (
                element[element.find("location"):].replace(
                    "location", "").strip()
            )
            tmp = re.findall(r'[0-9]+-[0-9]+', element)
            if len(tmp) > 0:
                location = tmp[0]
            else:
                location = ''
        if "added on" in element:
            date = parse(
                element[element.find("added on"):].replace(
                    "added on", "").strip()
            )
            date = date.strftime("%Y-%m-%d %I:%M:%S")
        if "添加于" in element:
            datestr = element[element.find("添加于"):].replace("添加于", "").strip()
            datestr = datestr.split('星期')[0] + ' ' + datestr.split('午')[-1]
            date = dt.datetime.strptime(datestr, '%Y年%m月%d日 %I:%M:%S')
            date = date.strftime("%Y-%m-%d %I:%M:%S")

    return page, location, date, is_note


def _add_parsed_items_to_all_books_dict(
    all_books: Dict,
    title: str,
    author: str,
    highlight: str,
    page: str,
    location: str,
    date: str,
    is_note: bool,
) -> Dict:
    if title not in all_books:
        all_books[title] = {"author": author, "highlights": []}
    all_books[title]["highlights"].append(
        (highlight, page, location, date, is_note))
    return all_books


def _parse_raw_author_and_title(raw_clipping_list: List) -> Tuple[str, str]:
    author = ""
    title = raw_clipping_list[0]

    if re.findall(r"\(.*?\)", raw_clipping_list[0]):
        author = (re.findall(r"\(.*?\)", raw_clipping_list[0]))[-1]
        author = author.removeprefix("(").removesuffix(")")
    else:
        if title not in BOOKS_WO_AUTHORS:
            BOOKS_WO_AUTHORS.append(title)
            print(
                f"{title} - No author found. You can manually add the author in the Notion database."
            )

    title = raw_clipping_list[0].replace(author, "").strip().replace(
        " ()", "").replace("(Z-Library)", "").strip()

    return author, title


def _deal_with_exceptions_in_author_name(author: str, title: str) -> Tuple[str, str]:
    if "(" in author:
        author = author + ")"
        title = title.removesuffix(")")

    if ", " in author and all(x not in author for x in DELIMITERS):
        if (author.split(", "))[1] not in ACADEMIC_TITLES:
            author = " ".join(reversed(author.split(", ")))

    if "; " in author:
        authorList = author.split("; ")
        author = ""
        for ele in authorList:
            author += " ".join(reversed(ele.split(", "))) + ", "
        author = author.removesuffix(", ")
    return author, title


def _deal_with_exceptions_in_title(title: str) -> str:
    if ", The" in title:
        title = "The " + title.replace(", The", "")
    return title

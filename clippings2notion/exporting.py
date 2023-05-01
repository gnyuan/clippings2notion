from datetime import datetime
from typing import Dict, List, Tuple

import notional
from notional.blocks import Paragraph, TextObject
from notional.query import TextCondition
from notional.types import Date, ExternalFile, Number, RichText, Title


NO_COVER_IMG = "https://via.placeholder.com/150x200?text=No%20Cover"


def export_to_notion(
    all_books: Dict,
    enable_highlight_date: bool,
    notion_api_auth_token: str,
    notion_database_id: str,
) -> None:
    print("Initiating transfer...\n")

    for title in all_books:
        each_book = all_books[title]
        author = each_book["author"]
        clippings = each_book["highlights"]
        clippings_count = len(clippings)
        (
            formatted_clippings,
            last_date,
        ) = _prepare_aggregated_text_for_one_book(clippings, enable_highlight_date)
        message = _add_book_to_notion(
            title,
            author,
            clippings_count,
            formatted_clippings,
            last_date,
            notion_api_auth_token,
            notion_database_id,
        )
        if message != "None to add":
            print("✓", message)


def _prepare_aggregated_text_for_one_book(
    clippings: List, enable_highlight_date: bool
) -> Tuple[str, str]:
    # TODO: Special case for books with len(clippings) >= 100 characters. Character limit in a Paragraph block in Notion is 100
    formatted_clippings = []
    for each_clipping in clippings:
        aggregated_text = ""
        text = each_clipping[0]
        page = each_clipping[1]
        location = each_clipping[2]
        date = each_clipping[3]
        is_note = each_clipping[4]
        if is_note == True:
            aggregated_text += "> " + "NOTE: \n"

        aggregated_text += text + "\n* "
        if page != "":
            aggregated_text += "Page: " + page + ", "
        if location != "":
            aggregated_text += "Location: " + location
        if enable_highlight_date and (date != ""):
            aggregated_text += ", Date Added: " + date

        aggregated_text = aggregated_text.strip() + "\n\n"
        formatted_clippings.append(aggregated_text)
        last_date = date
    return formatted_clippings, last_date


def _add_book_to_notion(
    title: str,
    author: str,
    clippings_count: int,
    formatted_clippings: list,
    last_date: str,
    notion_api_auth_token: str,
    notion_database_id: str,
):
    notion = notional.connect(auth=notion_api_auth_token)
    last_date = datetime.strptime(last_date, "%Y-%m-%d %I:%M:%S")

    # Condition variables
    title_exists = False
    current_clippings_count = 0

    query = (
        notion.databases.query(notion_database_id)
        .filter(property="Title", rich_text=TextCondition(equals=title))
        .limit(1)
    )
    data = query.first()

    if data:
        title_exists = True
        block_id = data.id
        block = notion.pages.retrieve(block_id)
        if block["Highlights"] == None:
            block["Highlights"] = Number[0]
        elif block["Highlights"] == clippings_count:  # if no change in clippings
            title_and_author = str(block["Title"]) + " (" + str(block["Author"]) + ")"
            print(title_and_author)
            print("-" * len(title_and_author))
            return "None to add.\n"

    title_and_author = title + " (" + str(author) + ")"
    print(title_and_author)
    print("-" * len(title_and_author))

    # Add a new book to the database
    if not title_exists:
        new_page = notion.pages.create(
            parent=notion.databases.retrieve(notion_database_id),
            properties={
                "Title": Title[title],
                "Author": RichText[author],
                "Highlights": Number[clippings_count],
                "Last Highlighted": Date[last_date],
                "Last Synced": Date[datetime.now()],
            },
            children=[],
        )
        # page_content = _update_book_with_clippings(formatted_clippings)
        page_content = Paragraph["".join(formatted_clippings)]
        notion.blocks.children.append(new_page, page_content)
        block_id = new_page.id

        cover = ExternalFile[NO_COVER_IMG]
        print("✓ Added book cover.")
        notion.pages.set(new_page, cover=cover)
    else:
        # update a book that already exists in the database
        page = notion.pages.retrieve(block_id)
        # page_content = _update_book_with_clippings(formatted_clippings)
        page_content = Paragraph["".join(formatted_clippings)]
        notion.blocks.children.append(page, page_content)
        # TODO: Delete existing page children (or figure out how to find changes to be made by comparing it with local json file.)
        current_clippings_count = int(float(str(page["Highlights"])))
        page["Highlights"] = Number[clippings_count]
        page["Last Highlighted"] = Date[last_date.isoformat()]
        page["Last Synced"] = Date[datetime.now().isoformat()]

    # Logging the changes made
    diff_count = (
        clippings_count - current_clippings_count
        if clippings_count > current_clippings_count
        else clippings_count
    )
    message = str(diff_count) + " notes/highlights added successfully.\n"

    return message

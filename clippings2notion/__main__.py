import json
import os
import click
import notional

from pathlib import Path

from clippings2notion.reading import read_from_file
from clippings2notion.parsing import parse_to_books_dict
from clippings2notion.exporting import export_to_notion
from clippings2notion.update_via_isbn import update_notion_db_info
from clippings2notion.utils import load_dotenv



# @click.command()
# @click.argument("notion_api_auth_token")
# @click.argument("notion_database_id")
# @click.argument("clippings_file")
# @click.option(
#     "--enable_highlight_date",
#     default=True,
#     help='Set to False if you don\'t want to see the "Date Added" information in Notion.',
# )
def main(
    notion_api_auth_token,
    notion_database_id,
    clippings_file_path,
    enable_highlight_date,
):
    load_dotenv()
    if os.environ.get('NOTION_API_AUTH_TOKEN'):
        notion_api_auth_token = os.environ.get('NOTION_API_AUTH_TOKEN')
    if os.environ.get('NOTION_DATABASE_ID'):
        notion_database_id = os.environ.get('NOTION_DATABASE_ID')

    notion = notional.connect(auth=notion_api_auth_token)
    db = notion.databases.retrieve(notion_database_id)

    if not db:
        print(
            "Notion page not found! Please check whether the Notion database ID is assigned properly."
        )
        return

    print("Notion page is found. Analyzing clippings file...")

    # Open the clippings text file and load it into all_clippings
    all_clippings = read_from_file(clippings_file_path)

    # Parse all_clippings file and format the content to be sent tp the Notion DB into all_books
    all_books = parse_to_books_dict(all_clippings)

    # Export all the contents in all_books into the Notion DB.
    export_to_notion(
        all_books,
        enable_highlight_date,
        notion_api_auth_token,
        notion_database_id,
    )

    with open("my_kindle_clippings.json", "w") as out_file:
        json.dump(all_books, out_file, indent=4)

    print("Transfer complete... Exiting script...")


if __name__ == "__main__":
    test_clippings_file_path = (
        Path(__file__).parent.absolute() / "../tests/test_data/My Clippings.txt"
    )
    main('', '', test_clippings_file_path, True)
    # update_notion_db_info('','')

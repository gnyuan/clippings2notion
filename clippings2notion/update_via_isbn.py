
import json
from typing import Dict
import requests
import os

from clippings2notion.utils import load_dotenv
from datetime import datetime
from typing import Dict, List, Tuple

import notional
from notional.blocks import Paragraph, TextObject
from notional.query import TextCondition
from notional.types import Date, ExternalFile, Number, RichText, Title


def get_book_info_via_isbn(isbn: str) -> Dict:
    '''
    https://www.googleapis.com/books/v1/volumes?q=isbn:9787111565178
    return 
    {'isbn': '9787111565178'
    , 'bookName': '波动率交易：期权量化交易员指南'
    , 'author': '辛克莱'
    , 'pressDate': '2017-01-01'
    , 'cover': 'https://img2.doubanio.com/view/subject/s/public/s29463821.jpg'
    , 'class': '经济'}
    '''
    URL = 'http://47.99.80.202:6066/openApi/getInfoByIsbn?isbn={isbn}&appKey=ae1718d4587744b0b79f940fbef69e77'
    res = requests.get(URL.format(isbn=isbn))
    info = json.loads(res.content)
    ret = {}
    if info.get('code') != 0:
        return ret
    ret['isbn'] = info['data']['isbn']
    ret['bookName'] = info['data']['bookName']
    ret['author'] = info['data']['author']
    ret['pressDate'] = info['data']['pressDate']
    ret['cover'] = json.loads(info['data']['pictures'])[0]
    ret['class'] = info['data']['clcName']
    return ret


def update_notion_db_info():
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

    notion = notional.connect(auth=notion_api_auth_token)

    query = (
        notion.databases.query(notion_database_id)
    )
    for block in query.execute():
        block_id = block.id
        page = notion.pages.retrieve(block_id)
        isbn = block.properties['isbn']
        if isbn:
            info = get_book_info_via_isbn(str(isbn))
            print(info)
            notion.pages.set(page, cover=info['cover'])
            print("✓ Updated book cover.")


# update_notion_db_info()

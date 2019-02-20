#!/usr/bin/python
# -*-coding:utf-8 -*-
import json
from json import JSONDecodeError
from urllib.parse import urlencode

import requests
from requests.exceptions import RequestException


def get_page_index(offset, keyword):
    data = {
        'aid': 24,
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'en_qc': 1,
        'cur_tab': 1,
        'from': 'search_tab',
        'pd': 'synthesis'
    }
    url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)
    try:
        respose = requests.get(url)
        if respose.status_code == 200:
            return respose.text
        return None
    except RequestException:
        print('请求异常')


def parse_page_index(html):
    try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                yield item.get('article_url')
    except JSONDecodeError:
        pass


def main():
    html = get_page_index(20, '街拍')
    # print(html)
    for url in parse_page_index(html):
        print(url)


if __name__ == '__main__':
    main()

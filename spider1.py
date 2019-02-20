#!/usr/bin/python
# -*-coding:utf-8 -*-

import requests
from requests.exceptions import RequestException


def get_one_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def main():
    url = 'https://maoyan.com/board/4?offset=0'
    html = get_one_page(url)
    print(html)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*-coding:utf-8 -*-
import json
from hashlib import md5
from json import JSONDecodeError
from urllib.parse import urlencode

import re

import os
import pymongo
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


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
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引页异常')


def parse_page_index(html):
    try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                yield item.get('article_url')
    except JSONDecodeError:
        pass


def get_page_detail(url):
    if url is not None:
        try:
            res = re.match('^http.*?(\d+)/$', url)
            response = requests.get('https://www.toutiao.com/a' + res.group(1) + '/')
            if response.status_code == 200:
                return response.text
            return None
        except RequestException:
            print('请求详情页异常')


def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    images_pattern = re.compile('gallery: JSON.parse\(\"(.*?)\"\),', re.S)
    ress = re.search(images_pattern, html)

    if ress:
        str = ress.group(1)
        data = json.loads(str.replace("\\", ""))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images: download_image(image)
            return {
                'title': title,
                'images': images,
                'url': url
            }


def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('Successfully Saved to Mongo', result)
        return True
    return False


def download_image(url):
    print('Downloading', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content)
        return None
    except ConnectionError:
        return None


def save_image(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    print(file_path)
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def main():
    html = get_page_index(0, '街拍')
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html, url)
            if result:
                save_to_mongo(result)


if __name__ == '__main__':
    main()

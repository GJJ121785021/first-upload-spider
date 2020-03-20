# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.exceptions import DropItem
import re


class ScrapyZhonghongindustryresearchV251Pipeline(object):
    def __init__(self, mongo_uri, mongo_db, mongo_coll):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_coll = mongo_coll

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB'),
            mongo_coll=crawler.settings.get('MONGO_COLL'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        self.db[self.mongo_coll].insert(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()


class CleanPipeline(object):
    def process_item(self, item, spider):
        # 清洗单位 取出（上年=100）这类单位
        if not item['unit'] or item['unit'] == '%':
            unit = re.findall('\((.*?00.*?)\)', item['indic_name'])
            if not unit:
                unit = re.findall('（(.*?00.*?)）', item['indic_name'])
            if unit:
                item['unit'] = unit[0]
        return item


class TextPipeline(object):
    def process_item(self, item, spider):
        item_print = item['indic_name']
        item = item_print
        return item
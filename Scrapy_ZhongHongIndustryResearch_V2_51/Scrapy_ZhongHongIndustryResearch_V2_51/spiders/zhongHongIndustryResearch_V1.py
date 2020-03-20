# -*- coding: utf-8 -*-
import scrapy
from Scrapy_ZhongHongIndustryResearch_V2_51.items import ScrapyZhonghongindustryresearchV251Item
from scrapy.crawler import logger
import json
import requests


class ZhonghongindustryresearchV1Spider(scrapy.Spider):
    name = 'zhongHongIndustryResearch_V1'
    start_urls = ['http://zhcy.app.ckcest.cn/api/GetNavJson?id=10']
    url_get_id = 'http://zhcy.app.ckcest.cn/api/GetArchAnsyJson?id={}'
    url_get_data = 'http://zhcy.app.ckcest.cn/include/handler.ashx?ar=76&id={}&by=1990&ey=2019&new=1&nt=1&dv=2'

    # the api is similar to mysql_for_id.py
    url_mysql_api = 'http://127.0.0.1:5591/?table_name={}&name={}&pid={}&must_create=1'
    table_name = 'entertainment_catalogue'
    root_id = 18005

    def parse(self, response):
        datas = json.loads(response.text).get('subNavItem')
        for data in datas:
            eles = data.get('archInfoItem')
            for ele in eles:
                id = ele.get('aid')
                name = ele.get('aName')



                if '文教、工美、体育和娱乐用品制造业' == name:
                    new_id = requests.get(self.url_mysql_api.format(self.table_name, name, self.root_id)).json().get(
                        'parent_id')
                    yield scrapy.Request(url=self.url_get_id.format(id), meta={'parent_id': new_id}, callback=self.parse_page)

    def parse_page(self, response):
        # 取下一页所需的id
        # id_data = eval(response.text.replace('null', '"null"')).get('indexItem')[0].get('id')
        datas = json.loads(response.text).get('subArchItem')
        for data in datas:
            isParent = data.get('isParent')
            id = data.get('id')
            if isParent:
                name = data.get('name')
                new_id = requests.get(self.url_mysql_api.format(self.table_name, name, response.meta['parent_id'])).json().get(
                    'parent_id')
                yield scrapy.Request(url=self.url_get_id.format(id)+'&name='+name, meta={'parent_id': new_id},
                                     callback=self.parse_page)
            else:
                yield scrapy.Request(self.url_get_id.format(id), meta={'parent_id': response.meta['parent_id']},
                                     callback=self.parse_page_2)

    def parse_page_2(self, response):
        datas = json.loads(response.text).get('indexItem')
        for data in datas:
            id = data.get('id')
            yield scrapy.Request(self.url_get_data.format(id), meta={'parent_id': response.meta['parent_id']},
                                 callback=self.parse_response)

    def parse_response(self, response):
        # 解析数据
        # 删除空数据的网页
        if response.text == '<err>Empty</err>':
            logger.info('该页面数据为空')
            return None
        indic_name = response.xpath('//tr[2]/td[2]/text()').get()  # 名称
        logger.info(indic_name)
        new_id = requests.get(self.url_mysql_api.format(self.table_name, indic_name, response.meta['parent_id'])).json().get('parent_id')

        unit = response.xpath('//tr[2]/td[4]/text()').get()  # 单位
        region = response.xpath('//tr[2]/td[3]/text()').get()  # 全国、省份、市等地区
        # 把表格中的时间及数据以列表的形式取出来并解析
        datatimes = response.xpath('//tr[1]/th/text()').getall()[4:]
        values = response.xpath('//tr[2]/td/text()').getall()[4:]
        for datatime, value in zip(datatimes, values):
            create_time = datatime  # 数据产生时间
            if create_time.endswith('年'):
                create_time = create_time[:-1]

            item = ScrapyZhonghongindustryresearchV251Item()
            item['parent_id'] = str(new_id)
            item['root_id'] = '18'
            item['indic_name'] = indic_name
            item['frequency'] = 5
            item['unit'] = unit
            item['data_source'] = '中宏产业研究平台'
            item['region'] = region
            item['country'] = '0'
            item['sign'] = '03'
            item['status'] = 1
            item['cleaning_status'] = 0
            item['create_time'] = create_time
            item['data_year'] = int(datatime[:-1])
            item['data_day'] = 0
            item['data_month'] = 0
            item['data_value'] = float(value.replace(',', ''))  # 把数据中夹杂的逗号(,)删除
            yield item


import os

if __name__ == '__main__':
    os.system('scrapy crawl zhongHongIndustryResearch_V1')

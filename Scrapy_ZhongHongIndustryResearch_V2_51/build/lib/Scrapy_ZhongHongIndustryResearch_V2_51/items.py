# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyZhonghongindustryresearchV251Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 数据目录
    parent_id = scrapy.Field()

    # 根目录id
    root_id = scrapy.Field()

    # 名称
    indic_name = scrapy.Field()

    # 年：1992
    data_year = scrapy.Field()

    # 月：1 - 12
    data_month = scrapy.Field()

    # 日：1 - 31
    data_day = scrapy.Field()

    # 频率(0：季度， 1234： 季度 ，5678：年月周日  )
    frequency = scrapy.Field()

    # 单位
    unit = scrapy.Field()

    # 数据来源(网站名) 国家统计局
    data_source = scrapy.Field()

    # 全国、省份、市等地区
    region = scrapy.Field()

    # 国家#
    country = scrapy.Field()

    # 数据产生时间
    create_time = scrapy.Field()

    # 数值
    data_value = scrapy.Field()

    # 个人编号 01 - 20
    sign = scrapy.Field()

    # 0: 无效  1: 有效
    status = scrapy.Field()

    # 0: 未清洗 1 ： 清洗过
    cleaning_status = scrapy.Field()

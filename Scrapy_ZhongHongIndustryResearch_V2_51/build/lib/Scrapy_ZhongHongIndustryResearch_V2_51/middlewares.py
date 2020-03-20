# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests
from scrapy import Selector
from PIL import Image
import io
import tesserocr
import time
import base64


class ScrapyZhonghongindustryresearchV251DownloaderMiddleware(object):
    # cookies
    JSESSIONID = None
    # 获取会话表格url
    table_url = 'http://zhcy.app.ckcest.cn/MacroCy/index.html'

    def __init__(self, logger):
        self.logger = logger
        self.proxy = None
        self.limit = 0

    def login(self):
        # 创建会话
        session = requests.Session()
        # 访问登录界面
        login_url = 'https://sso.ckcest.cn/portal/signin?locale=zh_CN&device=pc&type=account&service=http%3A%2F%2Fwww.ckcest.cn%2Fcas'
        login_view = session.get(url=login_url)
        res = Selector(text=login_view.text)
        # 获取请求数据
        app_key = res.xpath('//input[@name="app_key"]/@value').get()

        # 获取验证码
        code = token = ''
        while len(code) != 4:
            self.logger.info('********* 识别验证码 *********')
            url_image_json = 'https://sso.ckcest.cn/api/auth_web/captcha?width=120&height=51&type=char&app_key={}&timestamp={}'

            response_imgjson = session.get(url_image_json.format(app_key, time.time() * 1000)).json()
            token = response_imgjson.get('data').get('token')
            img_str = response_imgjson.get('data').get('base64Image').split(',', 1)[-1]
            img_byte = base64.b64decode(img_str)
            img_file = io.BytesIO(img_byte)
            # 识别验证码
            img = Image.open(img_file)
            code = tesserocr.image_to_text(img).strip()
            # self.logger.info(f'********* {code}*********')

        # 访问登录API
        login_api = 'https://sso.ckcest.cn/api/auth_web/login_code_token'
        data = dict()
        data['account'] = '17109324122'
        data['password'] = 'JJ597379946'
        data['code'] = code
        data['app_key'] = app_key
        data['service'] = 'https://sso.ckcest.cn/portal/signin?locale=zh_CN&device=pc&type=account&service=http%3A%2F%2Fwww.ckcest.cn%2Fcas&_s=http%3A%2F%2Fwww.ckcest.cn%2Fcas'
        data['_eventId'] = 'submit'
        data['token'] = token
        login = session.post(url=login_api, data=data)
        res = Selector(text=login.text)
        result = res.xpath('//title[contains(text(), "登录-中国工程科技知识")]').get()
        if result:
            # 循环登录
            return False

        # 请求表格数据  获取JSESSIONID和ASP.NET_SessionId 字段
        session.get(url=self.table_url)
        self.JSESSIONID = session.cookies.get('JSESSIONID', domain='zhcy.app.ckcest.cn')
        return True

    def process_request(self, request, spider):
        if not self.JSESSIONID:
            while True:
                if self.login():
                    break
        cookies = {
            'JSESSIONID': self.JSESSIONID,
        }
        request.cookies = cookies

        # 加代理
        if (not self.proxy) or self.limit > 10:
            self.limit = 0
            self.proxy = requests.get('http://192.168.0.11:5010/get/').json().get('proxy')
        self.limit += 1
        request.meta['proxy'] = 'http://' + self.proxy

    def process_response(self, request, response, spider):
        if response.status == 302:  # 暂时重定向
            self.JSESSIONID = None
            request = request.replace(dont_filter=True)
            return request  # 重新请求
        if response.status != 200 or not response.text:
            self.proxy = None
        return response

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(crawler.spider.logger)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

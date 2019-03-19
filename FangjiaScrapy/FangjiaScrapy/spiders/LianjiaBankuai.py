# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request

from ..items import Zone


class LianjiabankuaiSpider(scrapy.Spider):
    name = 'LianjiaBankuai'
    allowed_domains = ['lianjia.com']
    root_url = "https://hz.lianjia.com"
    start_urls = ['https://hz.lianjia.com/ershoufang/']

    def parse(self, response):
        selections = response.xpath(
            "/html/body/div[3]/div[@class='m-filter']/div[@class='position']/dl[2]/dd/div[1]/div/a")
        for sel in selections:
            zone = Zone()
            zone["district"] = sel.xpath("text()").extract_first()
            link = sel.xpath("@href").extract_first()  # eg: /ershoufang/xihu/
            url = self.root_url + link
            zone["district_url_lj"] = link
            yield Request(url=url, callback=self.process_section1, meta={'item': zone})

    def process_section1(self, response):
        selections = response.xpath(
            "/html/body/div[3]/div[@class='m-filter']/div[@class='position']/dl[2]/dd/div[1]/div[2]/a")
        for sel in selections:
            zone = response.meta.get('item').copy()
            zone["bizcircle"] = sel.xpath("text()").extract_first()
            link = sel.xpath("@href").extract_first()  # eg: /ershoufang/cuiyuan/
            zone["bizcircle_url_lj"] = link
            yield zone

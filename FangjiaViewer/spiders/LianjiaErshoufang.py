# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.http import Request

from FangjiaViewer.config import LJCONFIG
from FangjiaViewer.items import House
from FangjiaViewer.shared import safe_list_get_first, safe_list_get


class LianjiaershoufangSpider(scrapy.Spider):
    name = "LianjiaErshoufang"
    allowed_domains = ["lianjia.com"]
    root_url = "https://hz.lianjia.com"
    start_urls = ['https://hz.lianjia.com/ershoufang/']

    flood_pattern = re.compile(r"([\u4e00-\u9fff]+楼层)\(共([0-9]*)层\)[0-9]{4}年[\u4e00-\u9fff]+  -  [\u4e00-\u9fff]+")

    def parse(self, response):
        selections = response.xpath(
            "/html/body/div[3]/div[@class='m-filter']/div[@class='position']/dl[2]/dd/div[1]/div/a")
        for selection in selections:
            link = selection.xpath("@href").extract()[0]  # eg: /ershoufang/xihu/
            url = self.root_url + link
            yield Request(url=url, callback=self.process_section1)

    def process_section1(self, response):
        selections = response.xpath(
            "/html/body/div[3]/div[@class='m-filter']/div[@class='position']/dl[2]/dd/div[1]/div[2]/a")
        for sel in selections:
            link = safe_list_get_first(sel.xpath("@href").extract(), "")  # eg: /ershoufang/cuiyuan/
            url = self.root_url + link
            yield Request(url=url, callback=self.process_section2)

    def process_section2(self, response):
        xpath = "/html/body/div[@class='content ']/div[@class='leftContent']/div[@class='resultDes clear']/h2[@class='total fl']/span/text()"
        max_items = response.xpath(xpath).extract()[0]
        max_items = int(max_items)
        xpath = "/html/body/div[@class='content ']/div[@class='leftContent']/ul/li[@class='clear LOGCLICKDATA']"
        item_num_per_page = len(response.xpath(xpath))
        if max_items and item_num_per_page != 0:
            max_page = (max_items + item_num_per_page - 1) / item_num_per_page
        else:
            max_page = LJCONFIG['MAXPAGE']
        # max_page = 2  # TODO: debug
        urls = [
            self.root_url + "/ershoufang/pg" + str(pgIdx) + '/' for pgIdx in range(1, int(max_page))
        ]
        for url in urls:
            yield Request(url=url, callback=self.process_house_list)

    def process_house_list(self, response):
        xpath = "/html/body/div[@class='content ']/div[@class='leftContent']/ul/li[@class='clear LOGCLICKDATA']/div[@class='info clear']"
        house_list = response.xpath(xpath)
        for sel in house_list:
            link = safe_list_get_first(sel.xpath("div[@class='title']/a/@href").extract(), "")  # https://hz.lianjia.com/ershoufang/103102482192.html
            house = House()
            house['community_name'] = safe_list_get_first(sel.xpath("div[@class='address']/div[@class='houseInfo']/a/text()").extract(), "")
            house['community_name'] = house['community_name'].strip()
            house_info = safe_list_get_first(sel.xpath("div[@class='address']/div[@class='houseInfo']/text()").extract(), "")
            house_infos = house_info.split(" | ")
            house['room'] = house_infos[1]
            house['area'] = house_infos[2]
            house['orient'] = house_infos[3]
            house['decoration'] = house_infos[4]
            house['elevator'] = safe_list_get(house_infos, 5, "")
            flood_info = safe_list_get_first(sel.xpath("div[@class='flood']/div[@class='positionInfo']/text()").extract(), "")
            flood_match = self.flood_pattern.match(flood_info)
            house['flood'] = flood_match.group(1) if flood_match else flood_info
            house['total_flood'] = flood_match.group(2) if flood_match else flood_info
            price_info = safe_list_get_first(sel.xpath("div[@class='priceInfo']/div[@class='totalPrice']/span/text()").extract(), "")
            house['total_price'] = price_info + "0000"  # 万
            house['url_lj'] = str.replace(link, self.root_url, "")
            yield Request(url=link, callback=self.process_house_details, meta={'item': house})

    def process_house_details(self, response):
        house = response.meta.get('item').copy()
        return house

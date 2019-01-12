# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request

from FangjiaViewer.config import LJCONFIG
from FangjiaViewer.items import Community
from FangjiaViewer.shared import safe_list_get_first


class LianjiajiuxiaoquSpider(scrapy.Spider):
    name = 'LianjiaJiuxiaoqu'
    allowed_domains = ['lianjia.com']
    root_url = "https://hz.lianjia.com"
    start_urls = ['https://hz.lianjia.com/xiaoqu/']

    building_year_pattern = re.compile(r"([0-9]{4})年建成")

    def parse(self, response):
        xpath = "/html/body/div[@class='m-filter']/div[@class='position']/dl[2]/dd/div/div[1]/a"
        selections = response.xpath(xpath)
        for sel in selections:
            link = safe_list_get_first(sel.xpath("@href").extract(), "")  # eg: /ershoufang/xihu/
            url = self.root_url + link
            yield Request(url=url, callback=self.process_section1)

    def process_section1(self, response):
        xpath = "/html/body/div[@class='m-filter']/div[@class='position']/dl[2]/dd/div/div[2]/a"
        selections = response.xpath(xpath)
        for sel in selections:
            link = safe_list_get_first(sel.xpath("@href").extract(), "")  # eg: /ershoufang/cuiyuan/
            url = self.root_url + link
            yield Request(url=url, callback=self.process_section2)

    def process_section2(self, response):
        xpath = "/html/body/div[4]/div[@class='leftContent']/div[@class='resultDes clear']/h2[@class='total fl']/span/text()"
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
            response.url + "/pg" + str(pgIdx) + '/' for pgIdx in range(1, int(max_page))
        ]
        for url in urls:
            yield Request(url=url, callback=self.process_community_list)

    def process_community_list(self, response):
        xpath = "/html/body/div[@class='content']/div[@class='leftContent']/ul[@class='listContent']/li[@class='clear xiaoquListItem']"
        community_list = response.xpath(xpath)
        for sel in community_list:
            link = safe_list_get_first(sel.xpath("div[@class='info']/div[@class='title']/a/@href").extract(), "")
            community = Community()
            community['name'] = safe_list_get_first(sel.xpath("div[@class='info']/div[@class='title']/a/text()").extract(), "")
            community['selling_status'] = "ershou"
            community['district'] = safe_list_get_first(sel.xpath("div[@class='info']/div[@class='positionInfo']/a[@class='district']/text()").extract(), "")
            community['bizcircle'] = safe_list_get_first(sel.xpath("div[@class='info']/div[@class='positionInfo']/a[@class='bizcircle']/text()").extract(), "")
            community['main_avg_price_perm'] = safe_list_get_first(sel.xpath("div[@class='xiaoquListItemRight']/div[@class='xiaoquListItemPrice']/div[@class='totalPrice']/span/text()").extract(), "")
            community['url_lj'] = "/" + "/".join(link.split("/")[3:])  # eg: https://hz.lianjia.com/xiaoqu/1811043641802/ => /xiaoqu/1811043641802/
            yield Request(url=link, callback=self.process_community_details, meta={'item': community})

    def process_community_details(self, response):
        community = response.meta.get('item').copy()
        community["location"] = response.xpath("/html/body/div[@class='xiaoquDetailHeader']/div[@class='xiaoquDetailHeaderContent clear']/div[@class='detailHeader fl']/div[@class='detailDesc']/text()").extract()[0]
        sel = response.xpath("/html/body/div[@class='xiaoquOverview']")
        year_string = safe_list_get_first(sel.xpath("div[@class='xiaoquDescribe fr']/div[@class='xiaoquInfo']/div[@class='xiaoquInfoItem'][1]/span[@class='xiaoquInfoContent']/text()").extract(), "")
        year_string = year_string.strip()
        year_string_match = self.building_year_pattern.match(year_string)
        community["building_date"] = year_string_match.group(1) if year_string_match else year_string
        community["building_type"] = safe_list_get_first(sel.xpath("div[@class='xiaoquDescribe fr']/div[@class='xiaoquInfo']/div[@class='xiaoquInfoItem'][2]/span[@class='xiaoquInfoContent']/text()").extract(), "")
        community["estate_developer"] = safe_list_get_first(sel.xpath("div[@class='xiaoquDescribe fr']/div[@class='xiaoquInfo']/div[@class='xiaoquInfoItem'][5]/span[@class='xiaoquInfoContent']/text()").extract(), "")
        return community

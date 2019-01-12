# -*- coding: utf-8 -*-
import re

from scrapy.http import Request
from scrapy.spiders import Spider

from FangjiaViewer.config import LJCONFIG
from FangjiaViewer.items import Community
from FangjiaViewer.shared import safe_list_get_first


class LianjiaxinxiaoquSpider(Spider):
    name = "LianjiaXinxiaoqu"
    allowed_domains = ["lianjia.com"]
    root_url = 'https://hz.fang.lianjia.com'
    start_urls = [
        'https://hz.fang.lianjia.com/loupan/'
    ]
    area_range_pattern = re.compile(r"建面 (([1-9][0-9]*-){0,1}([1-9][0-9]*))㎡")
    price_pattern = re.compile(r"总价([1-9][0-9]*)万/套起")
    green_rate_pattern = re.compile(r".*\n.*([0-9]{2,3})%\n.*")  # 30%\n
    total_area_pattern = re.compile(r".*\n\s+([0-9\,]*).*\n.*")  # 34,499㎡\n
    volume_rate_pattern = re.compile(r".*\n\s+([0-9\.]*)\n.*")  # 2.50\n

    def parse(self, response):
        max_items = response.xpath('/html/body/div[5]/@data-total-count').extract()[0]
        max_items = int(max_items)
        xpath = "/html/body/div[@class='resblock-list-container clearfix']/ul[@class='resblock-list-wrapper']/li[@class='resblock-list post_ulog_exposure_scroll has-results']"
        item_num_per_page = len(response.xpath(xpath))
        if max_items and item_num_per_page != 0:
            max_page = (max_items + item_num_per_page - 1) / item_num_per_page
        else:
            max_page = LJCONFIG['MAXPAGE']
        # max_page = 2  # TODO: debug
        urls = [
            'https://hz.fang.lianjia.com/loupan/pg' + str(pgIdx) + '/' for pgIdx in range(1, int(max_page))
        ]
        for url in urls:
            yield Request(url=url, callback=self.process_community_list)

    def process_community_list(self, response):
        xpath = "/html/body/div[@class='resblock-list-container clearfix']/ul[@class='resblock-list-wrapper']/li[@class='resblock-list post_ulog_exposure_scroll has-results']/div[@class='resblock-desc-wrapper']"
        community_list = response.xpath(xpath)
        for sel in community_list:
            link = safe_list_get_first(sel.xpath("div[@class='resblock-name']/a[@class='name ']/@href").extract(), "")
            community = Community()
            community['name'] = safe_list_get_first(sel.xpath("div[@class='resblock-name']/a[@class='name ']/text()").extract(), "")
            community['type'] = safe_list_get_first(sel.xpath('div[1]/span[1]/text()').extract(), "")
            community['selling_status'] = safe_list_get_first(sel.xpath('div[1]/span[2]/text()').extract(), "")
            community['district'] = '|'.join(sel.xpath('div[2]/span/text()').extract())
            community['bizcircle'] = safe_list_get_first(sel.xpath('div[2]/a/text()').extract(), "")
            community['room'] = '|'.join(sel.xpath('a/span/text()').extract())
            area_range = safe_list_get_first(sel.xpath('div[3]/span/text()').extract(), "")
            area_range_match = self.area_range_pattern.match(area_range)
            community['area_range'] = area_range_match.group(1) if area_range_match else area_range
            community['tags'] = '|'.join(sel.xpath('div[5]/span/text()').extract())
            community['main_avg_price_perm'] = safe_list_get_first(sel.xpath('div[6]/div[1]/span/text()').extract(), "")
            community['min_total_price'] = safe_list_get_first(sel.xpath('div[6]/div[2]/text()').extract(), "")
            total_price = community['min_total_price']
            total_price_match = self.price_pattern.match(community['min_total_price'])
            community['min_total_price_per_house'] = total_price_match.group(1) + "0000" if total_price_match else total_price  # 100万/套
            community['url_lj'] = link  # eg: /loupan/p_zcxgafsaj/
            url = self.root_url + link + "xiangqing/"
            yield Request(url=url, callback=self.process_community_details, meta={"item": community})

    def process_community_details(self, response):
        xpath="/html/body/div[@class='add-panel clear']/div[@class='big-left fl']/"
        sel = response.xpath("/html/body/div[@class='add-panel clear']/div[@class='big-left fl']")
        community = response.meta.get("item")
        community['location'] = safe_list_get_first(sel.xpath("ul[@class='x-box'][1]/li[@class='all-row'][1]/span[@class='label-val']/text()").extract(), "")
        community['estate_developer'] = safe_list_get_first(sel.xpath("ul[@class='x-box'][1]/li[@class='all-row'][3]/span[@class='label-val']/text()").extract(), "")
        community['building_date'] = safe_list_get_first(sel.xpath("ul[@class='fenqi-ul']/li[@class='fq-nbd'][1]/span[@class='fq-td fq-open']/span/text()").extract(), "")
        community['selling_date'] = safe_list_get_first(sel.xpath("ul[@class='fenqi-ul']/li[3]/span[@class='fq-td fq-open']/span/text()").extract(), "")
        community['building_type'] = safe_list_get_first(sel.xpath("ul[@class='x-box'][2]/li[1]/span[@class='label-val']/text()").extract(), "")
        total_area = safe_list_get_first(sel.xpath("ul[@class='x-box'][2]/li[3]/span[@class='label-val']/text()").extract(), "")
        total_area_match = self.total_area_pattern.match(safe_list_get_first(sel.xpath("ul[@class='x-box'][2]/li[3]/span[@class='label-val']/text()").extract(), ""))
        community['total_area'] = total_area_match.group(1) if total_area_match else total_area
        total_building_area = safe_list_get_first(sel.xpath("ul[@class='x-box'][2]/li[5]/span[@class='label-val']/text()").extract(), "")
        total_building_area_match = self.total_area_pattern.match(total_building_area)
        community['total_building_area'] = total_building_area_match.group(1) if total_building_area_match else total_building_area
        green_rate = safe_list_get_first(sel.xpath("ul[@class='x-box'][2]/li[2]/span[@class='label-val']/text()").extract(), "")
        green_rate_match = self.green_rate_pattern.match(green_rate)
        community['green_rate'] = green_rate_match.group(1) if green_rate_match else green_rate
        volume_rate = safe_list_get_first(sel.xpath("ul[@class='x-box'][2]/li[4]/span[@class='label-val']/text()").extract(), "")
        volume_rate_match = self.volume_rate_pattern.match(volume_rate)
        community['volume_rate'] = volume_rate_match.group(1) if volume_rate_match else volume_rate
        return community

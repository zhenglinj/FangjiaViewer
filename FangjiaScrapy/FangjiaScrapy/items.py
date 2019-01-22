# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Zone(scrapy.Item):
    district = scrapy.Field()
    bizcircle = scrapy.Field()
    district_url_lj = scrapy.Field()
    bizcircle_url_lj = scrapy.Field()


class Community(scrapy.Item):
    name = scrapy.Field()
    type = scrapy.Field()
    district = scrapy.Field()
    bizcircle = scrapy.Field()
    room = scrapy.Field()
    orig_area_range = scrapy.Field()
    area_range = scrapy.Field()
    tags = scrapy.Field()
    # details
    location = scrapy.Field()
    estate_developer = scrapy.Field()
    orig_building_date = scrapy.Field()
    building_type = scrapy.Field()
    orig_total_area = scrapy.Field()
    total_area = scrapy.Field()
    orig_total_building_area = scrapy.Field()
    total_building_area = scrapy.Field()
    orig_green_rate = scrapy.Field()
    green_rate = scrapy.Field()
    orig_volume_rate = scrapy.Field()
    volume_rate = scrapy.Field()
    # changeable variable
    building_date = scrapy.Field()
    selling_date = scrapy.Field()
    selling_status = scrapy.Field()
    main_avg_price_perm = scrapy.Field()
    min_total_price = scrapy.Field()
    min_total_price_per_house = scrapy.Field()
    # short url
    url_lj = scrapy.Field()

    # extra info
    community_id = scrapy.Field()
    effective_date = scrapy.Field()


class House(scrapy.Item):
    community_name = scrapy.Field()
    room = scrapy.Field()
    area = scrapy.Field()
    orient = scrapy.Field()
    decoration = scrapy.Field()
    elevator = scrapy.Field()
    orig_flood_info = scrapy.Field()
    flood = scrapy.Field()
    total_flood = scrapy.Field()
    # details
    # changeable variable
    total_price = scrapy.Field()
    # short url
    url_lj = scrapy.Field()

    # extra info
    community_id = scrapy.Field()
    house_id = scrapy.Field()
    effective_date = scrapy.Field()

# -*- coding: utf-8 -*-

import unittest

from .items import Community
from .itemdaos import CommunityDao
from .pipelines import DbSinkPipeline


class TestFangjiaScrapyPipeline(unittest.TestCase):
    pipeline = None

    def setUp(self):
        self.pipeline = FangjiaScrapyDbSinkPipeline()

    def testDbInsertData(self):
        item = Community()
        item['url_lj'] = 'abc'
        item['name'] = 'x小区'
        item['type'] = 'type'
        item['selling_status'] = 'saleStatus'
        item['district'] = 'location1'
        item['bizcircle'] = 'location2'
        item['room'] = 'room'
        item['area_range'] = 'area_range'
        item['tags'] = 'tags'
        self.pipeline.process_community_data(item)

    def testQueryData(self):
        community = self.pipeline.session.query(CommunityDao).filter(CommunityDao.type=='type1').first()
        if community:
            print(community.__dict__)
        else:
            print(community)

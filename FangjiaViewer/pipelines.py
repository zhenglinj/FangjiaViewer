# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import FangjiaViewer.dbconfig as CONFIG
from FangjiaViewer.itemdaos import Base, ZoneDao, CommunityDao, HouseDao, CommunityHistoryDao, HouseHistoryDao
from FangjiaViewer.items import Zone, Community, House


class FangjiaviewerPipeline(object):
    def process_item(self, item, spider):
        return item


class FangjiaviewerDbSinkPipeline(object):
    engine = None
    DBSession = None
    session = None

    def __init__(self):
        if CONFIG.DBENGINE == 'sqlite3':
            self.engine = create_engine('sqlite:///{0}'.format(os.path.join(os.curdir, 'data', CONFIG.DBNAME + '.db')),
                                        echo=True)

        if CONFIG.DBENGINE == 'mysql':
            self.engine = create_engine(
                'mysql://{0}:{1}@{2}:{3}/{4}?charset=utf8'.format(CONFIG.DBUSER, CONFIG.DBPASSWORD, CONFIG.DBHOST,
                                                                  CONFIG.DBPORT, CONFIG.DBNAME),
                echo=True)

        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()
        Base.metadata.create_all(self.engine)
        # 动态创建orm类,必须继承Base, 这个表名是固定的

    def process_item(self, item, spider):
        if isinstance(item, Zone):
            self.process_zone_data(item)
        if isinstance(item, Community):
            self.process_community_data(item)
        if isinstance(item, House):
            self.process_house_data(item)
        return item

    def process_zone_data(self, item):
        zone = ZoneDao(**item)
        result = self.session.query(ZoneDao).filter(
            ZoneDao.district == zone.district and ZoneDao.bizcircle == zone.bizcircle).first()
        if not result:
            self.session.add(zone)
        self.session.commit()

    def process_community_data(self, item):
        community = CommunityDao(**item)
        result = self.session.query(CommunityDao).filter(CommunityDao.url_lj == community.url_lj).first()
        if not result:
            community.effective_date = datetime.datetime.today()
            self.session.add(community)
        community_history = CommunityHistoryDao(**item)
        community_history.effective_date = datetime.datetime.today()
        self.session.add(community_history)
        self.session.commit()

    def process_house_data(self, item):
        house = HouseDao(**item)
        belong_community = self.session.query(CommunityDao).filter(CommunityDao.name == item["community_name"]).first()
        if belong_community:
            house.communityId = belong_community.__dict__["id"]
        result = self.session.query(HouseDao).filter(HouseDao.url_lj == house.url_lj).first()
        if not result:
            house.effectiveDate = datetime.datetime.today()
            self.session.add(house)
        house_history = HouseHistoryDao(**item)
        house_history.effective_date = datetime.datetime.today()
        self.session.add(house_history)
        self.session.commit()

    def close_spider(self, spider):
        self.session.close()

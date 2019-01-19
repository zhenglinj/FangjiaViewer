# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import FangjiaViewer.dbconfig as CONFIG
from FangjiaViewer.itemdaos import Base, ZoneDao, CommunityDao, HouseDao, CommunityHistoryDao, HouseHistoryDao
from FangjiaViewer.spiders.LianjiaBankuai import LianjiabankuaiSpider
from FangjiaViewer.spiders.LianjiaXinxiaoqu import LianjiaxinxiaoquSpider
from FangjiaViewer.spiders.LianjiaJiuxiaoqu import LianjiajiuxiaoquSpider
from FangjiaViewer.spiders.LianjiaErshoufang import LianjiaershoufangSpider
from FangjiaViewer.shared import BulkBuffer


class FangjiaviewerPipeline(object):
    def process_item(self, item, spider):
        return item


class FangjiaviewerDbSinkPipeline(object):
    engine = None
    DBSession = None
    session = None
    buffer = BulkBuffer()
    bulk_size = CONFIG.DB_BULK_SIZE
    is_initialized = True  # if it is the first time, the is_initialized=false, else the is_initialized=True

    def __init__(self):
        if CONFIG.DBENGINE == 'sqlite3':
            self.engine = create_engine('sqlite:///{0}'.format(os.path.join(os.curdir, 'data', CONFIG.DBNAME + '.db')),
                                        echo=True)

        if CONFIG.DBENGINE == 'mysql':
            self.engine = create_engine(
                'mysql://{0}:{1}@{2}:{3}/{4}?charset=utf8'.format(CONFIG.DBUSER, CONFIG.DBPASSWORD, CONFIG.DBHOST,
                                                                  CONFIG.DBPORT, CONFIG.DBNAME),
                echo=True)

        self.DBSession = scoped_session(sessionmaker())
        self.DBSession.remove()
        self.DBSession.configure(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = self.DBSession()
        Base.metadata.create_all(self.engine)

    def process_item(self, item, spider):
        if isinstance(spider, LianjiabankuaiSpider):
            self.process_zone_data(item, spider)
        elif isinstance(spider, LianjiaxinxiaoquSpider) or isinstance(spider, LianjiajiuxiaoquSpider):
            self.process_community_data(item, spider)
        elif isinstance(spider, LianjiaershoufangSpider):
            self.process_house_data(item, spider)
        else:
            raise Exception("Invalid spider")
        return item

    def process_zone_data(self, item, spider):
        zone = ZoneDao(**item)
        if self.is_initialized:
            result = self.session.query(ZoneDao).filter(
                ZoneDao.district == zone.district and ZoneDao.bizcircle == zone.bizcircle).first()
            if not result:
                self.buffer.add(item)
        else:
            self.buffer.add(item)
        self.process_bulk(spider, self.bulk_size)

    def process_community_data(self, item, spider):
        community = CommunityDao(**item)
        if self.is_initialized:
            result = self.session.query(CommunityDao).filter(CommunityDao.url_lj == community.url_lj).first()
            if not result:
                item["effective_date"] = datetime.datetime.today()
                self.buffer.add(item)
        else:
            self.buffer.add(item)
        self.process_bulk(spider, self.bulk_size)

    def process_house_data(self, item, spider):
        house = HouseDao(**item)
        if self.is_initialized:
            # belong_community = self.session.query(CommunityDao).filter(CommunityDao.name == item["community_name"]).first()
            # if belong_community:
            #     house.community_id = belong_community.__dict__["id"]
            #     item["community_id"] = house.community_id
            result = self.session.query(HouseDao).filter(HouseDao.url_lj == house.url_lj).first()
            if not result:
                item["effective_date"] = datetime.datetime.today()
                self.buffer.add(item)
        else:
            self.buffer.add(item)
        self.process_bulk(spider, self.bulk_size)

    def process_bulk(self, spider, bulk_size=0):
        if self.buffer.get_len() > bulk_size:
            if isinstance(spider, LianjiabankuaiSpider):
                self.engine.execute(
                    ZoneDao.__table__.insert(),
                    self.buffer.get_all()
                )
                self.buffer.empty()
            elif isinstance(spider, LianjiaxinxiaoquSpider) or isinstance(spider, LianjiajiuxiaoquSpider):
                self.engine.execute(
                    CommunityDao.__table__.insert(),
                    self.buffer.get_all()
                )
                self.engine.execute(
                    CommunityHistoryDao.__table__.insert(),
                    self.buffer.get_all()
                )
                self.buffer.empty()
            elif isinstance(spider, LianjiaershoufangSpider):
                self.engine.execute(
                    HouseDao.__table__.insert(),
                    self.buffer.get_all()
                )
                self.engine.execute(
                    HouseHistoryDao.__table__.insert(),
                    self.buffer.get_all()
                )
                self.buffer.empty()
            self.session.commit()

    def close_spider(self, spider):
        self.process_bulk(spider)
        self.session.close()

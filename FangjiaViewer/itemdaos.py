# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ZoneDao(Base):
    __tablename__ = 'Zone'

    id = Column(Integer, primary_key=True)  # 主键自增
    district = Column(String(100))
    bizcircle = Column(String(100))
    district_url_lj = Column(String(100))
    bizcircle_url_lj = Column(String(100))

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])


class CommunityDao(Base):
    __tablename__ = 'Community'

    id = Column(Integer, primary_key=True)  # 主键自增
    name = Column(String(100))
    type = Column(String(100))
    district = Column(String(100))
    bizcircle = Column(String(100))
    room = Column(String(100))
    orig_area_range = Column(String(100))
    area_range = Column(String(100))
    tags = Column(String(100))
    # details
    location = Column(String(100))
    estate_developer = Column(String(100))
    orig_building_date = Column(String(100))
    building_type = Column(String(100))
    orig_total_area = Column(String(100))
    total_area = Column(String(100))
    orig_total_building_area = Column(String(100))
    total_building_area = Column(String(100))
    orig_green_rate = Column(String(100))
    green_rate = Column(String(100))
    orig_volume_rate = Column(String(100))
    volume_rate = Column(String(100))
    # short url
    url_lj = Column(String(100))

    # extra info
    effective_date = Column(Date)

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])


class CommunityHistoryDao(Base):
    __tablename__ = 'CommunityHistory'

    id = Column(Integer, primary_key=True)  # 主键自增
    community_id = Column(Integer, ForeignKey('Community.id'))
    community = relationship(CommunityDao)
    # changeable variable
    building_date = Column(String(100))
    selling_date = Column(String(100))
    selling_status = Column(String(100))
    main_avg_price_perm = Column(String(100))
    min_total_price = Column(String(100))
    min_total_price_per_house = Column(String(100))
    # short url
    url_lj = Column(String(100))

    # extra info
    effective_date = Column(Date)

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])


class HouseDao(Base):
    __tablename__ = 'House'

    id = Column(Integer, primary_key=True)  # 主键自增
    community_id = Column(Integer, ForeignKey('Community.id'))
    community = relationship(CommunityDao)
    community_name = Column(String(100))
    room = Column(String(100))
    area = Column(String(100))
    orient = Column(String(100))
    decoration = Column(String(100))
    elevator = Column(String(100))
    orig_flood_info = Column(String(100))
    flood = Column(String(100))
    total_flood = Column(String(100))
    url_lj = Column(String(100))

    # extra info
    effective_date = Column(Date)

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])


class HouseHistoryDao(Base):
    __tablename__ = 'HouseHistory'

    id = Column(Integer, primary_key=True)  # 主键自增
    house_id = Column(Integer, ForeignKey('House.id'))
    house = relationship(HouseDao)
    # changeable variable
    total_price = Column(String(100))
    url_lj = Column(String(100))
    # extra info
    effective_date = Column(Date)

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])

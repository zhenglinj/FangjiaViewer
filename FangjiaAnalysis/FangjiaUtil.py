# -*- coding: utf-8 -*-

import datetime
from sys import version_info

import pandas as pd

if version_info.major != 3:
    raise Exception('请使用Python 3 来完成此项目')


def load_data(conn):
    zone_df = pd.read_sql('select * from Zone;', con=conn)
    community_df = pd.read_sql('select * from Community;', con=conn)
    community_hist_df = pd.read_sql('select * from CommunityHistory;', con=conn)
    house_df = pd.read_sql('select * from House;', con=conn)
    house_hist_df = pd.read_sql('select * from HouseHistory;', con=conn)

    # new community ############
    # merge hangzhou zone
    new_df = pd.merge(community_df, zone_df, how='right', left_on=['district', 'bizcircle'],
                      right_on=['district', 'bizcircle'], suffixes=('', '_'))
    new_df = new_df[new_df['id'].notna()]
    # merge history price
    new_df = pd.merge(new_df, community_hist_df, how='left', left_on='url_lj', right_on='url_lj', suffixes=('', '_'))
    new_df = new_df[new_df['id'].notna()]
    # cast some columns to numeric
    new_df['id'] = new_df['id'].astype(int)
    new_df['total_area'] = new_df['total_area'].str.replace(',', '')
    new_df['days_to_today'] = pd.Timestamp(datetime.datetime.now().date())
    new_df['building_date'] = new_df['building_date'].str.replace('预计', '', regex=False)
    new_df['building_date'] = pd.to_datetime(new_df['building_date'], format='%Y-%m-%d', errors='coerce')
    new_df['days_to_today'] = (new_df['building_date'] - new_df['days_to_today']).apply(lambda x: x.days)
    new_df['total_building_area'] = new_df['total_building_area'].str.replace(',', '')
    # cast some columns to numeric
    for col in ('total_area', 'total_building_area', 'green_rate', 'volume_rate', 'main_avg_price_perm',
                'min_total_price_per_house'):
        new_df[col] = pd.to_numeric(new_df[col], errors='coerce')
    # filter fields
    new_df = new_df[['id', 'name', 'type', 'district', 'bizcircle', 'location', 'building_type', 'total_area',
                     'total_building_area', 'green_rate', 'volume_rate', 'building_date', 'days_to_today',
                     'main_avg_price_perm', 'min_total_price_per_house']]
    # old house ############
    # merge hangzhou zone with new_df
    old_df = pd.merge(house_df, new_df, how='left', left_on=['community_name'], right_on=['name'])
    # merge history price
    old_df = pd.merge(old_df, house_hist_df, how='left', left_on='url_lj', right_on='url_lj', suffixes=('', '_'))
    old_df = old_df[old_df['id'].notna()]
    # cast some columns to numeric
    old_df['area'] = old_df['area'].str.replace('平米', '', regex=False)
    for col in ('green_rate', 'volume_rate', 'area', 'total_price'):
        old_df[col] = pd.to_numeric(old_df[col], errors='coerce')
    # drop_duplicates
    old_df = old_df.sort_values(by=['community_name', 'type', 'district', 'bizcircle', 'location', 'building_type',
                                    'green_rate', 'volume_rate', 'building_date', 'total_price'])
    old_df = old_df.drop_duplicates(subset=['community_name', 'district', 'bizcircle'])
    old_df = old_df[old_df['id'].notna()]
    # filter fields
    old_df = old_df[['id', 'community_name', 'type', 'district', 'bizcircle', 'location', 'building_type', 'green_rate',
                     'volume_rate', 'building_date', 'days_to_today', 'room', 'area', 'orient', 'decoration',
                     'elevator', 'orig_flood_info', 'flood', 'total_flood', 'total_price']]

    return new_df, old_df

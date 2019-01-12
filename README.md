# FangjiaViewer

- 该项目基于Python3 scrapy, sqlalchemy等框架的房源数据抓取分析工具；支持新房，二手房房源爬虫，支持MySQL, SQLite3数据持久化存储；通过Pyhton Jupyter Notebook做数据分析
- **此代码仅供学习与交流，请勿用于商业用途后果自负**


# 使用说明

## 背景知识

- 爬虫基于Python scrapy框架，需要对该工具基本使用方法有所了解。[scrapy官方文档](https://scrapy-chs.readthedocs.io/zh_CN/latest/)
- 目前支持持久化到MySQL / SQLite3，需要对MySQL / SQLite3有所了解。本项目以爬取 Hangzhou 数据并持久化到SQLite3为例

## 下载源码和安装依赖包

```shell
git clone https://github.com/zhenglinj/FangjiaViewer.git
# If you'd like not to use [virtualenv](https://virtualenv.pypa.io/en/stable/), please skip below 2 steps
virtualenv fangjia
source fangjia/bin/activate
pip install -r requirements.txt
```

## 配置

**配置数据源网站相关参数**

如，链家网搜索/查看结果最多显示100页

```python
### user config
LJCONFIG = {
    'MAXPAGE': 100
}
```

**配置数据库 `dbconfig.py`**

```python
DBENGINE = 'sqlite3'  # ENGINE OPTIONS: mysql, sqlite3
DBNAME = 'HangZhouFangJia'
DBUSER = 'root'
DBPASSWORD = 'toor'
DBHOST = '127.0.0.1'
DBPORT = 3306
```

## 数据关系

小区信息依赖于区域/板块信息，每户房信息依赖于小区信息

```
Zone

Community <- House

Community <- CommunityHistory

House <- HouseHistory
```

## 运行爬虫

由于数据依赖关系启动爬虫有先后次序

```shell
scrapy list
# LianjiaBankuai
# LianjiaErshoufang
# LianjiaJiuxiaoqu
# LianjiaXinxiaoqu

# 获取区域/板块信息
scrapy crawl LianjiaBankuai
# 获取小区信息
scrapy crawl LianjiaXinxiaoqu
scrapy crawl LianjiaJiuxiaoqu
# 获取每户房信息
scrapy crawl LianjiaErshoufang
```

# TODO

- [ ] 增加更多数据源，如透明售房网(tmsf.com)，我爱我家(5i5j.com)
- [ ] 增加更多数据分析

# Change Logs

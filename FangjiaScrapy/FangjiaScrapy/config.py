# -*- coding: utf-8 -*-

### Vender config
class LianjiaConfig:
    MAXPAGE = 100


### Database config
class DBConfig:
    DBENGINE = 'sqlite3'  # ENGINE OPTIONS: mysql, sqlite3
    DBNAME = 'HangZhouFangJia'
    DBUSER = 'root'
    DBPASSWORD = 'toor'
    DBHOST = '127.0.0.1'
    DBPORT = 3306
    DB_BULK_SIZE = 1000

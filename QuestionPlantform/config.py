import os
from datetime import timedelta

# debug模式
DEBUG = True

# 配置数据库
DIALECT = 'mysql'
DRIVER = 'mysqldb'
USERNAME = 'root'
PASSWORD = '1234'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'questionplantform'
# SQLALCHEMY标志URI
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8" \
    .format(DIALECT, DRIVER, USERNAME,
            PASSWORD, HOST, PORT,
            DATABASE)
# 忽略SQLALCHEMY警告
SQLALCHEMY_TRACK_MODIFICATIONS = False

# session
# 设置session'盐'：SECRET_KEY
SECRET_KEY = os.urandom(24)
# 设置session过期时间，25天，设置permanent默认一个月，没设置关闭浏览器就销毁
PERMANENT_SESSION_LIFETIME = timedelta(days=25)

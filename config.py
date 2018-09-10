# -*- coding: UTF-8 -*-
import configparser
import os

# 用os模块来读取
curpath = os.path.dirname(os.path.realpath(__file__))
cfgpath = os.path.join(curpath, "config.ini")  # 读取到本机的配置文件

conf = configparser.ConfigParser()
conf.read(cfgpath, 'UTF-8')
# 获取数据库配置信息
host = conf.get('database_14', 'gsMSSQLServerHostName')
db = conf.get('database_14', 'gsMSSQLServerDatabaseName')
port = conf.get('database_14', 'gsMSSQLServerPortNumber')
user = conf.get('database_14', 'gsMSSQLServerUserName')
pwd = conf.get('database_14', 'gsMSSQLServerPassword')


# 获取上一次更新时间
time_point = conf.get('update_time', 'time_point')


def set(time_point):
    conf.set('update_time', 'time_point', time_point)
    conf.write(open("config.ini", "w"))
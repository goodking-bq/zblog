# -*- coding:utf-8 -*-

import os

CSRF_ENABLED = False
SECRET_KEY = 'you-will-never-guess'
#WTF_CSRF_ENABLED  = True


basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI ='mysql://root:zoushjde@192.168.137.2/blog'
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'blog.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')





#邮件服务器设置
MAIL_SERVER = 'smtp.exmail.qq.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'email@zousj.cn'
MAIL_PASSWORD = 'z120225883'


# administrator list
ADMINS = ['email@zousj.cn']

#每页显示的文章数
ARTICLES_PER_PAGE = 5
#随机密码长度
RANDOM_PASSWORD_LENGTH=5
#全文搜索数据库
WHOOSH_BASE = os.path.join(basedir, 'search.db') #路径
MAX_SEARCH_RESULTS = 50 #搜索最大返回数
# -*- coding:utf-8 -*-

import os
import datetime

CSRF_ENABLED = False
WTF_CSRF_ENABLED = True
SECRET_KEY = '120225883@qq.com'
REMEMBER_COOKIE_DURATION = datetime.timedelta(seconds=30)
""" session 过期时间 """
PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=5)
WTF_CSRF_ENABLED = True

"""本程序根目录"""
basedir = os.path.abspath(os.path.dirname(__file__))

"""数据库设置"""
SQLALCHEMY_DATABASE_URI = 'mysql://root:zoushjde@192.168.137.2/blog'
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'blog.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

"""邮件服务器设置"""
MAIL_SERVER = 'smtp.exmail.qq.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'email@zousj.cn'
MAIL_PASSWORD = 'z120225883'

"""管理员邮箱配置"""
ADMINS = ['email@zousj.cn', '120225883@qq.com']

"""每页显示的文章数"""
ARTICLES_PER_PAGE = 10
"""随机密码长度"""
RANDOM_PASSWORD_LENGTH = 5
"""全文搜索数据库"""
WHOOSH_BASE = os.path.join(basedir, 'search.db')  #路径
MAX_SEARCH_RESULTS = 50  #搜索最大返回数

"""上传文件配置"""
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'rar', 'zip', 'tar', 'word', 'xsl', 'xsls'])
MAX_CONTENT_LENGTH = 20 * 1024 * 1024

""" 备份路径 """
BACKUP_DIR = os.path.join(basedir, 'backup')
LOG_DIR = os.path.join(basedir, 'tmp')

""" 机器人访问关键字 """
ROBOT_VISIT = set(
    ['Baiduspider', 'JianKongBao', 'DotBot', 'bingbot', 'Googlebot', '360Spider', 'EasouSpider', 'YisouSpider',
     'Sogou web spider'])

"""恶意访问关键字"""
ATTACK_VISIT = set(['php'])

"""配置缓存"""
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 60

"""日志路径配置"""
LOG_NGINX = r'd:\zblog\tmp'
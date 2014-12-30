# -*- coding:utf-8 -*-
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.cache import Cache
from flask.ext.script import Manager
from flask.ext.migrate import Migrate
from flask_wtf.csrf import CsrfProtect
from flask_oauthlib.client import OAuth
from config import LOG_DIR

blog = Flask(__name__)
blog.config.from_object('config')

csrf = CsrfProtect()
csrf.init_app(blog)

db = SQLAlchemy(blog)

lm = LoginManager()
lm.init_app(blog)
lm.login_view = 'login'
lm.login_message = u"请先登录"

cache = Cache(blog)

oauth = OAuth(blog)

'''控制台'''
manager = Manager(blog)
'''数据库更新'''
migrate = Migrate(blog, db)

# mail
from flask.ext.mail import Mail

mymail = Mail(blog)

from blog import views, models, Urls, admin, upload, backup


'''日志设置'''
'''
if not blog.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    blog.logger.addHandler(mail_handler)
'''

if not blog.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler(LOG_DIR + '/blog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    blog.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    blog.logger.addHandler(file_handler)
    blog.logger.info('blog startup')
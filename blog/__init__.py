# -*- coding:utf-8 -*-
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.cache import Cache
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, \
    MAIL_PASSWORD, LOG_DIR, SQLALCHEMY_DATABASE_URI

blog = Flask(__name__)
blog.config.from_object('config')

db = SQLAlchemy(blog)

lm = LoginManager()
lm.init_app(blog)
lm.login_view = 'login'
lm.login_message = u"请先登录"

cache = Cache(blog)


# oid = OpenID(blog, os.path.join(basedir, 'tmp'))

# mail
from flask.ext.mail import Mail

mymail = Mail(blog)

from blog import views, models, Urls, admin, upload, backup




# logs
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
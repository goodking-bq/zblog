#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'

from setuptools import setup, find_packages

setup(
    name='Zou-Blog',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-Cache',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'Flask-Testing',
        'Flask-Script',
        'Flask-Uploads',
        'Flask-Login',
        'Flask-MySQL',
        'Flask-WhooshAlchemy',
        'Flask-Mail',
        'Flask-Migrate'
        # 'sqlalchemy',
        # 'Werkzeug',
        # 'WTForms'
    ],
    author="gooken",
    author_email="mail@zousj.cn",
    description=u"这是一个简单的博客",
    keywords=u'一个简单的博客',
    url='www.zousj.cn'
)
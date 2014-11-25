#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'
__create__ = '2014-11-13'

from blog import manager
from flask.ext.migrate import MigrateCommand
from blog.extend.LogHelper import LogManager


manager.add_command('db', MigrateCommand)
manager.add_command('log', LogManager)

if __name__ == '__main__':
    manager.run()
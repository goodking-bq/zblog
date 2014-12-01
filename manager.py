#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'
__create__ = '2014-11-13'

from blog import manager
from flask.ext.migrate import MigrateCommand, command
from blog.extend.LogHelper import LogManager
from blog.extend.InitHelper import InitManager

manager.add_command('migrate', MigrateCommand)
manager.add_command('log', LogManager)
manager.add_command('init', InitManager)

if __name__ == '__main__':
    manager.run()
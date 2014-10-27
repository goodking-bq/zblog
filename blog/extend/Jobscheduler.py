#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'
__createday__ = '2014-10-19'
"""
    apscheduler for flask
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.util import undefined


class Jobscheduler(BackgroundScheduler):
    def __init__(self, app=None):
        super(BackgroundScheduler, self).__init__()
        if app is not None:
            self.app = app
        if app.config['SQLALCHEMY_DATABASE_URI']:
            self.db_url = app.config['SQLALCHEMY_DATABASE_URI']
        self.add_jobstore('sqlalchemy', url=self.db_url)

    def wrapper_job_add(self, trigger, args=None, kwargs=None, id=None, name=None, misfire_grace_time=undefined,
                        coalesce=undefined, max_instances=undefined, next_run_time=undefined, jobstore='default',
                        executor='default', **trigger_args):
        print 'inner func'

        def inner(func):
            print 'in inner'
            self.add_job(func, trigger, args, kwargs, id, name, misfire_grace_time, coalesce, max_instances,
                         next_run_time, jobstore, executor, True, **trigger_args)
            print 'end add_job'
            return func

        return inner

    def job_start(self):
        self.start()

    def job_stop(self):
        self.shutdown()

    def job_remove(self, id):
        self.remove_job(job_id=id)





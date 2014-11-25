#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'
__create__ = '2014-11-23'

from blog.models import Article, Visit_log, Blog_info, User, Login_log, Ip_blacklist, Robot
from blog import db, manager
import datetime
from flask.ext.script import Manager, prompt_bool
from config import ROBOT


LogManager = Manager(usage=u'处理访问日志')


@LogManager.option('-i', '--id', help=u'清理的最大ID')
def clean(id=None):
    u"清理日志,max_id默认清理所有"
    if id == None:
        id = db.session.query(db.func.max(Visit_log.id).label('max_id')).first().max_id
    visit_statistics(id)
    for log in db.session.query(Visit_log).filter(Visit_log.id <= id).all():
        db.session.delete(log)  # 删除旧日志
    db.session.commit()
    print u'%s -> 删除所有记录' % datetime.datetime.now()
    print u'%s -> 任务完成' % datetime.datetime.now()


def visit_statistics(max_id):
    import socket

    print u'%s -> 开始归档访问数据 -----' % datetime.datetime.now()
    logs = db.session.query(Visit_log).filter(Visit_log.id <= max_id).all()
    if logs:
        for log in logs:
            if not robot(log):
                php_url(log)
    else:
        print u'%s -> 没有需要归档的黑名单数据' % datetime.datetime.now()


def php_url(log):
    if log.visiturl.find('php') >= 0:
        alter_ip_blacklist(log, u'访问带有PHP的链接')
        return True
    return False


"""判断是否机器人访问，并检查真实性"""


def robot(log):
    import socket

    r = is_robot(log.ipaddr, log.agent)
    if r and r <> 1:
        try:
            a = socket.gethostbyaddr(log.ipaddr)
            v = ROBOT.get(r)
            if a[0].find(v) >= 0:
                print u'%s -> 新增机器人 IP ----- %s' % (datetime.datetime.now(), log.ipaddr)
                rob = Robot(name=r,
                            dns_name=v,
                            ip=log.ipaddr,
                            address=log.real_addr
                )
                db.session.add(rob)
                db.commit()
                return True
            else:
                alter_ip_blacklist(log.ipaddr, log.real_addr, u'爬虫欺骗访问')
                return False
        except:
            alter_ip_blacklist(log.ipaddr, log.real_addr, u'爬虫欺骗访问')
            return False


"""判断是否机器人访问"""


def is_robot(ip, agent):
    ro = Robot.query.filter_by(ip=ip).first()
    if ro:
        return 1
    else:
        for r in ROBOT.keys():
            if agent.find(r) >= 0:
                return r


def alter_ip_blacklist(log, reason):
    ip = Ip_blacklist.find_by_ip(log.ipaddr)
    if ip:
        print u'%s -> 更新记录 IP ----- %s ，原因 ----- %s' % (datetime.datetime.now(), log.ipaddr, reason)
        ip.visit_count += 1
        ip.attack_count += 1
    else:
        print u'%s -> 新增记录 IP ----- %s ，原因 ----- %s' % (datetime.datetime.now(), log.ipaddr, reason)
        ip = Ip_blacklist(ipaddr=log.ipaddr,
                          real_addr=log.real_addr,
                          attack_count=0,
                          is_forbid=0,
                          reason=reason
        )
        ip.forbid_date = datetime.date.today()
    db.session.add(ip)
    db.session.commit()


@LogManager.command
def count():
    u'统计日志条数'
    c = Visit_log.count_all()
    print u'共有访问日志%s条' % c



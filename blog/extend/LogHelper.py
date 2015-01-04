#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'
__create__ = '2014-11-23'
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


from blog.models import Article, Visit_log, Blog_info, User, Login_log, Ip_blacklist, Robot
from blog import db
import datetime
from flask.ext.script import Manager, prompt_bool
from config import ROBOT
from blog.extend.StringHelper import get_ip_location
import socket

LogManager = Manager(usage=u'处理访问日志')


@LogManager.option('-i', '--id', help='清理的最大ID')
def clean(id=None):
    "清理日志,max_id默认清理所有"
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
    logs = db.session.query(Visit_log).filter(Visit_log.id <= max_id).order_by(Visit_log.id).all()
    if logs:
        for log in logs:
            log.date = str(log.timestamp)[:10]
            if not robot(log):
                if not php_url(log):
                    Blog_info.new_visit(log.date)
    else:
        print u'%s -> 没有需要归档的黑名单数据' % datetime.datetime.now()


def php_url(log):
    if log.url.find('php') >= 0:
        alter_ip_blacklist(log, u'访问带有PHP的链接')
        Blog_info.new_attack_visit(log.date)
        return True
    return False


"""判断是否机器人访问，并检查真实性"""


def robot(log):
    r = is_robot(log.ip, log.agent)
    if r == 1:
        Blog_info.new_robot_visit(log.date)
    elif r and r != 1:
        try:
            a = socket.gethostbyaddr(log.ip)
            v = ROBOT.get(r)
            if a[0].find(v) >= 0:
                print u'%s -> 新增机器人 IP ----- %s' % (datetime.datetime.now(), log.ip)
                rob = Robot(name=r,
                            dns_name=v,
                            ip=log.ip,
                            address=get_ip_location(log.ip)
                )
                db.session.add(rob)
                db.commit()
                Blog_info.new_robot_visit(log.date)  #
                return True
            else:
                alter_ip_blacklist(log, u'爬虫欺骗访问')
                Blog_info.new_attack_visit(log.date)
                return False
        except:
            alter_ip_blacklist(log, u'爬虫欺骗访问')
            Blog_info.new_attack_visit(log.date)
            return False
    else:
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
            else:
                return False


def alter_ip_blacklist(log, reason):
    ip = Ip_blacklist.find_by_ip(log.ip)
    Blog_info.new_attack_visit(log.date)
    if ip:
        print u'%s -> 更新记录 IP ----- %s ，原因 ----- %s' % (datetime.datetime.now(), log.ip, reason)
        ip.visit_count += 1
        ip.attack_count += 1
    else:
        print u'%s -> 新增记录 IP ----- %s ，原因 ----- %s' % (datetime.datetime.now(), log.ip, reason)
        ip = Ip_blacklist(ip=log.ip,
                          address=get_ip_location(log.ip),
                          attack_count=0,
                          is_forbid=0,
                          reason=reason
        )
        ip.forbid_date = datetime.date.today()
    db.session.add(ip)
    db.session.commit()


@LogManager.command
def count():
    '统计日志条数'
    c = Visit_log.count_all()
    print u'共有访问日志%s条' % c



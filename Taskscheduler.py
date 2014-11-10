#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'
__createday__ = '2014-10-16'

from blog.models import Article, Visit_log, Blog_info, User, Login_log, Ip_blacklist
from blog import db
import datetime
from flask import redirect, url_for, flash, g
from flask.ext.login import login_required


def visit_statistics():  # 访问统计.filter(Visit_log.id <= max_id)
    if g.user.is_admin():
        max_id = db.session.query(db.func.max(Visit_log.id).label('max_id')).first().max_id
        date = datetime.date.today()
        old = Blog_info.newest_info()
        info = Blog_info()  # 添加本次统计到数据库
        if old:
            info.visit_all = old.visit_all + db.session.query(Visit_log).filter(Visit_log.id <= max_id).count()
            info.visit_day = old.visit_day + db.session.query(Visit_log).filter(Visit_log.id <= max_id,
                                                                                Visit_log.year_month_day == date).count()
            info.visit_month = old.visit_month + db.session.query(Visit_log).filter(Visit_log.id <= max_id,
                                                                                    Visit_log.year_month == str(date)[
                                                                                                            :7]).count()
            info.visit_year = old.visit_year + db.session.query(Visit_log).filter(Visit_log.id <= max_id,
                                                                                  Visit_log.year == str(date)[
                                                                                                    :4]).count()
            info.article_all = Article.count_all()
            info.article_month = Article.count_current_month()
            info.user_all = User.count_all()
            info.login_all = Login_log.count_all()
            info.nowtimes = datetime.datetime.now()
            info.count_attack = old.count_attack + db.session.query(Visit_log).filter(Visit_log.id <= max_id,
                                                                                      Visit_log.visiturl.like(
                                                                                          '%php%')).count()
            info.Statistics = Blog_info.max_Statistics() + 1
        else:
            info.visit_all = db.session.query(Visit_log).filter(Visit_log.id <= max_id).count()
            info.visit_day = db.session.query(Visit_log).filter(Visit_log.id <= max_id,
                                                                Visit_log.year_month_day == date).count()
            info.visit_month = db.session.query(Visit_log).filter(Visit_log.id <= max_id,
                                                                  Visit_log.year_month == str(date)[
                                                                                          :7]).count()
            info.visit_year = db.session.query(Visit_log).filter(Visit_log.id <= max_id,
                                                                 Visit_log.year == str(date)[:4]).count()
            info.article_all = Article.count_all()
            info.article_month = Article.count_current_month()
            info.user_all = User.count_all()
            info.login_all = Login_log.count_all()
            info.nowtimes = datetime.datetime.now()
            info.count_attack = db.session.query(Visit_log).filter(Visit_log.id <= max_id,
                                                                   Visit_log.visiturl.like('%php%')).count()
            info.Statistics = 1
        db.session.add(info)
        for i in Visit_log.ip_attack_count():
            if i:
                ip = Ip_blacklist.find_by_ip(i.ipaddr)
                if ip:
                    ip.visit_count += Visit_log.count_by_ip(ip.ipaddr)
                    ip.attack_count += i.count
                    ip.real_addr = i.real_addr
                else:
                    ip = Ip_blacklist(ipaddr=i.ipaddr,
                                      real_addr=i.real_addr,
                                      attack_count=i.count,
                                      is_forbid=0,
                    )
                    ip.forbid_date = datetime.date.today()
                    ip.visit_count = Visit_log.count_by_ip(i.ipaddr)
                db.session.add(ip)
            else:
                flash(u'没有需要归档的数据')
        for log in db.session.query(Visit_log).filter(Visit_log.id <= max_id).all():
            db.session.delete(log)  # 删除旧日志
        db.session.commit()
    else:
        flash(u'无权限操作')
    return redirect(url_for('index1'))


def test():
    info = Blog_info.query.order_by(Blog_info.id.desc())
    for i in info:
        print i.visit_all


def nginx_log():
    from config import LOG_NGINX

    access = LOG_NGINX + r'\host.access.log'
    log = file(access, 'r').readlines()
    print len(log)


nginx_log()


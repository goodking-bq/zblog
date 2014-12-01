#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'
__createday__ = '2014-11-28'

from blog.models import Blog_info, Settings, User
from datetime import datetime
from flask.ext.script import Manager
from blog import db

InitManager = Manager(usage='初始化博客')


@InitManager.command
def data():
    '初始化数据'
    if Settings.query.filter_by(type='init_date').first():
        print '已初始化数据，不能重复初始化'
    else:
        admin_user()
        Setting_data()
        Blog_info_data()


@InitManager.command
def tables():
    '初始化数据库结构'
    db.create_all()
    print '初始化数据库结构...[确定]'


@InitManager.command
def evn():
    '初始化运行环境'
    from subprocess import Popen

    Popen('python /root/zblog/setup.py install', shell=True)
    print '初始化运行环境...[确定]'


@InitManager.command
def stat():
    '初始化状态检测'
    try:
        date = Settings.query.filter_by(type='init_date').first()
        if not date:
            print '未初始化表数据'
        else:
            print 'blog 已初始化'
    except Exception, e:
        if str(e).find('OperationalError') >= 0:
            print '数据连接错误，请检查配置'
        elif str(e).find('ProgrammingError') >= 0:
            print '表不存在，请初始化数据库结构'
        else:
            print e
            print '未知错误'


@InitManager.command
def all():
    '初始化所有'
    print '第一步：初始化运行环境...'
    evn()
    print '第二步：初始化数据库...'
    db()
    print '第三步：初始化基本数据...'
    data()


def Blog_info_data():
    blog_info = Blog_info()
    blog_info.date = str(datetime.now().date())
    blog_info.visit_all = 0
    blog_info.visit_day = 0
    blog_info.visit_month = 0
    blog_info.visit_attack = 0
    blog_info.visit_attack_day = 0
    blog_info.visit_robot = 0
    blog_info.visit_robot_day = 0
    blog_info.article_all = 0
    blog_info.article_month = 0
    blog_info.user_all = 0
    blog_info.login_all = 0
    db.session.add(blog_info)
    db.session.commit()


def Setting_data():
    # 其他
    default = [('本站用户', '/admin/users', 'admin_second_bar', 1, 4, 'glyphicon glyphicon-USER'),
               ('文章分类', '/admin/category', 'admin_second_bar', 1, 2, 'glyphicon glyphicon-leaf'),
               ('本站文章', '/admin/article', 'admin_second_bar', 1, 3, 'glyphicon glyphicon-book'),
               ('本站概况', '/admin/main', 'admin_second_bar', 1, 1, 'glyphicon glyphicon-home'),
               ('这个菜单', '/admin/admin_second_bar', 'admin_second_bar', 1, 9, 'glyphicon glyphicon-tree-conifer'),
               ('基本设置', '/admin/tagsettings', 'admin_second_bar', 1, 7, 'glyphicon glyphicon-wrench'),
               ('图片管理', '/admin/imgs', 'admin_second_bar', 1, 5, 'glyphicon glyphicon-picture'),
               ('附件管理', '/admin/files', 'admin_second_bar', 1, 6, 'glyphicon glyphicon-FILE'),
               ('我的日历', '/admin/calendar', 'admin_second_bar', 1, 8, 'glyphicon glyphicon-calendar'),
               ('本站备份', '/admin/BACKUP', 'admin_second_bar', 1, 10, 'glyphicon glyphicon-hdd'),
               ('主页', '/INDEX', 'first_bar', 1, 1, 'glyphicon glyphicon-home'),
               ('留言', '/blog_msg', 'first_bar', 1, 2, 'glyphicon glyphicon-COMMENT'),
               ('关于', '/about', 'first_bar', 1, 4, 'glyphicon glyphicon-info-SIGN'),
               ('日历', '/calendar', 'first_bar', 1, 3, 'glyphicon glyphicon-calendar')]
    for data in default:
        setting = Settings()
        setting.name, setting.url, setting.type, setting.is_use, setting.seq, setting.icon = data
        db.session.add(setting)
    # blog名称
    blog_name = raw_input('输入blog名称：')
    setname = Settings()
    setname.name = blog_name
    setname.type = 'blog_name'
    setname.is_use = 1
    db.session.add(setname)
    # 初始化时间
    settdate = Settings()
    settdate.name = str(datetime.now().date())
    settdate.type = 'init_date'
    settdate.is_use = 1
    db.session.add(settdate)
    db.session.commit()


def admin_user():
    email = raw_input('输入管理员邮箱：')
    inp = 1
    while inp == 1:
        pwd1 = raw_input('输入管理员密码：')
        pwd2 = raw_input('确认管理员密码：')
        if pwd1 == pwd2:
            inp = 0
        else:
            print '两次输入的不一样，请重新输入'
            continue
    print '--------------------------------'
    print '输入的管理员邮箱为：%s' % email
    print '输入的管理员密码为：%s' % pwd1
    print '--------------------------------'
    if raw_input('确定（Y）').lower() == 'y':
        pwd = User.make_random_passwd(email=email)
        user = User(email=pwd['email'],
                    role=1,
                    nicename=email,
                    passwd=pwd['pwdmd5'],
                    is_locked=0,
                    salt=pwd['salt'])
        user.register_date = datetime.now(),
        db.session.add(user)
        db.session.commit()
        print '保存设置...[确定]'
    else:
        exit()
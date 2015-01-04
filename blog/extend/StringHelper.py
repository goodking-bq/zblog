#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'

import random
from hashlib import md5, sha1
from base64 import b64encode
from datetime import datetime
from config import ROBOT_VISIT, ATTACK_VISIT
import socket

""" 返回l长度的随机字符串及经过加密的字符串"""

basicstring = '''1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-[]{}/'''
colorstring = '''0123456789ABCDEF'''


def make_random_passwd(l, pwd, email):
    from blog.models import User
    from blog import db

    user = User.query.filter_by(email=email).first()
    if pwd == None:
        pwd = ''.join(random.sample(basicstring, l))
    if user == None:
        salt = ''.join(random.sample(basicstring, 32))
    else:
        salt = user.salt
    pwdmd5 = sha1(salt + pwd).hexdigest()
    for i in range(1, 5):
        pwdmd5 = md5(pwdmd5).hexdigest()
    pwdmd5 = b64encode(pwdmd5)
    return {'pwd': pwd,
            'pwdmd5': pwdmd5,
            'email': email,
            'salt': salt}


def random_color():
    color = ''.join(random.sample(colorstring, 6))
    color = '#' + color
    return color


def get_avatar_url(email, size):
    md5str = md5(email).hexdigest()
    avatar_url = 'https://secure.gravatar.com/avatar/' + md5str + '?d=mm&s=' + str(size)
    return avatar_url


'''返回IP的地理位置'''


def get_ip_location(ip):
    import urllib2
    import json

    try:
        url = 'http://ip.taobao.com/service/getIpInfo.php?ip=' + ip
        js = urllib2.urlopen(url).read()
    except:
        return u'查询接口无法打开'
    s = json.loads(js)
    if not s['code']:
        return s['data']['country'] + s['data']['area'] + s['data']['region'] + s['data']['city'] + s['data']['isp']
    else:
        return u'查询失败'





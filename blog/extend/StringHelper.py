#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'

import random
from hashlib import md5, sha1
from base64 import b64encode
from datetime import datetime

""" 返回l长度的随机字符串及经过加密的字符串"""

basicstring = '''1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-[]{}/'''


def make_random_passwd(l, pwd, email):
    from blog.models import User_salt, User
    from blog import db

    salt = User_salt()
    if pwd == None:
        pwd = ''.join(random.sample(basicstring, l))
    if salt.get_salt(email) == None:
        saltstr = ''.join(random.sample(basicstring, 32))
        salt.email = email
        salt.salt = saltstr
        db.session.add(salt)
        db.session.commit()
    else:
        saltstr = salt.get_salt(email)
    pwdmd5 = sha1(saltstr + pwd).hexdigest()
    for i in range(1, 5):
        pwdmd5 = md5(pwdmd5).hexdigest()
    pwdmd5 = b64encode(pwdmd5)
    return {'pwd': pwd,
            'pwdmd5': pwdmd5,
            'email': email}


def get_avatar_url(email, size):
    md5str = md5(email).hexdigest()
    avatar_url = 'http://www.gravatar.com/avatar/' + md5str + '?d=mm&s=' + str(size)
    return avatar_url


'''返回IP的地理位置'''


def realaddr(ip):
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


#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'
__createday__ = '2014-12-08'

from blog import oauth

weibo = oauth.remote_app(
    'weibo',
    consumer_key='3729199793',
    consumer_secret='e824bd5361f352026cd491f097aa0208',
    request_token_params={'scope': 'email,statuses_to_me_read',
                          'response_type': 'code', },
    base_url='https://api.weibo.com/2/',
    authorize_url='https://api.weibo.com/oauth2/authorize',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.weibo.com/oauth2/access_token',
    # since weibo's response is a shit, we need to force parse the content
    content_type='application/json',
)

qq = oauth.remote_app(
    'qq',
    consumer_key='101174503',
    consumer_secret='b1a34da978ed7f82a9a4c76f3292689c',
    request_token_params={'scope': 'get_user_info,do_like,upload_pic',
                          'client_id': '101174503'},
    base_url='http://graph.qq.com/demo/index.jsp',
    authorize_url='https://graph.qq.com/oauth2.0/authorize',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://graph.qq.com/oauth2.0/token',
    # since weibo's response is a shit, we need to force parse the content
    content_type='application/json'
)
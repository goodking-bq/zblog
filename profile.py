#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'
__createday__ = '2014-12-19'

from werkzeug.contrib.profiler import ProfilerMiddleware

from blog import blog


blog.config['PROFILE'] = True
blog.wsgi_app = ProfilerMiddleware(blog.wsgi_app, restrictions=[30])
blog.run(debug=True)
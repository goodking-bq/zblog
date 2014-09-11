#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'
from flask.ext.admin import Admin,BaseView,expose
from blog import blog
myadmin=Admin(blog)
#base_template='admin/my-master.html'
class MyAdminView(BaseView):
    @expose('/')
    def admin_index(self):
        return self.render('user/index.html')
class AnotherAdminView(BaseView):
    @expose('/')
    def admin_index(self):
        return self.render('user/index.html')
    @expose('/test/')
    def test(self):
        return self.render('user/index.html')

# Create user interface
myadmin.add_view(MyAdminView(category='Test'))
myadmin.add_view(AnotherAdminView(category='Test1'))





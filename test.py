#!flask/bin/python
import os
import unittest

from config import basedir
from blog import blog, db
from blog.models import User


class TestCase(unittest.TestCase):
    def setUp(self):
        blog.config['TESTING'] = True
        blog.config['CSRF_ENABLED'] = False
        blog.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:zoushjde@192.168.137.2/blog_test'
        self.blog = blog.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_avatar(self):
        u = User(nicename='john', email='john@example.com')
        avatar = u.avatar(128)
        expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
        assert avatar[0:len(expected)] == expected

    def test_user_check(self):
        pwd = User.make_random_passwd(email='abc@qq.com')
        user = User(email=pwd['email'],
                    passwd=pwd['pwdmd5'])
        db.session.add(user)
        db.session.commit()
        is_true = User.user_check('abc@qq.com', pwd['pwd'])
        assert is_true != True

if __name__ == '__main__':
    unittest.main()
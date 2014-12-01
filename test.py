#!flask/bin/python
import os
import unittest

from config import basedir
from blog import blog, db
from blog.models import User, Blog_info


class TestUser(unittest.TestCase):
    def setUp(self):
        blog.config['TESTING'] = True
        blog.config['CSRF_ENABLED'] = False
        blog.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = blog.test_client()
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
                    passwd=pwd['pwdmd5'],
                    salt=pwd['salt'])
        db.session.add(user)
        db.session.commit()
        is_true = User.user_check('abc@qq.com', pwd['pwd'])
        assert is_true == True

    def test_new_visit(self):
        old = Blog_info.get_info_by_day('2014-11-27')
        Blog_info.new_visit('2014-11-27')
        new = Blog_info.get_info_by_day('2014-11-27')
        print new.visit_day - old.visit_day
        assert new.visit_day - old.visit_day == 1

    def test(self):
        assert True

if __name__ == '__main__':
    unittest.main()
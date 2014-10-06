# -*- coding:utf-8 -*-
from blog import db, blog
import flask.ext.whooshalchemy as whooshalchemy
from hashlib import md5
from config import ARTICLES_PER_PAGE, RANDOM_PASSWORD_LENGTH
from datetime import datetime

ROLE_USER = 0
ROLE_ADMIN = 1
User_LOCKED = 0
IS_USE = 1


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nicename = db.Column(db.String(64), index=True, unique=True)
    passwd = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    info = db.Column(db.String(140))
    url = db.Column(db.String(100))
    is_locked = db.Column(db.Integer(1), default=User_LOCKED)
    last_seen = db.Column(db.DateTime)
    register_date = db.Column(db.DateTime)
    register_ip = db.Column(db.String(15))

    def is_authenticated(self):
        return True

    def is_active(self):
        if self.is_locked == 0:
            return True
        else:
            return False

    def is_anonymous(self):
        return False

    def is_admin(self):
        if self.role == 1:
            return True
        else:
            return False

    def get_id(self):
        return unicode(self.id)

    @classmethod
    def is_email_use(cls, email):
        user = User.query.filter_by(email=email).first()
        if user:
            return True

    def avatar(self, size):
        md5str = md5(self.email).hexdigest()
        # return 'http://v'+md5str[0]+'.i7avatar.com/'+md5str+'?http://1.gravatar.com/avatar/b1180c028bdb0181eafd3da5a657e0bb?s=44&d=http%3A%2F%2F1.gravatar.com%2Favatar%2Fad516503a11cd5ca435acc9bb6523536%3Fs%3D44&r=G'
        return 'http://www.gravatar.com/avatar/' + md5str + '?d=mm&s=' + str(size)

    def __repr__(self):
        return '<User %r>' % (self.nicename)

    @classmethod
    def user_check(cls, email, passwd):
        pwdmd5 = User.make_random_passwd(passwd, email)['pwdmd5']
        user = User.query.filter_by(email=email, passwd=pwdmd5).first()
        if user:
            return user
        else:
            return False

    @staticmethod
    def make_random_passwd(pwd=None, email=None):
        from blog.extend.StringHelper import make_random_passwd

        pwd = make_random_passwd(RANDOM_PASSWORD_LENGTH, pwd, email)
        return pwd

    @classmethod
    def count_all(cls):
        count = db.session.query(db.func.count(User.id).label('user_all')).first().user_all
        return count


class User_salt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128))
    salt = db.Column(db.String(32))

    @classmethod
    def get_salt(cls, email):
        U = User_salt.query.filter_by(email=email).first()
        if U:
            return U.salt
        else:
            return None


class Article(db.Model):
    __tablename__ = 'article'
    __searchable__ = ['body', 'title']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
    text = db.Column(db.String(4000))
    tag = db.Column(db.String(50))
    post_date = db.Column(db.DateTime)
    is_open = db.Column(db.Integer(1))
    timestamp = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    months = db.Column(db.String(7), default=str(datetime.now())[:7])

    def __init__(self, title, body, text, timestamp, user_id, category_id, tag, is_open):
        self.title = title
        self.body = body
        self.text = text
        self.timestamp = timestamp
        self.user_id = user_id
        self.category_id = category_id
        self.tag = tag
        self.is_open = is_open


    def __repr__(self):
        return '<Article %r>' % (self.title)

    def view_count(self):
        count = db.session.query(Visit_log).filter(Visit_log.visiturl.match(self.title)).count()
        return count

    @classmethod
    def find_by_id(self, id):

        art = self.query.filter_by(id=id).first()
        return art

    @classmethod
    def find_by_name(self, title):
        art = self.query.filter_by(title=title).first()
        return art

    @classmethod
    def article_per_page(cls, name, month, page, pagenum=ARTICLES_PER_PAGE):
        if name == 'all' and month == 'all':
            art = Article.query.filter_by(is_open=1).order_by(Article.timestamp.desc())
            return art.paginate(page, pagenum, False)
        elif month == 'all' and name <> 'all':
            cg = Category.find_by_name(name)
            if cg:
                art = Article.query.filter(Article.category_id == cg.id, Article.is_open == 1).order_by(
                    Article.timestamp.desc())
                return art.paginate(page, pagenum, False)
        elif month <> 'all' and name == 'all':
            art = Article.query.filter(Article.months == month, Article.is_open == 1).order_by(Article.timestamp.desc())
            return art.paginate(page, pagenum, False)
        elif month <> 'all' and name <> 'all':
            cg = Category.find_by_name(name)
            if cg:
                art = Article.query.filter(Article.months == month, Article.category_id == cg.id,
                                           Article.is_open == 1).order_by(
                    Article.timestamp.desc())
                return art.paginate(page, pagenum, False)

    @classmethod
    def article_per_page_all(cls, page, pagenum=ARTICLES_PER_PAGE):
        art = Article.query.all().order_by(Article.timestamp.desc())
        return art.paginate(page, pagenum, False)

    @classmethod
    def count_by_month(cls):
        month_count = db.session.query(Article.months, db.func.count('*').label('num')).group_by(
            Article.months).order_by(Article.months.desc())
        return month_count

    @classmethod
    def count_all(cls):
        count = db.session.query(db.func.count(Article.id).label('article_count')).first().article_count
        return count


whooshalchemy.whoosh_index(blog, Article)

# class comments(db.Model):
#    id=id = db.Column(db.Integer, primary_key=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    createdate = db.Column(db.DateTime)
    articles = db.relationship('Article', backref='category', lazy='dynamic')
    is_use = db.Column(db.Integer(1), default=IS_USE)
    seq = db.Column(db.Integer)

    def __repr__(self):
        return '<Category %r>' % (self.name)

    @classmethod
    def find_by_name(cls, name):
        return Category.query.filter(Category.name == name, Category.is_use == 1).first()

    @classmethod
    def default_seq(cls):
        return db.session.query(db.func.max(Category.seq).label('seq_max')).first().seq_max + 1


class Uploads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(50))
    file_type = db.Column(db.String(4))
    upload_date = db.Column(db.DateTime, default=datetime.now())
    upload_user = db.Column(db.Integer)


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    url = db.Column(db.String(200))
    type = db.Column(db.String(20))
    is_use = db.Column(db.Integer(1), default=1)
    seq = db.Column(db.Integer())
    icon = db.Column(db.String(50))

    @classmethod
    def admin_second_bar(cls):
        list_bar = Settings.query.filter(Settings.type == 'admin_second_bar', Settings.is_use == 1).order_by(
            Settings.seq)
        return list_bar

    @classmethod
    def blog_name(cls):
        blog_name = Settings.query.filter(Settings.type == 'blog_name', Settings.is_use == 1).first()
        return blog_name

    @classmethod
    def first_bar(cls):
        first_bar = Settings.query.filter(Settings.type == 'first_bar', Settings.is_use == 1).order_by(Settings.seq)
        return first_bar


class Visit_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    ipaddr = db.Column(db.String(15))
    visiturl = db.Column(db.String(100))
    year = db.Column(db.String(4), default=str(datetime.now())[:4])
    year_month = db.Column(db.String(7), default=str(datetime.now())[:7])
    year_month_day = db.Column(db.String(10), default=str(datetime.now())[:10])

    @classmethod
    def count_all(cls):
        count = db.session.query(db.func.count(Visit_log.id).label('visit_all')).first().visit_all
        return count

    @classmethod
    def count_by_day(cls):
        count = Visit_log.query.filter(Visit_log.year_month_day == str(datetime.now())[:10]).count()
        return count

    @classmethod
    def count_by_year(cls):
        count = Visit_log.query.filter(Visit_log.year == datetime.now().year).count()
        return count


class Login_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.now())
    ipaddr = db.Column(db.String(15))
    year = db.Column(db.String(4), default=datetime.now().year)
    year_month = db.Column(db.String(7), default=str(datetime.now())[:7])
    year_month_day = db.Column(db.String(10), default=datetime.now().date())

    def __str__(self):
        return self.email

    @classmethod
    def count_all(cls):
        count = db.session.query(db.func.count(Login_log.id).label('login_all')).first().login_all
        return count


class Tj(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visit_all = db.Column(db.Integer)
    visit_day = db.Column(db.Integer)
    visit_month = db.Column(db.Integer)
    visit_year = db.Column(db.Integer)
    article_all = db.Column(db.Integer)
    user_all = db.Column(db.Integer)
    login_all = db.Column(db.Integer)
    nowtimes = db.Column(db.DateTime, default=datetime.now())

    @classmethod
    def tongji(cls):
        tj = Tj()
        tj.visit_all = Visit_log.count_all()
        tj.visit_day = Visit_log.count_by_day()
        tj.article_all = Article.count_all()
        tj.user_all = User.count_all()
        tj.login_all = Login_log.count_all()
        tj.nowtimes = str(datetime.now().time())[:8]
        return tj


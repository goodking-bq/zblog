# -*- coding:utf-8 -*-
from blog import db, blog, cache
import flask.ext.whooshalchemy as whooshalchemy
from hashlib import md5
from config import ARTICLES_PER_PAGE, RANDOM_PASSWORD_LENGTH
from datetime import datetime
from blog.extend.decorators import async
from blog.extend.StringHelper import get_ip_location

ROLE_USER = 0
ROLE_ADMIN = 1
User_LOCKED = 0
IS_USE = 1

'''用户'''


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nicename = db.Column(db.String(64), index=True, unique=True)
    passwd = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    info = db.Column(db.String(140))
    url = db.Column(db.String(100))
    is_locked = db.Column(db.Integer, default=User_LOCKED)
    last_seen = db.Column(db.DateTime)
    register_date = db.Column(db.DateTime)
    register_ip = db.Column(db.String(15))
    salt = db.Column(db.String(32))

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


'''文章类别'''


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True)
    createdate = db.Column(db.DateTime)
    article = db.relationship('Article', backref='category', lazy='dynamic')
    is_use = db.Column(db.Integer, default=IS_USE)
    seq = db.Column(db.Integer)

    def __repr__(self):
        return '<Category %r>' % (self.name)

    @classmethod
    def find_by_name(cls, name):
        return Category.query.filter(Category.name == name, Category.is_use == 1).first()

    @classmethod
    def default_seq(cls):
        return db.session.query(db.func.max(Category.seq).label('seq_max')).first().seq_max + 1

    @classmethod
    def choices(cls):
        choice = [(c.id, c.name) for c in
                  Category.query.filter_by(is_use=1).order_by(Category.seq)]
        return choice
'''文章'''


class Article(db.Model):
    __tablename__ = 'article'
    __searchable__ = ['body', 'title']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True)
    body = db.Column(db.Text)
    text = db.Column(db.String(4000))
    tag = db.Column(db.String(50))
    post_date = db.Column(db.DateTime)
    is_open = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    months = db.Column(db.String(7), default=str(datetime.now())[:7])
    numlook = db.Column(db.Integer)

    def __init__(self, title, body, text, timestamp, user_id, category_id, tag, is_open, numLook=0):
        self.title = title
        self.body = body
        self.text = text
        self.timestamp = timestamp
        self.user_id = user_id
        self.category_id = category_id
        self.tag = tag
        self.is_open = is_open
        self.numlook = numLook

    def __repr__(self):
        return '<Article %r>' % (self.title)

    # 根据ID
    @classmethod
    def find_by_id(self, max_id):
        art = self.query.filter_by(id=max_id).first()
        return art

    # 根据title查找，每次查询numlook+1（排除robot访问）
    @classmethod
    def find_by_name(self, title, agent):
        art = self.query.filter_by(title=title).first_or_404()
        art.numlook += 1
        return art

    # 分类、分月查询
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

    # 所有博文，最后编辑时间倒序
    @classmethod
    def article_all(cls):
        art = Article.query.order_by(Article.timestamp.desc())
        return art

    # 按月统计
    @classmethod
    def count_by_month(cls):
        month_count = db.session.query(Article.months, db.func.count('*').label('num')).group_by(
            Article.months).order_by(Article.months.desc())
        return month_count

    # 当月博文统计
    @classmethod
    def count_current_month(cls):
        current_month = str(datetime.now())[:7]
        count = db.session.query(Article.months, db.func.count('*').label('num')).filter(
            Article.months == current_month).first().num
        return count

    @classmethod
    def find_by_month(cls):
        article = Article.query.filter(Article.is_open == 1).all()
        return article

    # 是否再次经过编辑
    @classmethod
    def find_edit(cls):
        article = Article.query.filter(Article.is_open == 1, Article.post_date <> Article.timestamp).all()
        return article

    # 统计所有博文数量
    @classmethod
    def count_all(cls):
        count = db.session.query(db.func.count(Article.id).label('article_count')).first().article_count
        return count

    # 按类别统计博文数量
    @classmethod
    def count_by_category(cls):
        art = db.session.query(Category.name,
                               db.func.count(Article.id).label('count')).filter(
            Category.id == Article.category_id).group_by(Category.name).all()
        return art

    # top 5
    @classmethod
    def top(cls, num):
        art = db.session.query(Article).order_by(Article.numlook.desc()).limit(num)
        return art

whooshalchemy.whoosh_index(blog, Article)

'''上传附件'''


class Uploads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(50))
    file_url = db.Column(db.String(50))
    use_url = db.Column(db.String(50))
    file_type = db.Column(db.String(4))
    upload_date = db.Column(db.DateTime)
    upload_user = db.Column(db.Integer)

    @classmethod
    def get_imgs(cls):
        imgs = Uploads.query.filter_by(file_type='img').order_by(Uploads.upload_date.desc())
        return imgs

    @classmethod
    def get_atts(cls):
        atts = Uploads.query.filter_by(file_type='att').order_by(Uploads.upload_date.desc())
        return atts


'''设置'''


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    url = db.Column(db.String(200))
    type = db.Column(db.String(20))
    is_use = db.Column(db.Integer, default=1)
    seq = db.Column(db.Integer)
    icon = db.Column(db.String(50))

    @classmethod
    def admin_second_bar(cls):
        list_bar = Settings.query.filter(Settings.type == 'admin_second_bar', Settings.is_use == 1).order_by(
            Settings.seq)
        return list_bar

    @classmethod
    def blog_name(cls):
        blog_name = Settings.query.filter(Settings.type == 'blog_name', Settings.is_use == 1).first()
        if blog_name:
            return blog_name.name
        else:
            return 'zou-blog'


    @classmethod
    def first_bar(cls):
        first_bar = Settings.query.filter(Settings.type == 'first_bar', Settings.is_use == 1).order_by(Settings.seq)
        return first_bar

    @classmethod
    def blog_setting(cls):
        settings = Settings.query.filter(Settings.seq == '', Settings.is_use == 1).all()
        return settings


'''访问日志'''


class Visit_log(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    ip = db.Column(db.String(15))
    url = db.Column(db.String(100))
    agent = db.Column(db.String(500))

    def __repr__(self):
        return '<URL: %r>' % (self.url)

    def __init__(self, timestamp, ip, url, agent):
        self.timestamp = timestamp
        self.ip = ip
        self.url = url
        self.agent = agent

    @classmethod
    def count_all(cls):  # 访问总量
        count = db.session.query(db.func.count(Visit_log.id).label('visit_all')).first().visit_all
        return count

    @classmethod
    def max_id(cls):  #
        return db.session.query(db.func.max(Visit_log.id).label('max_id')).first().max_id


'''登陆日志'''


class Login_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    ip = db.Column(db.String(15))
    address = db.Column(db.String(50))

    def __init__(self, email, ip):
        self.email = email
        self.ip = ip
        self.address = get_ip_location(ip)

    def __str__(self):
        return self.email

    @classmethod
    def count_all(cls):
        count = db.session.query(db.func.count(Login_log.id).label('login_all')).first().login_all
        return count


'''备份日志'''


class Backup_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    finish_time = db.Column(db.DateTime)
    status = db.Column(db.String(10))
    msg = db.Column(db.Text)
    type = db.Column(db.String(10))


'''blog信息汇总'''


class Blog_info(db.Model):
    date = db.Column(db.String(10), primary_key=True, index=True)
    visit_all = db.Column(db.Integer)
    visit_day = db.Column(db.Integer)
    visit_month = db.Column(db.Integer)
    visit_attack = db.Column(db.Integer)
    visit_attack_day = db.Column(db.Integer)
    visit_robot = db.Column(db.Integer)
    visit_robot_day = db.Column(db.Integer)
    article_all = db.Column(db.Integer)
    article_month = db.Column(db.Integer)
    user_all = db.Column(db.Integer)
    login_all = db.Column(db.Integer)


    def __init__(self):
        pass

    def __repr__(self):
        return '<Date: %s>' % self.date

    '''根据日期返回记录,没有就新增'''

    @classmethod
    def get_info_by_day(cls, date):
        info = Blog_info.query.order_by(Blog_info.date.desc()).first()
        if not info:
            info = Blog_info()
            info.date = date
            info.visit_all = 0
            info.visit_day = 0
            info.visit_month = 0
            info.visit_attack = 0
            info.visit_attack_day = 0
            info.visit_robot = 0
            info.visit_robot_day = 0
            info.article_all = 0
            info.article_month = 0
            info.user_all = 0
            info.login_all = 0
            db.session.add(info)
            db.session.commit()
            info = Blog_info.query.filter_by(date=date).first()
        if info.date != date:
            new = Blog_info()
            new.date = date
            new.visit_day = 0
            new.visit_attack_day = 0
            new.visit_robot_day = 0
            new.visit_all = info.visit_all
            new.visit_attack = info.visit_attack
            new.visit_robot = info.visit_robot
            new.article_all = info.article_all
            new.user_all = info.user_all
            new.login_all = info.login_all
            if info.date[5:7] != date[5:7]:
                new.visit_month = 0
                new.article_month = 0
            else:
                new.visit_month = info.visit_month
                new.article_month = info.article_month
            db.session.add(new)
            db.session.commit()
            info = Blog_info.query.filter_by(date=date).first()
        return info


    '''实时信息'''
    @classmethod
    def info(cls):
        old = Blog_info.query.order_by(Blog_info.date.desc()).first()
        old.blog_name = Settings.blog_name()
        return old


    '''正常访问+1'''
    @classmethod
    def new_visit(cls, date):
        info = Blog_info.get_info_by_day(date)
        info.visit_day += 1
        if info.date[5:7] == str(datetime.now().date())[5:7]:
            info.visit_month += 1
        else:
            info.visit_month = 1
        info.visit_all += 1
        db.session.add(info)
        db.session.commit()


    '''机器人访问+1'''
    @classmethod
    def new_robot_visit(cls, date):
        info = Blog_info.get_info_by_day(date)
        info.visit_robot += 1
        info.visit_robot_day += 1
        db.session.add(info)
        db.session.commit()


    '''疑似攻击+1'''

    @classmethod
    def new_attack_visit(cls, date):
        info = Blog_info.get_info_by_day(date)
        info.visit_attack += 1
        info.visit_attack_day += 1
        db.session.add(info)
        db.session.commit()


    '''文章+1'''

    @classmethod
    def new_article(cls):
        old = Blog_info.get_info_by_day(str(datetime.now().date()))
        old.article_all += 1
        old.article_month += 1
        db.session.add(old)
        db.session.commit()


    '''用户+1'''
    @classmethod
    def new_user(cls):
        old = Blog_info.get_info_by_day(str(datetime.now().date()))
        old.user_all += 1
        db.session.add(old)
        db.session.commit()


    '''登陆+1'''
    @classmethod
    def new_login(cls):
        old = Blog_info.get_info_by_day(str(datetime.now().date()))
        old.login_all += 1
        db.session.add(old)
        db.session.commit()


'''ip黑名单'''


class Ip_blacklist(db.Model):
    ip = db.Column(db.String(15), primary_key=True, index=True)
    address = db.Column(db.String(50))
    visit_count = db.Column(db.Integer, default=1)
    attack_count = db.Column(db.Integer, default=1)
    is_forbid = db.Column(db.Integer, default=0)  # 是否禁止访问
    forbid_date = db.Column(db.Integer)  # 禁止日期
    reason = db.Column(db.String(50))  # 原因

    @classmethod
    def find_by_ip(cls, ip):
        ip = Ip_blacklist.query.filter_by(ip=ip).first()
        return ip


class Robot(db.Model):
    ip = db.Column(db.String(15), primary_key=True, index=True)
    name = db.Column(db.String(20))
    dns_name = db.Column(db.String(20))
    address = db.Column(db.String(50))
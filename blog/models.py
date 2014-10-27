# -*- coding:utf-8 -*-
from blog import db, blog
import flask.ext.whooshalchemy as whooshalchemy
from hashlib import md5
from config import ARTICLES_PER_PAGE, RANDOM_PASSWORD_LENGTH
from datetime import datetime
from blog.extend.StringHelper import realaddr, is_robot, is_attack

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


'''用户salt'''


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


'''文章'''


class Article(db.Model):
    __tablename__ = 'article'
    __searchable__ = ['body', 'title']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
    text = db.Column(db.String(4000))
    tag = db.Column(db.String(50))
    post_date = db.Column(db.DateTime)
    is_open = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    months = db.Column(db.String(7), default=str(datetime.now())[:7])
    numLook = db.Column(db.Integer)

    def __init__(self, title, body, text, timestamp, user_id, category_id, tag, is_open, numLook=0):
        self.title = title
        self.body = body
        self.text = text
        self.timestamp = timestamp
        self.user_id = user_id
        self.category_id = category_id
        self.tag = tag
        self.is_open = is_open
        self.numLook = numLook

    def __repr__(self):
        return '<Article %r>' % (self.title)

    def view_count(self, max_id):
        count = db.session.query(Visit_log.id <= max_id).filter(Visit_log.visiturl.like('%' + self.title + '%')
        ).count()
        return count

    @classmethod
    def find_by_id(self, max_id):
        art = self.query.filter_by(id=max_id).first()
        return art

    @classmethod
    def find_by_name(self, title, agent):
        art = self.query.filter_by(title=title).first_or_404()
        if art and not is_robot(agent):
            art.numLook += 1
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
    def article_all(cls):
        art = Article.query.order_by(Article.timestamp.desc())
        return art

    @classmethod
    def count_by_month(cls):
        month_count = db.session.query(Article.months, db.func.count('*').label('num')).group_by(
            Article.months).order_by(Article.months.desc())
        return month_count

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

    @classmethod
    def find_edit(cls):
        article = Article.query.filter(Article.is_open == 1, Article.post_date <> Article.timestamp).all()
        return article

    @classmethod
    def count_all(cls):
        count = db.session.query(db.func.count(Article.id).label('article_count')).first().article_count
        return count


whooshalchemy.whoosh_index(blog, Article)

'''文章类别'''


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    createdate = db.Column(db.DateTime)
    articles = db.relationship('Article', backref='category', lazy='dynamic')
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
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    ipaddr = db.Column(db.String(15))
    visiturl = db.Column(db.String(100))
    year = db.Column(db.String(4), default=str(datetime.now())[:4])
    year_month = db.Column(db.String(7), default=str(datetime.now())[:7])
    year_month_day = db.Column(db.String(10), default=str(datetime.now())[:10])
    real_addr = db.Column(db.String(50))
    agent = db.Column(db.String(500))

    def __repr__(self):
        return '<Article %r>' % (self.visiturl)

    def __init__(self, timestamp, ipaddr, visiturl, agent):
        self.timestamp = timestamp
        self.ipaddr = ipaddr
        self.visiturl = visiturl
        self.year = str(timestamp)[:4]
        self.year_month = str(timestamp)[:7]
        self.year_month_day = str(timestamp)[:10]
        self.real_addr = realaddr(ipaddr)
        self.agent = agent

    @classmethod
    def count_all(cls):  # 访问总量
        count = db.session.query(db.func.count(Visit_log.id).label('visit_all')).first().visit_all
        return count

    @classmethod
    def count_by_day(cls):  # 日访问
        count = Visit_log.query.filter(Visit_log.year_month_day == str(datetime.now())[:10]).count()
        return count

    @classmethod
    def count_by_year(cls):  # 年访问
        count = Visit_log.query.filter(Visit_log.year == datetime.now().year).count()
        return count

    @classmethod
    def count_by_ip(cls, ip):  # ip访问量
        count = Visit_log.query.filter(Visit_log.ipaddr == ip).count()
        return count

    @classmethod
    def count_attack(cls):  # 恶意访问量
        count = Visit_log.query.filter(Visit_log.visiturl.like('%php%')).count()
        return count

    @classmethod
    def ip_attack_count(cls):  # 统计ip的恶意访问次数
        count = db.session.query(Visit_log.ipaddr, Visit_log.real_addr,
                                 db.func.count(Visit_log.ipaddr).label('count')).filter(
            Visit_log.visiturl.like('%php%')).all()
        return count

    @classmethod
    def max_id(cls):  #
        return db.session.query(db.func.max(Visit_log.id).label('max_id')).first().max_id


'''登陆日志'''


class Login_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.now())
    ipaddr = db.Column(db.String(15))
    year = db.Column(db.String(4))
    year_month = db.Column(db.String(7))
    year_month_day = db.Column(db.String(10))
    real_addr = db.Column(db.String(50))

    def __init__(self, email, ipaddr):
        self.email = email
        self.ipaddr = ipaddr
        self.real_addr = realaddr(ipaddr)
        self.year = datetime.now().year
        self.year_month = str(datetime.now())[:7]
        self.year_month_day = datetime.now().date()

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
    id = db.Column(db.Integer, primary_key=True)
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
    date = db.Column(db.String(10))

    def __init__(self):
        pass

    '''最新的一条记录'''

    @classmethod
    def newest_info(cls):
        info = Blog_info.query.order_by(Blog_info.id.desc()).first()
        return info

    '''实时信息'''

    @classmethod
    def info(cls):
        old = Blog_info.newest_info()
        old.blog_name = Settings.blog_name()
        return old

    '''访问+1'''

    @classmethod
    def new_visit(cls, url, agent):
        old = Blog_info.newest_info()
        if old.date == str(datetime.now().date()):
            old.visit_day += 1
            if old.date[5:7] == str(datetime.now().date())[5:7]:
                old.visit_month += 1
            else:
                old.visit_month = 1
            old.visit_all += 1
            if is_attack(url) == 1:
                old.visit_attack += 1
                old.visit_attack_day += 1
            if is_robot(agent):
                old.visit_robot += 1
                old.visit_robot_day += 1
            db.session.add(old)
            db.session.commit()
        else:
            new = Blog_info()
            new.date = str(datetime.now().date())
            new.visit_day = 1
            new.visit_all = old.visit_all + 1
            if old.date[5:7] == str(datetime.now().date())[5:7]:
                new.visit_month = old.visit_month + 1
                new.article_month = old.article_month
            else:
                new.visit_month = 1
                new.article_month = 0
            if is_attack(url) == 1:
                new.visit_attack = old.visit_attack + 1
                new.visit_attack_day = 1
            else:
                new.visit_attack = old.visit_attack
                new.visit_attack_day = 0
            if is_robot(agent):
                new.visit_robot = old.visit_robot + 1
                new.visit_robot_day = 1
            else:
                new.visit_robot = old.visit_robot
                new.visit_robot_day = 0
            new.article_all = old.article_all
            new.login_all = old.login_all
            new.user_all = old.user_all
            db.session.add(new)
            db.session.commit()

    '''文章+1'''

    @classmethod
    def new_article(cls):
        old = Blog_info.newest_info()
        old.article_all += 1
        old.article_month += 1
        db.session.add(old)
        db.session.commit()

    '''用户+1'''

    @classmethod
    def new_user(cls):
        old = Blog_info.newest_info()
        old.user_all += 1
        db.session.add(old)
        db.session.commit()

    '''登陆+1'''

    @classmethod
    def new_login(cls):
        old = Blog_info.newest_info()
        old.login_all += 1
        db.session.add(old)
        db.session.commit()


'''ip黑名单'''


class Ip_blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ipaddr = db.Column(db.String(15))
    real_addr = db.Column(db.String(50))
    visit_count = db.Column(db.Integer)
    attack_count = db.Column(db.Integer)
    is_forbid = db.Column(db.Integer)  # 是否禁止访问
    forbid_date = db.Column(db.Integer)  # 禁止日期

    @classmethod
    def find_by_ip(cls, ip):
        ip = Ip_blacklist.query.filter_by(ipaddr=ip).first()
        return ip


class apscheduler_jobs(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    next_run_time = db.Column(db.Numeric)
    job_state = db.Column(db.BLOB)
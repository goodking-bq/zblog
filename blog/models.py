# -*- coding:utf-8 -*-
from blog import db,blog
import flask.ext.whooshalchemy as whooshalchemy
from hashlib import md5
from config import  ARTICLES_PER_PAGE,RANDOM_PASSWORD_LENGTH
from datetime import  datetime
ROLE_USER=0
ROLE_ADMIN=1



class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    passwd = db.Column(db.String(128))
    email = db.Column(db.String(128),index = True, unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    createdate=db.Column(db.DateTime)
    articles = db.relationship('Article', backref = 'author', lazy = 'dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)    
    register_ip= db.Column(db.String(15))
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)  
    
    def avatar(self, size):
        md5str=md5(self.email).hexdigest()
        #return 'http://v'+md5str[0]+'.i7avatar.com/'+md5str+'?http://1.gravatar.com/avatar/b1180c028bdb0181eafd3da5a657e0bb?s=44&d=http%3A%2F%2F1.gravatar.com%2Favatar%2Fad516503a11cd5ca435acc9bb6523536%3Fs%3D44&r=G'
        return 'http://www.gravatar.com/avatar/' + md5str + '?d=mm&s=' + str(size)    
    
    def __repr__(self):
        return '<User %r>' % (self.nickname)    
        
    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname
    @staticmethod
    def make_random_passwd(pwd=None,email=None):
        from blog.extend.StringHelper import make_random_passwd
        pwd=make_random_passwd(RANDOM_PASSWORD_LENGTH,pwd,email)
        return pwd
    @classmethod
    def count_all(cls):
        count = db.session.query(db.func.count(User.id).label('user_all')).first().user_all
        return count
class User_salt(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(128))
    salt = db.Column(db.String(32))

    @classmethod
    def get_salt(cls,email):
        U=User_salt.query.filter_by(email=email).first()
        if U:
            return  U.salt
        else:
            return  None
class Article(db.Model):
    __tablename__ = 'article'
    __searchable__ = ['body','title']

    id = db.Column(db.Integer, primary_key = True)
    title=db.Column(db.String(100))
    body = db.Column(db.String(4000))
    text = db.Column(db.String(4000))
    create_date = db.Column(db.DateTime )
    timestamp = db.Column(db.DateTime,default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id=db.Column(db.Integer, db.ForeignKey('category.id'))
    months = db.Column(db.String(7))

    def __init__(self,title,body,text,timestamp,user_id,category_id):
        self.title = title
        self.body = body
        self.text = text
        self.timestamp = timestamp
        self.user_id = user_id
        self.category_id = category_id


    def __repr__(self):
        return '<Article %r>' % (self.title)
    
    @classmethod
    def find_by_id(self,id):
        from blog.extend.Ubb2Html import Ubb2Html
        art=self.query.filter_by(id=id).first()
        art.body=Ubb2Html(art.body)
        return art
    @classmethod
    def find_by_name(self,title):
        from blog.extend.Ubb2Html import Ubb2Html
        art=self.query.filter_by(title=title).first()
        art.body=Ubb2Html(art.body)
        return art
    @classmethod
    def article_per_page(cls,name,month,page):
        if name == 'all' and month == 'all':
            art = Article.query.order_by(Article.timestamp.desc())
            return art.paginate(page, ARTICLES_PER_PAGE, False)
        elif month=='all' and name<>'all':
            cg=Category.find_by_name(name)
            if cg:
                art = Article.query.filter_by(category_id=cg.id).order_by(Article.timestamp.desc())
                return art.paginate(page, ARTICLES_PER_PAGE, False)
        elif month<>'all' and name=='all':
            art = Article.query.filter_by(months=month).order_by(Article.timestamp.desc())
            return  art.paginate(page, ARTICLES_PER_PAGE, False)
        elif month<>'all' and name <>'all':
            cg = Category.find_by_name(name)
            if cg:
                art=Article.query.filter(Article.months == month, Article.category_id==cg.id).order_by(Article.timestamp.desc())
                return art.paginate(page, ARTICLES_PER_PAGE, False)
    @classmethod
    def count_by_month(cls):
        month_count = db.session.query(Article.months , db.func.count('*').label('num')).group_by(Article.months).all()
        return month_count
    @classmethod
    def count_all(cls):
        count = db.session.query(db.func.count(Article.id).label('article_count')).first().article_count
        return count
whooshalchemy.whoosh_index(blog,Article)
class Category(db.Model):
    id=db.Column(db.Integer, primary_key = True)
    name=db.Column(db.String(20))
    createdate=db.Column(db.DateTime)
    articles = db.relationship('Article', backref = 'category', lazy = 'dynamic')
    
    def __repr__(self):
        return '<Category %r>' % (self.name)

    @classmethod
    def find_by_name(self,name):
        return self.query.filter_by(name=name).first()
class Visit_log(db.Model):
    id=db.Column(db.Integer, primary_key = True)
    timestamp=db.Column(db.DateTime,default=datetime.now())
    ipaddr=db.Column(db.String(15))
    visiturl=db.Column(db.String(100))
    year=db.Column(db.String(4),default=str(datetime.now())[:4])
    year_month=db.Column(db.String(7),default=str(datetime.now())[:7])
    year_month_day=db.Column(db.String(10),default=str(datetime.now())[:10])

    @classmethod
    def count_all(cls):
        count = db.session.query(db.func.count(Visit_log.id).label('visit_all')).first().visit_all
        return count
    @classmethod
    def count_by_day(cls):
        count=Visit_log.query.filter(Visit_log.year_month_day == str(datetime.now())[:10]).count()
        return count
    @classmethod
    def count_by_year(self):
        return self.timestamp[:4]
class Login_log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime,default=datetime.now())
    ipaddr = db.Column(db.String(15))
    year = db.Column(db.String(4),default=datetime.now().year)
    year_month = db.Column(db.String(7),default=str(datetime.now())[:7])
    year_month_day = db.Column(db.String(10),default=datetime.now().date())

    def __str__(self):
        return self.email
    @classmethod
    def count_all(cls):
        count = db.session.query(db.func.count(Login_log.id).label('login_all')).first().login_all
        return count
class Tj(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    visit_all = db.Column(db.Integer)
    visit_day = db.Column(db.Integer)
    visit_month = db.Column(db.Integer)
    visit_year = db.Column(db.Integer)
    article_all = db.Column(db.Integer)
    user_all = db.Column(db.Integer)
    login_all = db.Column(db.Integer)
    nowtimes = db.Column(db.DateTime,default=datetime.now())

    @classmethod
    def tongji(cls):
        tj=Tj()
        tj.visit_all=Visit_log.count_all()
        tj.visit_day=Visit_log.count_by_day()
        tj.article_all=Article.count_all()
        tj.user_all=User.count_all()
        tj.login_all=Login_log.count_all()
        tj.nowtimes=datetime.now().time()
        return tj


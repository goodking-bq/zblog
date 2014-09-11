# -*- coding:utf-8 -*-

from blog import blog, db, lm, oid
from flask import render_template, flash, redirect , session, url_for, request, g
from forms import LoginForm ,EditForm,RegisterForm,ArticleForm,CategoryForm,SearchForm
from flask.ext.login import login_user, logout_user, current_user, login_required
from models import User, ROLE_USER, ROLE_ADMIN,Article,Category,Visit_log
from datetime import datetime
from flask import copy_current_request_context

@blog.route('/',methods = ['GET', 'POST'])
@blog.route('/index',methods = ['GET', 'POST'])
@blog.route('/index/<string:categoryname>/<string:month>/<int:page>',methods = ['GET', 'POST'])
#@login_required
def index(categoryname='all',month='all',page=1):
    user = g.user
    category=Category.query.all()
    article=Article.article_per_page(categoryname,month,page)
    count=Article.count_by_month()
    return render_template("index.html",
                       title = 'Home',
                       user=user,
                       article=article,
                       category=category,
                       categoryname=categoryname,
                       month=month,
                       count=count)
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('login'))
    form = LoginForm(request.form)
    if form.validate_on_submit() and request.method=='POST':
        pwdmd5=User.make_random_passwd(form.passwd.data,form.email.data)['pwdmd5']
        user = User.query.filter_by(email = form.email.data,passwd=pwdmd5).first()
        if user:
            login_user(user,remember = True)
            flash(u'恭喜，登录成功！')
            return redirect(url_for('index'))
        else:
            flash(u'登录失败')
            return redirect(url_for('login'))
    return render_template('login.html',
        title = 'Sign In',
        form = form)
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
@oid.after_login
def after_login(resp):
    pass

@blog.before_request
def before_request():
    g.search_form = SearchForm()
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.now()
        db.session.add(g.user)
        db.session.commit()
    if request.url.find('static')<0:
        log=Visit_log(timestamp=datetime.now(),
                      ipaddr=request.remote_addr,
                      visiturl=request.url_root)
        db.session.add(log)
        db.session.commit()


def logout():
    logout_user()
    flash(u'已退出登录')
    return redirect(url_for('index'))



@login_required
def user(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    posts = [
        { 'author': user, 'body': 'Test post #1' },
        { 'author': user, 'body': 'Test post #2' }
    ]
    return render_template('user/user.html',
        user = user,
        posts = posts)

@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash(u'已保存修改！')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html',
        form = form)

@blog.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@blog.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

from blog.extend.EmailHelper import register_mail



def register():
    form=RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        pwd=User.make_random_passwd(email=form.email.data)
        user=User(email=pwd['email'],
                  role=ROLE_USER,
                  nickname=form.email.data,
                  passwd=pwd['pwdmd5'],
                  register_ip=request.remote_addr)
        createdate=datetime.now(),
        db.session.add(user)
        db.session.commit()
        user.passwd=pwd['pwd']
        register_mail(user)
        flash(u'恭喜，注册成功！')
        return redirect(url_for('login'))
    return render_template('register.html',
                           title=u'欢迎注册',
                           form=form)

def article_show(title):
    article=Article.find_by_name(title)
    return render_template('article_show.html',
                           article=article)

@login_required
def article_create():
    form=ArticleForm(request.form,g.user.id)
    if request.method=='POST' and form.validate():
        nowtime = datetime.now()
        article=Article(title=form.title.data,
                        body=form.body.data,
                        user_id=g.user.id,
                        category_id=form.category_id.data,
                        text=request.form.get('textformat'),
                        timestamp=nowtime
                        )
        article.create_date=nowtime
        article.months=str(nowtime)[:7]
        db.session.add(article)
        db.session.commit()
        flash(u'文章已创建！')
        return redirect(url_for('index')) 
   
    return render_template('article_create.html',
                           form=form)


@login_required
def article_edit(id):
    form = ArticleForm(request.form)
    article=Article.find_by_id(int(id))
    if form.validate_on_submit():
        article.title=form.title.data
        article.body=form.body.data
        article.text=request.form.get('textformat')
        db.session.add(article)
        db.session.commit()
        flash(u'已保存修改!')
        return redirect(url_for('article_edit',id=id))
    else:
        
        form.title.data=article.title
        form.body.data=article.body
    return render_template('article_create.html',
        form = form)

@login_required
def category_create():
    form=CategoryForm(request.form)
    if request.method=='POST' and form.validate():
        #title=form.title.data
        category=Category(name=form.name.data)
        category.createdate=datetime.now()
        db.session.add(category)
        db.session.commit()
        flash(u'类别已创建！')
        return redirect(url_for('index')) 
    return render_template('category_create.html',
                           form=form)

def search():
    if not g.search_form.validate_on_submit():
        return url_for('index')
    return redirect(url_for('search_result', search=g.search_form.search.data,page=1))

def search_result(search,page=1):
    result = Article.query.whoosh_search(search, 50).all()#order_by(Article.timestamp.desc()).paginate(page, 5, False)
    user = g.user
    if not result:
        return 'aaaaaaa'
    count=Article.count_by_month()
    return render_template("index.html",
                       title = u'搜索:'+search,
                       user=user,
                       article=result,
                       count=count)
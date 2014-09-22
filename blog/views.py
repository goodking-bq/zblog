# -*- coding:utf-8 -*-

from blog import blog, db, lm
from flask import render_template, flash, redirect , session, url_for, request, g
from forms import LoginForm ,UserEditForm,\
                RegisterForm,ArticleCreateForm,\
                ArticleEditForm,CategoryForm,SearchForm,UserChangePwdForm
from flask.ext.login import login_user, logout_user, current_user, login_required
from models import User, ROLE_USER,User_LOCKED,IS_USE,Article,Category,Visit_log,Tj,Login_log
from datetime import datetime
from flask import copy_current_request_context
from blog.extend.Ubb2Html import Ubb2Html

@blog.route('/',methods = ['GET', 'POST'])
@blog.route('/index',methods = ['GET', 'POST'])
@blog.route('/index/<string:categoryname>/<string:month>/<int:page>',methods = ['GET', 'POST'])
def index(categoryname='all',month='all',page=1):
    user = g.user
    category=Category.query.filter_by(is_use=1).order_by(Category.id)
    article=Article.article_per_page(categoryname,month,page)
    count=Article.count_by_month()
    tj = Tj.tongji()
    return render_template("index.html",
                       title = 'Home',
                       user=user,
                       article=article,
                       category=category,
                       categoryname=categoryname,
                       month=month,
                       count=count,
                       tj=tj)
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if form.validate_on_submit() and request.method == 'POST':
        user = User.user_check(passwd=form.passwd.data , email=form.email.data)
        remember_me = form.remember_me.data
        if user:
            login_user(user,remember = remember_me)
            flash(u'恭喜，登录成功！')
            log=Login_log(email=user.email,
                          ipaddr=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            return redirect(request.args.get("next") or url_for("index"))
        else:
            flash(u'用户名或密码错误')
            return redirect(url_for('login'))
    return render_template('login.html',
        title = u'登陆',
        form = form)

@login_required
def logout():
    logout_user()
    flash(u'已退出登录')
    return redirect(url_for('index'))

@blog.before_request
def before_request():
    g.search_form = SearchForm()
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.now()
        db.session.add(g.user)
        db.session.commit()
    if request.url.find('static')<0 and request.url.find('favicon.ico')<0:
        log=Visit_log(timestamp=datetime.now(),
                      ipaddr=request.remote_addr,
                      visiturl=request.base_url)
        db.session.add(log)
        db.session.commit()

@login_required
def user(nicename):
    user = User.query.filter_by(nicename = nicename).first()
    if user == None:
        flash('User ' + nicename + ' not found.')
        return redirect(url_for('index'))
    posts = [
        { 'author': user, 'body': 'Test post #1' },
        { 'author': user, 'body': 'Test post #2' }
    ]
    return render_template('user/user.html',
        user = user,
        posts = posts)

@login_required
def usereditinfo():
    form = UserEditForm()
    pwdform = UserChangePwdForm()
    if form.validate_on_submit() and request.method == 'POST':
        g.user.nicename = form.nicename.data
        g.user.info = form.info.data
        g.user.url = form.url.data
        db.session.add(g.user)
        db.session.commit()
        flash(u'已保存修改！')
        return redirect(url_for('usereditinfo'))
    else:
        form.nicename.data = g.user.nicename
        form.info.data = g.user.info
        form.url.data=g.user.url
    return render_template('user/usereditinfo.html',
        form = form)

def userchangepwd():
    form=UserChangePwdForm()
    if form.validate_on_submit() and request.method == 'POST':
        flash(g.user.email)
        pwd=User.make_random_passwd(pwd=form.password.data,
                                    email=g.user.email)
        g.user.passwd = pwd['pwdmd5']
        db.session.add(g.user)
        db.session.commit()
        flash(u'密码修改成功！')
        return redirect(url_for('usereditinfo'))
    return render_template('user/userchangepwd.html',
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
                  nicename=form.email.data,
                  passwd=pwd['pwdmd5'],
                  is_locked = User_LOCKED,
                  register_ip=request.remote_addr)
        user.register_date=datetime.now(),
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
    form=ArticleCreateForm(request.form,g.user.id)
    if request.method=='POST' and form.validate():
        if not g.user.is_admin():
            flash(u'非管理员不能创建文章！')
            return redirect(url_for('index'))
        else:
            nowtime = datetime.now()
            article=Article(title=form.title.data,
                            body=Ubb2Html(form.body.data),
                            user_id=g.user.id,
                            category_id=form.category_id.data,
                            text=request.form.get('textformat'),
                            timestamp=nowtime
                            )
            article.post_date=nowtime
            db.session.add(article)
            db.session.commit()
            flash(u'文章已创建！')
            return redirect(url_for('index'))
   
    return render_template('article_create.html',
                           form=form)


@login_required
def article_edit(id):
    form = ArticleEditForm(request.form)
    article=Article.find_by_id(int(id))
    if form.validate_on_submit():
        if not g.user.is_admin():
            flash(u'非管理员不能编辑文章！')
            return redirect(url_for('index'))
        else:
            article.title=form.title.data
            article.body=Ubb2Html(form.body.data)
            article.category_id=form.category_id.data
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
        if not g.user.is_admin():
            flash(u'非管理员不能创建类别！')
            return redirect(url_for('index'))
        else:
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
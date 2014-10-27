# -*- coding:utf-8 -*-

from blog import blog, db, lm
from flask import render_template, flash, redirect, session, url_for, request, g
from forms import LoginForm, UserEditForm, \
    RegisterForm, ArticleCreateForm, \
    ArticleEditForm, CategoryForm, SearchForm, UserChangePwdForm, \
    UploadFileForm
from flask.ext.login import login_user, logout_user, current_user, login_required
from models import User, Settings, ROLE_USER, User_LOCKED, IS_USE, Article, Category, Visit_log, Blog_info, Login_log
from datetime import datetime
import json
# from flask import copy_current_request_context
from blog.extend.StringHelper import is_robot, is_attack


@blog.route('/', methods=['GET', 'POST'])
@blog.route('/index', methods=['GET', 'POST'])
@blog.route('/<string:categoryname>/<string:month>/<int:page>', methods=['GET', 'POST'])
def index(categoryname='all', month='all', page=1):
    user = g.user
    category = Category.query.filter_by(is_use=1).order_by(Category.seq)
    article = Article.article_per_page(categoryname, month, page)
    count = Article.count_by_month()
    return render_template("index.html",
                           title='Home',
                           article=article,
                           category=category,
                           categoryname=categoryname,
                           month=month)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if form.validate_on_submit() and request.method == 'POST':
        user = User.user_check(passwd=form.passwd.data, email=form.email.data)
        remember_me = form.remember_me.data
        if user:
            login_user(user, remember=remember_me)
            flash(u'恭喜，登录成功！')
            log = Login_log(email=user.email,
                            ipaddr=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            Blog_info.new_login()
            return redirect(request.args.get("next") or url_for("index"))
        else:
            flash(u'用户名或密码错误')
            return redirect(url_for('login'))
    return render_template('login.html',
                           title=u'请登陆',
                           form=form)


@login_required
def logout():
    logout_user()
    flash(u'已退出登录')
    return redirect(url_for('index'))


@blog.before_request
def before_request():
    g.search_form = SearchForm()
    g.user = current_user
    g.info = Blog_info.info()
    g.first_bar = Settings.first_bar()
    g.count = Article.count_by_month()
    if g.user.is_authenticated():
        g.user.last_seen = datetime.now()
        db.session.add(g.user)
        db.session.commit()
        g.list_bar = Settings.admin_second_bar()
    if request.url.find('static') < 0 and request.url.find('favicon.ico') < 0:
        agent = request.headers['User-Agent']
        url = request.base_url
        Blog_info.new_visit(url=url, agent=agent)
        if is_attack(url):
            log = Visit_log(timestamp=datetime.now(),
                            ipaddr=request.remote_addr,
                            visiturl=url,
                            agent=agent)
            db.session.add(log)
            db.session.commit()
        elif not is_robot(agent):
            log = Visit_log(timestamp=datetime.now(),
                            ipaddr=request.remote_addr,
                            visiturl=url,
                            agent=agent)
            db.session.add(log)
            db.session.commit()


@login_required
def usereditinfo():
    form = UserEditForm()
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
        form.url.data = g.user.url
    return render_template('user/usereditinfo.html',
                           title=u'修改用户信息',
                           form=form)


def userchangepwd():
    form = UserChangePwdForm()
    if form.validate_on_submit() and request.method == 'POST':
        flash(g.user.email)
        pwd = User.make_random_passwd(pwd=form.password.data,
                                      email=g.user.email)
        g.user.passwd = pwd['pwdmd5']
        db.session.add(g.user)
        db.session.commit()
        flash(u'密码修改成功！')
        return redirect(url_for('usereditinfo'))
    return render_template('user/userchangepwd.html',
                           title=u'修改密码',
                           form=form)


@blog.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@blog.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


from blog.extend.EmailHelper import register_mail


def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        pwd = User.make_random_passwd(email=form.email.data)
        user = User(email=pwd['email'],
                    role=ROLE_USER,
                    nicename=form.email.data,
                    passwd=pwd['pwdmd5'],
                    is_locked=User_LOCKED,
                    register_ip=request.remote_addr)
        user.register_date = datetime.now(),
        db.session.add(user)
        db.session.commit()
        user.passwd = pwd['pwd']
        register_mail(user)
        flash(u'恭喜，注册成功！')
        Blog_info.new_user()
        return redirect(url_for('login'))
    return render_template('register.html',
                           title=u'欢迎注册',
                           form=form)


@blog.route('/<string:title>')
# @blog.route('/article_show/<string:title>')
def article_show(title):
    article = Article.find_by_name(title, request.headers['User-Agent'])
    return render_template('article_show.html',
                           title=title,
                           article=article)


@login_required
def article_create():
    form = ArticleCreateForm(request.form, g.user.id)
    if request.method == 'POST' and form.validate():
        if not g.user.is_admin():
            flash(u'非管理员不能创建文章！')
            return redirect(url_for('index'))
        else:
            nowtime = datetime.now()
            article = Article(title=form.title.data,
                              body=form.body.data,
                              user_id=g.user.id,
                              category_id=form.category_id.data,
                              text=request.form.get('textformat'),
                              timestamp=nowtime,
                              tag=form.tag.data,
                              is_open=form.is_open.data
            )
            article.post_date = nowtime
            db.session.add(article)
            db.session.commit()
            flash(u'文章已创建！')
            Blog_info.new_article()
            return redirect(url_for('index'))
    return render_template('article_create.html',
                           title=u'创建文章',
                           form=form)


@login_required
def article_edit(id):
    form = ArticleEditForm(request.form)
    article = Article.find_by_id(int(id))
    if form.validate_on_submit():
        if not g.user.is_admin():
            flash(u'非管理员不能编辑文章！')
            return redirect(url_for('index'))
        else:
            article.title = form.title.data
            article.body = form.body.data
            article.category_id = form.category_id.data
            article.tag = form.tag.data
            article.text = request.form.get('textformat')
            article.is_open = form.is_open.data
            article.timestamp = datetime.now()
            db.session.add(article)
            db.session.commit()
            flash(u'已保存修改!')
            return redirect(url_for('article_edit', id=id))
    else:
        form.title.data = article.title
        form.body.data = article.body
        form.tag.data = article.tag
        form.category_id.data = article.category_id
        form.is_open.data = article.is_open
    return render_template('article_create.html',
                           title=u'编辑' + article.title,
                           form=form)


def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_result', search=g.search_form.search.data, page=1))


def search_result(search, page=1):
    result = Article.query.whoosh_search(search
    ).order_by(Article.timestamp.desc()).paginate(page, 5, False)
    return render_template("index.html",
                           title=u'搜索:' + search,
                           article=result)


def blog_msg():
    return render_template('blog_msg.html')


def blog_about():
    return render_template('blog_about.html')


def blog_calendar():
    return render_template('blog_calendor.html')


def calendar_json():
    create_article = Article.find_by_month()
    update_article = Article.find_edit()
    data = []
    for a in create_article:
        dic = {
            'title': u'新增文章' + a.title,
            'url': '/article_show/' + a.title,
            'start': str(a.post_date)
        }
        data.append(dic)
    for a in update_article:
        dic = {
            'title': u'更新文章' + a.title,
            'url': '/article_show/' + a.title,
            'start': str(a.timestamp)
        }
        data.append(dic)
    return json.dumps(data)


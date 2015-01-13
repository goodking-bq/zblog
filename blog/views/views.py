# -*- coding:utf-8 -*-

import datetime

from flask import render_template, flash, redirect, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask import json, session
from flask.ext.themes import render_theme_template

from blog import blog, db, lm, cache, csrf
from blog.forms import LoginForm, UserEditForm, \
    RegisterForm, ArticleCreateForm, \
    ArticleEditForm, SearchForm, UserChangePwdForm
from blog.models import User, Settings, ROLE_USER, User_LOCKED, Article, Category, Visit_log, Blog_info, Login_log

'''主题渲染'''


def render(template, **context):
    theme = session.get('theme', blog.config['DEFAULT_THEME'])
    print theme
    return render_theme_template(theme, template, **context)


def index(categoryname='all', month='all', page=1):
    category = Category.query.filter_by(is_use=1).order_by(Category.seq)
    article = Article.article_per_page(categoryname, month, page)
    return render("index.html",
                  title='Home',
                  article=article,
                  category=category,
                  categoryname=categoryname,
                  month=month)


@lm.user_loader
def load_user(uid):
    return User.query.get(int(uid))


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
                            ip=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            Blog_info.new_login()
            return redirect(request.args.get("next") or url_for("index"))
        else:
            flash(u'用户名或密码错误')
            return redirect(url_for('login'))
    return render('login.html',
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
    g.top_five = Article.top(10)
    if g.user.is_authenticated():
        g.user.last_seen = datetime.datetime.now()
        db.session.add(g.user)
        db.session.commit()
        g.list_bar = Settings.admin_second_bar()
    if request.url.find('static') < 0 and request.url.find('favicon.ico') < 0:
        agent = request.headers['User-Agent']
        url = request.base_url
        log = Visit_log(timestamp=datetime.datetime.now(),
                        ip=request.remote_addr,
                        url=url,
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


@csrf.error_handler
def csrf_error(reason):
    return render_template('csrf_error.html', reason=reason), 400


@blog.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


def register():
    from blog.extend.EmailHelper import register_mail

    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        pwd = User.make_random_passwd(email=form.email.data)
        user = User(email=pwd['email'],
                    role=ROLE_USER,
                    nicename=form.email.data,
                    passwd=pwd['pwdmd5'],
                    is_locked=User_LOCKED,
                    register_ip=request.remote_addr,
                    salt=pwd['salt'])
        user.register_date = datetime.datetime.now(),
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
@cache.cached(timeout=10)
def article_show(title):
    article = Article.find_by_name(title, request.headers['User-Agent'])
    return render_template('article_show.html',
                           title=title,
                           article=article)


@csrf.exempt
@login_required
def article_create():
    form = ArticleCreateForm()
    form.category_id.choices = Category.choices()
    if request.method == 'POST' and form.validate():
        if not g.user.is_admin():
            flash(u'非管理员不能创建文章！')
            return redirect(url_for('index'))
        else:
            nowtime = datetime.datetime.now()
            article = Article(title=form.title.data,
                              body=form.body.data,
                              user_id=g.user.id,
                              category_id=form.category_id.data,
                              text=request.form.get('textformat'),
                              timestamp=nowtime,
                              tag=form.tag.data,
                              is_open=form.is_open.data)
            article.post_date = nowtime
            db.session.add(article)
            db.session.commit()
            flash(u'文章已创建！')
            Blog_info.new_article()
            return redirect(url_for('article_edit', id=article.id))
    return render_template('article_create.html',
                           title=u'创建文章',
                           form=form)


@login_required
def article_edit(id):
    form = ArticleEditForm()
    form.category_id.choices = Category.choices()
    article = Article.find_by_id(int(id))
    form.title.data = article.title
    form.body.data = article.body
    form.tag.data = article.tag
    form.category_id.data = article.category_id
    form.is_open.data = article.is_open
    form.id.data = id
    return render_template('article_edit.html',
                           title=u'编辑' + article.title,
                           form=form)


@csrf.exempt
@login_required
def article_commit():
    if g.user.is_admin():
        data = request.form
        title, category, tag, is_open, body, text, art_id = data['title'], data['category'], data['tag'], \
                                                            data['open'], data['body'], data['text'], data["id"]
        if title == '' or tag == '' or body == '' or text == '':
            return json.dumps({'msg': u'必填字段不能为空'})
        if art_id:
            article = Article.find_by_id(int(id))
            article.title = title
            article.category_id = category
            article.tag = tag
            article.is_open = is_open
            article.body = body
            article.text = text
            article.timestamp = datetime.datetime.now()
            db.session.add(article)
        else:
            nowtime = datetime.datetime.now()
            article = Article(title=title,
                              body=body,
                              user_id=g.user.id,
                              category_id=category,
                              text=text,
                              timestamp=nowtime,
                              tag=tag,
                              is_open=is_open)
            article.post_date = nowtime
        try:
            db.session.add(article)
            db.session.commit()
            return json.dumps({'msg': u'保存成功'})
        except:
            return json.dumps({'msg': u'保存失败'})
    else:
        return json.dumps({'msg': u'请用管理员账号登陆'})


def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_result', sch=g.search_form.search.data, page=1))


def search_result(sch, page=1):
    try:
        result = Article.search(st=sch, page=page, num=5)
    except:
        result = None
    return render_template("search_result.html",
                           title=u'搜索:' + sch,
                           search=sch,
                           article=result)


def blog_msg():
    return render_template('blog_msg.html')


# @cache.cached(unless=True)
def blog_about():
    return render_theme_template('default', 'blog_about.html')


def visit_json():
    today = datetime.datetime.now().date()
    visits = dict()
    labels = list()
    visit = list()
    attack = list()
    robot = list()
    real = list()
    redata = Blog_info.query.order_by(Blog_info.date.desc()).limit(15)
    for d in redata:
        visit.append(str(d.visit_day))
        attack.append(str(d.visit_attack_day))
        labels.append(str(d.date)[5:])
        robot.append(str(d.visit_robot_day))
        real.append(str(d.visit_day - d.visit_attack_day - d.visit_robot_day))
    labels.reverse()
    attack.reverse()
    visit.reverse()
    robot.reverse()
    real.reverse()
    for i in range(20 - len(visit)):
        de = datetime.timedelta(days=i + 1)
        labels.append(str(today + de)[5:])
    visits['labels'] = labels
    visits['visit'] = visit
    visits['attack'] = attack
    visits['robot'] = robot
    visits['real'] = real
    return json.dumps(visits)


def article_json():
    article = dict()
    art = Article.count_by_category()
    labels = list()
    datas = list()
    for a in art:
        labels.append(a.name)
        d = {
            'value': a.count,
            'name': a.name
        }
        datas.append(d)
    article['labels'] = labels
    article['datas'] = datas
    return json.dumps(article)


@cache.cached(unless=True)
def blog_calendar():
    return render_template('blog_calendor.html')


@cache.memoize(unless=True, timeout=60)
def calendar_json():
    arg = request.args
    start, stop = arg['start'], arg['end']
    create_article = Article.query.filter(Article.post_date >= start).filter(Article.post_date <= stop).all()
    update_article = Article.find_edit(start, stop)
    visit = Blog_info.query.all()
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
            'url': '/' + a.title,
            'start': str(a.timestamp)
        }
        data.append(dic)
    for v in visit:
        dic = {
            'title': u'日访问量:' + str(v.visit_day),
            'start': str(v.date)
        }
        data.append(dic)
    return json.dumps(data)


@blog.route('/theme')
def theme():
    from flask.ext.themes import get_themes_list

    l = get_themes_list()
    n = ' '
    print l[1].name
    for a in l:
        n.join(a.name)
    return l[1].name
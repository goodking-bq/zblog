#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'

from blog import blog, db, lm
from flask import render_template, flash, redirect, session, url_for, request, g
from blog.models import User, Category, Article, Settings, Uploads
from blog.forms import AdminUserEditForm, CategoryForm, CategoryeditForm, Admin_second_barForm
from datetime import datetime
from flask.ext.login import login_required


@login_required
def index1():
    if g.user.is_admin():
        flash(u'管理员登入')
    else:
        flash(u'普通权限登陆，不能更改任何东西')
    return render_template('admin/index.html')


@login_required
def users():
    if g.user.is_admin():
        users = User.query.all()
        return render_template('admin/users.html', users=users)
    else:
        flash(u'无权限访问')
        return redirect(url_for('index1'))


@login_required
def useredit(id):
    if g.user.is_admin():
        form = AdminUserEditForm()
        user = User.query.get(int(id))
        if form.validate_on_submit() and request.method == 'POST' and g.user.is_admin():
            user.is_locked = form.is_locked.data
            user.role = form.role.data
            db.session.add(user)
            db.session.commit()
            flash(u'已保存修改！')
            return redirect(url_for('users'))
        else:
            form.is_locked.data = user.is_locked
            form.role.data = user.role
        return render_template('admin/useredit.html',
                               form=form, user=user)
    else:
        flash(u'无权限访问')
        return redirect(url_for('index1'))


@login_required
def userdelete(id):
    if g.user.is_admin():
        user = User.query.get(int(id))
        db.session.delete(user)
        db.session.commit()
        flash(u'删除成功！')
        return redirect(url_for('users'))
    else:
        flash(u'无权限访问')
        return redirect(url_for('index1'))


@login_required
def category():
    category = Category.query.all()
    return render_template('admin/category.html', category=category)


@login_required
def categorycreate():
    if g.user.is_admin():
        form = CategoryForm(request.form)
        if request.method == 'POST' and form.validate():
            if not g.user.is_admin():
                flash(u'非管理员不能创建类别！')
                return redirect(url_for('category'))
            else:
                category = Category(name=form.name.data)
                category.createdate = datetime.now()
                if form.seq.data == None:
                    category.seq = Category.default_seq()
                else:
                    category.seq = form.seq.data
                db.session.add(category)
                db.session.commit()
                flash(u'类别已创建！')
                return redirect(url_for('category'))
        return render_template('admin/categoryedit.html',
                               form=form)
    else:
        flash(u'无权限访问')
        return redirect(url_for('index1'))


@login_required
def categoryedit(id):
    form = CategoryeditForm()
    category = Category.query.get(int(id))
    if form.validate() and request.method == 'POST':
        if g.user.is_admin():
            category.name = form.name.data
            category.is_use = form.is_use.data
            category.seq = form.seq.data
            db.session.add(category)
            db.session.commit()
            flash(u'已保存修改！')
            return redirect(url_for('category'))
        else:
            return redirect(url_for('index1'))
    else:
        form.name.data = category.name
        form.is_use.data = category.is_use
        form.seq.data = category.seq
    return render_template('admin/categoryedit.html', form=form)


@login_required
def categorydelete(id):
    if g.user.is_admin():
        c = Category.query.get(int(id))
        db.session.delete(c)
        db.session.commit()
        flash(u'删除成功！')
        return redirect(url_for('category'))
    else:
        return redirect(url_for('index1'))


@login_required
def article():
    article = Article.article_all()
    return render_template('admin/article.html', article=article)


@login_required
def articledelete(id):
    if g.user.is_admin():
        article = Article.query.get(int(id))
        db.session.delete(article)
        db.session.commit()
        flash(u'删除成功！')
        return redirect(url_for('article'))
    else:
        return redirect(url_for('index1'))


@login_required
def admin_second_bar():
    bar = Settings.admin_second_bar()
    return render_template('admin/admin_second_bar.html', bar=bar)


@login_required
def admin_second_baredit(id):
    form = Admin_second_barForm()
    bar = Settings.query.get(int(id))
    if form.validate() and request.method == 'POST':
        if g.user.is_admin():
            bar.name = form.name.data
            bar.is_use = form.is_use.data
            bar.seq = form.seq.data
            bar.icon = form.icon.data
            bar.url = form.url.data
            db.session.add(bar)
            db.session.commit()
            flash(u'已保存修改！')
            return redirect(url_for('admin_second_bar'))
        else:
            return redirect(url_for('index1'))
    else:
        form.name.data = bar.name
        form.is_use.data = bar.is_use
        form.seq.data = bar.seq
        form.url.data = bar.url
        form.icon.data = bar.icon
    return render_template('admin/admin_second_baredit.html', form=form)


@login_required
def settings():
    form = Admin_second_barForm()
    bar = Settings.query.get(int(id))
    if form.validate() and request.method == 'POST':
        bar.name = form.name.data
        bar.is_use = form.is_use.data
        bar.seq = form.seq.data
        bar.icon = form.icon.data
        bar.url = form.url.data
        db.session.add(bar)
        db.session.commit()
        flash(u'已保存修改！')
        return redirect(url_for('admin_second_bar'))
    else:
        form.name.data = bar.name
        form.is_use.data = bar.is_use
        form.seq.data = bar.seq
        form.url.data = bar.url
        form.icon.data = bar.icon
    return render_template('admin/admin_second_baredit.html', form=form)


@login_required
def imgs():
    if g.user.is_admin():
        imgs = Uploads.get_imgs()
        return render_template('admin/imgs.html', imgs=imgs)
    else:
        return redirect(url_for('index1'))


@login_required
def atts():
    if g.user.is_admin():
        atts = Uploads.get_atts()
        return render_template('admin/atts.html', atts=atts)
    else:
        return redirect(url_for('index1'))

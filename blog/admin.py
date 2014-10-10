#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'

from blog import blog, db, lm
from flask import render_template, flash, redirect, session, url_for, request, g
from blog.models import User, Category, Article
from blog.forms import AdminUserEditForm, CategoryForm, CategoryeditForm
from datetime import datetime
from flask.ext.login import login_required


@login_required
def index1():
    if g.user.is_admin():
        return render_template('admin/index.html')
    else:
        flash(u'无权限访问')
        return redirect(url_for('index'))


@login_required
def users():
    if g.user.is_admin():
        users = User.query.all()
        return render_template('admin/users.html', users=users)
    else:
        flash(u'无权限访问')
        return redirect(url_for('index'))


@login_required
def useredit(id):
    if g.user.is_admin():
        form = AdminUserEditForm()
        user = User.query.get(int(id))
        if form.validate_on_submit() and request.method == 'POST':
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
        return redirect(url_for('index'))


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
        return redirect(url_for('index'))


@login_required
def category():
    if g.user.is_admin():
        category = Category.query.all()
        return render_template('admin/category.html', category=category)
    else:
        flash(u'无权限访问')
        return redirect(url_for('index'))


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
        return redirect(url_for('index'))


@login_required
def categoryedit(id):
    if g.user.is_admin():
        form = CategoryeditForm()
        category = Category.query.get(int(id))
        if form.validate() and request.method == 'POST':
            category.name = form.name.data
            category.is_use = form.is_use.data
            category.seq = form.seq.data
            db.session.add(category)
            db.session.commit()
            flash(u'已保存修改！')
            return redirect(url_for('category'))
        else:
            form.name.data = category.name
            form.is_use.data = category.is_use
            form.seq.data = category.seq
        return render_template('admin/categoryedit.html', form=form)
    else:
        flash(u'无权限访问')
        return redirect(url_for('index'))


@login_required
def categorydelete(id):
    if g.user.is_admin():
        c = Category.query.get(int(id))
        db.session.delete(c)
        db.session.commit()
        flash(u'删除成功！')
        return redirect(url_for('category'))
    else:
        flash(u'无权限访问')
        return redirect(url_for('index'))


@login_required
def article():
    article = Article.article_per_page('all', 'all', 1, 10)
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
        flash(u'无权限访问')
        return redirect(url_for('index'))


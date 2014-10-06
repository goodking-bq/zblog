#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'

from blog import blog, db, lm
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from blog.models import User, Category, Article
from blog.forms import UserEditForm, CategoryForm,CategoryeditForm
from datetime import  datetime

def index1():
    return render_template('admin/index.html')


def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)


def useredit(id):
    form = UserEditForm()
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


def userdelete(id):
    user = User.query.get(int(id))
    db.session.delete(user)
    db.session.commit()
    flash(u'删除成功！')
    return redirect(url_for('users'))


def category():
    category = Category.query.all()
    return render_template('admin/category.html', category=category)

def categorycreate():
    form=CategoryForm(request.form)
    if request.method=='POST' and form.validate():
        if not g.user.is_admin():
            flash(u'非管理员不能创建类别！')
            return redirect(url_for('category'))
        else:
            category=Category(name=form.name.data)
            category.createdate=datetime.now()
            if form.seq.data ==None:
                category.seq=Category.default_seq()
            else:
                category.seq=form.seq.data
            db.session.add(category)
            db.session.commit()
            flash(u'类别已创建！')
            return redirect(url_for('category'))
    return render_template('admin/categoryedit.html',
                           form=form)
def categoryedit(id):
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

def categorydelete(id):
    c = Category.query.get(int(id))
    db.session.delete(c)
    db.session.commit()
    flash(u'删除成功！')
    return redirect(url_for('category'))

def article():
    article = Article.article_per_page('all', 'all', 1, 10)
    return render_template('admin/article.html', article=article)


def articledelete(id):
    article = Article.query.get(int(id))
    db.session.delete(article)
    db.session.commit()
    flash(u'删除成功！')
    return redirect(url_for('article'))



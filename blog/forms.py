# -*- coding:utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, PasswordField, SelectField
from wtforms.validators import Required, Length, Email, EqualTo
from flask_wtf.file import  FileRequired,FileAllowed,FileField
from blog.models import User, Article, Category


class LoginForm(Form):
    email = TextField('email', validators=[Required(u'不能为空')])
    passwd = PasswordField('passwd', validators=[Required(u'不能为空')])
    remember_me = BooleanField('remember_me', default=False)


class UserEditForm(Form):
    nicename = TextField('nicename')
    info = TextAreaField('info', validators=[Length(min=0, max=140)])
    url = TextField('url', validators=[Length(min=0, max=100)])
    role = SelectField('role',choices=[(0,u'普通用户'),(1,u'管理员')],coerce=int)
    is_locked = SelectField('is_locked',choices=[(0,u'不锁定'),(1,u'锁定')],coerce=int)

class UserChangePwdForm(Form):
    password = PasswordField('New Password', [Required(), EqualTo('confirm', message=u'输入不匹配')])
    confirm = PasswordField('Repeat Password')

class RegisterForm(Form):
    email = TextField('Email Address', [Email(u'请输入正确的Email地址！')])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user != None:
            self.email.errors.append(u'此邮箱已被注册，请直接登录或更换邮箱！')
            return False
        return True

        # #######################################################################


class ArticleCreateForm(Form):
    title = TextField('article title', [Required(u'请输入标题！')])
    body = TextAreaField('article body',
                         [Required(u'文章内容不能为空！')], id='mceEditor')
    category_id = SelectField('category id',
                              choices=[(c.id, c.name) for c in Category.query.filter_by(is_use=1).order_by(Category.seq)],
                              coerce=int)
    tag = TextField('tag',[Length(max=20)])
    is_open = SelectField('is_open',choices=[(0,u'不公开'),(1,u'公开')],coerce=int)
    def validate(self):
        if not Form.validate(self):
            return False
        category = Article.query.filter_by(title=self.title.data).first()
        if category != None:
            self.title.errors.append(u'文章标题不能重复！')
            return False
        return True


class ArticleEditForm(Form):
    title = TextField('article title', [Required(u'请输入标题！')])
    body = TextAreaField('article body',
                         [Required(u'文章内容不能为空！')], id='mceEditor')
    category_id = SelectField('category id',
                              choices=[(c.id, c.name) for c in Category.query.filter_by(is_use=1).order_by(Category.seq)],
                              coerce=int)
    tag = TextField('tag',[Length(max=20)])
    is_open = SelectField('is_open',choices=[(0,u'不公开'),(1,u'公开')],coerce=int)
class CategoryForm(Form):
    name = TextField('category name', [Required(u'请输入类别名！')])
    is_use = SelectField('is_use',choices=[(0,u'停用'),(1,u'在用')],coerce=int)
    seq = TextField('seq')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        category = Category.query.filter_by(name=self.name.data).first()
        if category != None:
            self.name.errors.append(u'类别名不能重复！')
            return False
        return True

class CategoryeditForm(Form):
    name = TextField('category name', [Required(u'请输入类别名！')])
    is_use = SelectField('is_use',choices=[(0,u'停用'),(1,u'在用')],coerce=int)
    seq = TextField('seq')

class SearchForm(Form):
    search = TextField('search', validators=[Required()])

class UploadFileForm(Form):
    file = FileField('file', [FileRequired(),
                             FileAllowed(['txt','pdf','png','jpg','jpeg','gif','rar','zip','tar'])], id='uploader')
     
     
          
    
     
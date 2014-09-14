# -*- coding:utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, BooleanField,TextAreaField,PasswordField,SelectField
from wtforms.validators import Required,Length,Email
from blog.models import User,Article,Category

class LoginForm(Form):
    email = TextField('email', validators = [Required(u'不能为空')],id = 'emailipt')
    passwd=PasswordField('passwd',validators = [Required(u'不能为空')],id = 'passwdipt')
    remember_me = BooleanField('remember_me', default = False)



class EditForm(Form):
     nickname = TextField('nickname', validators = [Required()])
     about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 140)])

     def __init__(self, original_nickname, *args, **kwargs):
          Form.__init__(self, *args, **kwargs)
          self.original_nickname = original_nickname

     def validate(self):
          if not Form.validate(self):
               return False
          if self.nickname.data == self.original_nickname:
               return True
          user = User.query.filter_by(nickname = self.nickname.data).first()
          if user != None:
               self.nickname.errors.append('This nickname is already in use. Please choose another one.')
               return False
          return True
     
class RegisterForm(Form):
     email=TextField('Email Address',[Email(u'请输入正确的Email地址！')])
     
     def __init__(self, *args, **kwargs):
               Form.__init__(self, *args, **kwargs)
     
     def validate(self):
          if not Form.validate(self):
               return False
          user = User.query.filter_by(email = self.email.data).first()
          if user != None:
               self.email.errors.append(u'此邮箱已被注册，请直接登录或更换邮箱！')
               return False
          return True     
########################################################################
class ArticleForm(Form):
     title = TextField('article title',[Required(u'请输入标题！')])
     body = TextAreaField('article body',
                        [Required(u'文章内容不能为空！'),Length(min = 0, max = 4000)],id='mceEditor')
     category_id = SelectField('category id',
                             choices=[(c.id,c.name) for c in Category.query.order_by(Category.id)],
                             coerce=int)
     '''def validate(self):
          if not Form.validate(self):
               return False
          category = Article.query.filter_by(title = self.title.data).first()
          if category != None:
               self.title.errors.append(u'文章标题不能重复！')
               return False
          return True'''
class CategoryForm(Form):
     name=TextField('category name',[Required(u'请输入类别名！')])
     
     def __init__(self, *args, **kwargs):
          Form.__init__(self, *args, **kwargs)
          
     def validate(self):
          if not Form.validate(self):
               return False
          category = Category.query.filter_by(name = self.name.data).first()
          if category != None:
               self.name.errors.append(u'类别名不能重复！')
               return False
          return True  
     
class SearchForm(Form):
    search = TextField('search', validators = [Required()])
     
     
          
    
     
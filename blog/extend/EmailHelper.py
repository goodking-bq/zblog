# -*- coding:utf-8 -*-
from flask.ext.mail import Message
from blog import mymail,blog
from threading import Thread
from flask import copy_current_request_context
from decorators import async
@async 
def send_async_email(msg): 
    with blog.app_context():
        mymail.send(msg) 

def send_email(subject, sender, recipients,  html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.html = html_body
    thr = Thread(target = send_async_email, args = [msg])
    thr.start()
    
from flask import render_template
from config import ADMINS

  
def register_mail(user):
    send_email(u"恭喜! %s 成功注册我的博客。" % user.email,
        ADMINS[0],
        [user.email],
        render_template("register_email.html",
            user = user))
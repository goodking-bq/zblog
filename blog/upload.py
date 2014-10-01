#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'

from werkzeug.utils import secure_filename
from flask import  request,redirect,url_for,render_template,send_from_directory
from config import ALLOWED_EXTENSIONS,UPLOAD_FOLDER
import json
#import os
from blog.forms import UploadFileForm
#from blog import  blog

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def upload():
    if request.method=='POST':
        file = request.files.get('imgFile', None)
        if file and allowed_file(file.filename):
            filename=secure_filename(file.filename)
            try:
                file.save(UPLOAD_FOLDER+'/'+filename)
                url = "/uploads/"+filename
                data = {'error': 0, 'url': url}
                return json.dumps(data)
            except Exception,e:
                date = {'error':1,'message':'Exception:%s' % Exception+':'+e}
                return json.dumps(data)
    return 'FAIL!'

def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

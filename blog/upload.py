#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'

from blog import db, lm
from werkzeug.utils import secure_filename
from flask import request, send_from_directory, g, flash, redirect, url_for
from flask.ext.login import login_required
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
import json
from datetime import datetime
from time import time
from blog.models import Uploads
# import os
from blog.forms import UploadFileForm
# from blog import  blog
img = ['bmp', 'jpg', 'png', 'gif', 'jpeg']
file = ['txt', 'rar', 'zip', 'tar', 'word', 'xsl', 'xsls']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@login_required
def upload():
    if request.method == 'POST':
        datestr = str(int(time()))
        file = request.files.get('imgFile', None)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            fileType = filename.split('.')[-1]
            if fileType in img:
                savename = 'img' + datestr + '.' + fileType
                fileurl = '/img/' + savename
                fileType = 'img'
            else:
                savename = 'att' + datestr + '.' + fileType
                fileurl = '/att/' + savename
                fileType = 'att'
            try:
                file.save(UPLOAD_FOLDER + fileurl)
                url = "/uploads/" + savename
                upd = Uploads(file_name=savename,
                              file_url=fileurl,
                              use_url=request.base_url,
                              file_type=fileType,
                              upload_user=g.user.id)
                upd.upload_date = datetime.now()
                db.session.add(upd)
                db.session.commit()
                data = {'error': 0, 'url': url}
                return json.dumps(data)
            except Exception, ex:
                data = {'error': 1, 'message': 'Exception:%s' % (ex)}
                return json.dumps(data)
        else:
            data = {'error': 1, 'message': u'不支持的文件类型'}
            return json.dumps(data)
    return json.dumps({'error': 1, 'message': u'未知错误，请联系作者'})


def uploaded_file(filename):
    fileurl = filename[:3] + '/' + filename
    return send_from_directory(UPLOAD_FOLDER, fileurl)


def rmfile(filename, urls):
    import os

    florder = filename[:3]
    fileurl = os.path.join(UPLOAD_FOLDER, florder)
    realurl = os.path.join(fileurl, filename)
    f = Uploads.query.filter_by(file_name=filename).first()
    try:
        os.remove(realurl)
        flash(u'物理文件删除成功')
    except:
        flash(u'物理文件不存在')
    db.session.delete(f)
    db.session.commit()
    flash(u'数据删除成功')
    return redirect(url_for(urls))
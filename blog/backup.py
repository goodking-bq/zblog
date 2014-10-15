#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'
__createday__ = '2014-10-13'
from config import BACKUP_DIR, SQLALCHEMY_DATABASE_URI as dburl, UPLOAD_FOLDER
from flask import render_template, redirect, url_for, g
from flask.ext.login import login_required
from blog import db
from time import time
import os
from datetime import datetime
import subprocess
import zipfile
from blog.extend.EmailHelper import backup_mail
from blog.models import Backup_log

db_type = dburl[:dburl.find(':')]
dburl = dburl[dburl.find(':') + 1:]
db_user = dburl[dburl.find('/') + 2:dburl.find(':')]
dburl = dburl[dburl.find(':') + 1:]
db_pwd = dburl[:dburl.find('@')]
dburl = dburl[dburl.find('@') + 1:]
db_host = dburl[:dburl.find('/')]
db_name = dburl[dburl.find('/') + 1:]
sql_dir = os.path.join(BACKUP_DIR, str(time()) + '.sql')
back_script = 'mysqldump –u' + db_user + ' –p' + db_pwd + ' –lock-all-tables ' + db_name + ' > ' + sql_dir
back_file = os.path.join(BACKUP_DIR, str(time()) + '.zip')
global msg
msg = '<hr/>'


@login_required
def dobackup():
    if g.user.is_admin():
        start_time = datetime.now()
        global msg
        msg = msg + str(start_time) + ' -> ' + u'此次备份开始' + '<br/>'
        # try:
        # subprocess.Popen(back_script).wait()
        # return 1
        # except Exception,ex:
        # return Exception+':'+ex
        zip_file(UPLOAD_FOLDER, BACKUP_DIR)  # 压缩上传的附件
        msg = msg + str(datetime.now()) + ' -> ' + u'添加数据库备份到压缩文件' + '<br/>'
        # zf=zipfile.ZipFile(back_file,"a",zipfile.zlib.DEFLATED)
        #zf.write(sql_dir)
        #zf.close()
        msg = msg + str(datetime.now()) + ' -> ' + u'整个备份压缩成功' + '<br/>'
        backup_mail(back_file, msg)
        msg = msg + str(datetime.now()) + ' -> ' + u'已异步发送邮件，请查收' + '<br/>'
        msg = msg + str(datetime.now()) + ' -> ' + u'此次备份共耗时：' + str(
            (datetime.now() - start_time).seconds) + u'秒' + '<hr/>'
        log = Backup_log(start_time=start_time,
                         status=u'成功',
                         type=u'手动',
                         msg=msg)
        log.finish_time = datetime.now()
        db.session.add(log)
        db.session.commit()
        return redirect(url_for('backup'))
    else:
        return redirect(url_for('index1'))


def zip_file(dirname, zipfiledir):  # 压缩文件夹
    global msg
    filelist = []
    msg = msg + str(datetime.now()) + ' -> ' + u'加载需要压缩的上传文件' + '<br/>'
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else:
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))
    msg = msg + str(datetime.now()) + ' -> ' + u'上传文件加载完毕，开始压缩' + '<br/>'
    zf = zipfile.ZipFile(back_file, "w", zipfile.zlib.DEFLATED)
    for target in filelist:
        arcname = target[len(dirname):]
        zf.write(target, arcname)
        msg = msg + str(datetime.now()) + ' -> ' + arcname + u' 已写入文件 ' + back_file + '<br/>'
    zf.close()
    msg = msg + str(datetime.now()) + ' -> ' + u'上传文件压缩完毕' + '<br/>'


@login_required
def backup():
    log = Backup_log.query.order_by(Backup_log.id.desc()).first()
    return render_template('admin/backup.html', log=log)
#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'good'
__createday__ = '2014-10-13'
from config import BACKUP_DIR, UPLOAD_FOLDER
from flask import render_template, redirect, url_for, g
from flask.ext.login import login_required
from blog import db
import time
import os
from datetime import datetime
import subprocess
import zipfile
from blog.extend.EmailHelper import backup_mail
from blog.models import Backup_log

db_type = db.engine.url.drivername
db_user = db.engine.url.username
db_pwd = db.engine.url.password
db_host = db.engine.url.host
db_name = db.engine.url.database
global msg
msg = '<hr/>'


@login_required
def dobackup():
    sql_dir = os.path.join(BACKUP_DIR, format_time() + '.sql')
    back_script = 'mysqldump -u' + db_user + ' -p' + db_pwd + ' -h' + db_host + ' ' + db_name + ' > ' + sql_dir
    back_file = os.path.join(BACKUP_DIR, format_time() + '.zip')
    print back_script
    if g.user.is_admin():
        start_time = datetime.now()
        global msg
        msg = msg + str(start_time) + ' -> ' + u'此次备份开始' + '<br/>'
        zip_file(UPLOAD_FOLDER, back_file)  # 压缩上传的附件
        backupdb(back_script)
        t = 10
        while t >= 0:
            msg = msg + str(datetime.now()) + ' -> ' + u'等待数据库备份完成' + '<br/>'
            time.sleep(1)
            if os.path.exists(sql_dir):
                t = -1
            else:
                t -= 1
        if os.path.exists(sql_dir):
            msg = msg + str(datetime.now()) + ' -> ' + u'数据库备份完成。文件：' + sql_dir + '<br/>'
        else:
            msg = msg + str(datetime.now()) + ' -> ' + u'数据库备份失败。找不到文件：' + sql_dir + '<br/>'
        msg = msg + str(datetime.now()) + ' -> ' + u'添加数据库备份到压缩文件' + '<br/>'
        zf = zipfile.ZipFile(back_file, "a", zipfile.zlib.DEFLATED)
        zf.write(sql_dir)
        zf.close()
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


def zip_file(dirname, back_file):  # 压缩文件夹
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
    zf = zipfile.ZipFile(back_file, "a", zipfile.zlib.DEFLATED)
    for target in filelist:
        arcname = target[len(dirname):]
        zf.write(target, arcname)
        msg = msg + str(datetime.now()) + ' -> ' + arcname + u' 已写入文件 ' + back_file + '<br/>'
    zf.close()
    msg = msg + str(datetime.now()) + ' -> ' + u'上传文件压缩完毕' + '<br/>'


def backupdb(back_script):
    global msg
    msg = msg + str(datetime.now()) + ' -> ' + u'正在备份数据库...' + '<br/>'
    subprocess.Popen(back_script, shell=True,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)


def format_time():
    return 'backup_' + str(time.mktime(time.strptime(str(datetime.now())[:19],
                                                     "%Y-%m-%d %H:%M:%S")))[:10]


@login_required
def backup():
    log = Backup_log.query.order_by(Backup_log.id.desc()).first()
    return render_template('admin/backup.html', log=log)


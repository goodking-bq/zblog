#!/usr/bin/python
# coding=utf-8
__author__ = 'good'
__createday__ = '2014-12-11'

from flask.ext.script import Manager
from blog import db as database
from config import basedir, BACKUP_DIR, LOG_DIR, UPLOAD_FOLDER
import os

if os.name == 'nt':
    import sys

    reload(sys)
    sys.setdefaultencoding("utf-8")

BackupManager = Manager(help=u'备份一些东西')


@BackupManager.command
def uploads():
    u"""备份上传的附件"""
    pass


@BackupManager.command
def full():
    """备份整个blog"""
    zip_name = format_name('blog', 'zip')
    zip_dir = os.path.join(BACKUP_DIR, zip_name)
    file_zip(basedir, zip_dir, [BACKUP_DIR, LOG_DIR])


@BackupManager.command
def db():
    """备份数据库"""
    db_user = database.engine.url.username
    db_pwd = database.engine.url.password
    db_host = database.engine.url.host
    db_name = database.engine.url.database
    sql_file = zip_name = format_name('db', 'sql')
    backup_sql = 'mysqldump -u' + db_user + ' -p' + db_pwd + ' -h' + db_host + ' ' + db_name + ' > ' + sql_file
    zip_name = format_name('db', 'zip')
    zip_dir = os.path.join(BACKUP_DIR, zip_name)
    pass


@BackupManager.command
def auto():
    """默认备份（附件及数据库）"""
    pass


@BackupManager.command
def all():
    """备份所有"""
    pass


# 压缩文件
def file_zip(file_dir, zip_file_dir, excepts=None):
    import zipfile


    file_list = list()
    zf = zipfile.ZipFile(zip_file_dir,
                         "a", zipfile.zlib.DEFLATED)
    if os.path.isfile(file_dir):
        arcname = os.path.basename(file_dir)
        zf.write(file_dir, arcname)
    else:
        for root, dirs, files in os.walk(file_dir):
            if root not in excepts:
                for name in files:
                    file_list.append(os.path.join(root, name))
        if zip_file_dir in file_list:
            file_list.remove(zip_file_dir)
        if excepts is not None:
            for exc in excepts:
                if exc in file_list:
                    file_list.remove(exc)
        for target in file_list:
            arcname = target[len(file_dir):]
            zf.write(target, arcname)
    zf.close()


def format_name(st, type):
    import time
    from datetime import datetime

    return 'backup_' + st + '_' + str(time.mktime(time.strptime(str(datetime.now())[:19],
                                                                "%Y-%m-%d %H:%M:%S")))[:10] + type


    # BackupManager.add_command('auto', auto())
    # BackupManager.add_command('all', all())
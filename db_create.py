from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO
import os

from blog import db
from blog.models import Article
from blog.extend.Ubb2Html import Ubb2Html
#db.drop_all()
#db.create_all()

A=Article.query.all()
for c in A:
    c.text=Ubb2Html(c.body)
    db.session.add(c)
    db.session.commit()
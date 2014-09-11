from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO
import os

from blog import db
db.drop_all()
db.create_all()

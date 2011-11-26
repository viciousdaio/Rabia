#!/usr/bin/python

from google.appengine.ext import db

class RabiaStore(db.Model):
    url = db.StringProperty()
    comic = db.BlobProperty()
    datetime = db.DateTimeProperty(auto_now_add=True)
    encoding = db.StringProperty()

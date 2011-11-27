#!/usr/bin/python
import os
import urllib2
import datetime
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

# My Stuff
from models import RabiaStore
from imageurl import GetImageURLs
from storecomics import StoreComics

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("This is Rabia")


class GoStoreComics(webapp.RequestHandler):
    def get(self):
        storage = StoreComics()
        storage.get_comics()

        template_values = {
            'difference_set' : storage.state['difference'],
            'difference_count' : storage.state['difference_count'],
            'json_count' : storage.state['json_count'],
            'datastore_count' : storage.state['datastore_count']
            }

        path = os.path.join(os.path.dirname(__file__), 'storage.html')
        self.response.out.write(template.render(path, template_values))

class Browse(webapp.RequestHandler):
    def get(self):
        self.now = datetime.datetime.now()
        self.img_id = self.request.get('img', default_value='FFUU')
        if self.img_id == 'ERROR':
            self.response.out.write("FFUUUU")
        elif self.img_id == 'FFUU':
            self.no_have_id()
            self.common()
        else:
            self.have_id()
            self.common()

    def have_id(self):
        img_id = self.request.get('img')
        current_comic = RabiaStore.get(img_id)
        next_comic = RabiaStore.all().filter('__key__ <', db.Key(img_id)).order('-__key__')
        next_comic = next_comic.get()
        prev_comic = RabiaStore.all().filter('__key__ >', db.Key(img_id))
        prev_comic = prev_comic.get()

        if next_comic is not None:
            next_comic = next_comic.key()
        else:
            next_comic = False

        if prev_comic is not None:
            prev_comic = prev_comic.key()
        else:
            prev_comic = False
 
        self.template_values = {
            'prev_comic_id' : prev_comic,
            'next_comic_id' : next_comic,
            'imgur_url' : current_comic.url,
        }

    def no_have_id(self):
         query = db.Query(RabiaStore)
         query.filter("datetime <= ", self.now).order('-datetime')
         results = query.fetch(limit=3)
         current_comic = results[0]
         next_comic = results[1]
         comic_id = db.Key(str(results[1].key())).id()
         self.template_values = {
            'next_comic_id' : next_comic.key(),
            'imgur_url' : current_comic.url,
        }

    def common(self):
        path = os.path.join(os.path.dirname(__file__), 'browse.html')
        self.response.out.write(template.render(path, self.template_values))

application = webapp.WSGIApplication([
                                     ('/', MainPage),
                                     ('/browse', Browse),
                                     ('/storecomics', GoStoreComics)
                                     ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

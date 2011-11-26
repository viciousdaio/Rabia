#!/usr/bin/python
import os
import urllib2
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


class StorageClassDev(webapp.RequestHandler):
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


#        self.response.out.write(storage.state)
#        self.response.out.write(storage.state['json'])
#        self.response.out.write(storage.state['datastore'])
#        self.response.out.write(storage.state['difference'])
#        self.response.out.write(storage.state['json_count'])
#        self.response.out.write(storage.state['datastore_count'])
#        self.response.out.write(storage.state['difference_count'])

class ShowComics(webapp.RequestHandler):
    def get(self):
        img_id = self.request.get('img')
        rabia = RabiaStore()
        comic = rabia.get_by_id(int(img_id))
        next_comic = int(img_id) + 1
        prev_comic = int(img_id) - 1
        if comic.comic:
            self.response.headers['Content-Type'] = comic.encoding
            self.response.out.write(comic.comic)
        else:
            self.response.out.write("FFFFUUUUU")


class Browse(webapp.RequestHandler):
    def get(self):
        img_id = self.request.get('img')
        rabia = RabiaStore()
        comic = rabia.get_by_id(int(img_id))

        template_values = {
            'prev_comic_id' : int(img_id) - 1,
            'next_comic_id' : int(img_id) + 1,
            'imgur_url' : comic.url,
            'img_id' : img_id
            }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication([
                                     ('/', MainPage),
                                     ('/showcomics', ShowComics),
                                     ('/browse', Browse),
                                     ('/storecomics', StorageClassDev)
                                     ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

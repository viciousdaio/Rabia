#!/usr/bin/python
import os
import urllib2
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from models import RabiaStore
from ImageUrl import GetImageURLs
from sets import Set

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("This is Rabia")

class DupDetect(webapp.RequestHandler):
    def alt_prepare_query(self):
        """
        We'll use two Python sets and perform a difference operation
        between them. We get the performance of a dictionary but with
        much more readable and compact syntax.
        """
        json_url = "http://www.reddit.com/r/fffffffuuuuuuuuuuuu/.json"
        gi = GetImageURLs(json_url)
        urls = gi.get_image_url()
        query = db.Query(RabiaStore)
        query.filter("url IN ", urls)
        urls_from_json = Set(urls)
        results = query.fetch(limit=len(urls))
        urls_from_datastore = [each.url for each in results]
        urls_from_datastore = Set(urls_from_datastore)
        difference = urls_from_json - urls_from_datastore

        self.response.out.write(urls_from_datastore)
        self.response.out.write(urls_from_json)
        self.response.out.write(difference)

        if len(difference) == 0:
            self.response.out.write("No new comics have been found!")
        else:
            self.response.out.write("Found new comics! Proceeding to store:")
            for each in difference:
                image = urlfetch.fetch(each)
                rabia = RabiaStore()
                rabia.encoding = image.headers['content-type']
                rabia.comic = image.content
                rabia.url = each
                rabia.put()
                string = str("Just stored: %s"), str(each)
                self.response.out.write(string)

    def get(self):
        self.alt_prepare_query()

class PrimerRead(webapp.RequestHandler):
    """
    This class performs the initial primer read for the database.
    This is never used during production.
    """
    def get(self):
        json_url = "http://www.reddit.com/r/fffffffuuuuuuuuuuuu/.json"
        gi = GetImageURLs(json_url)

        for url in gi.get_image_url():
            image = urlfetch.fetch(url)
            rabia = RabiaStore()
            rabia.encoding = image.headers['content-type']
            rabia.comic = image.content
            rabia.url = url
            rabia.put()
            
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(rabia.key)
        self.response.out.write('Just stored some images!')

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
                                     ('/getcomics', PrimerRead),
                                     ('/showcomics', ShowComics),
                                     ('/browse', Browse),
                                     ('/dupdetect', DupDetect)
                                     ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

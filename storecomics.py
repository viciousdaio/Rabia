#!/usr/bin/python

from google.appengine.ext import db
from google.appengine.api import urlfetch
from sets import Set
from models import RabiaStore
from imageurl import GetImageURLs

class StoreComics:
    def __init__(self):
        self.json_url = "http://www.reddit.com/r/fffffffuuuuuuuuuuuu/.json"
        self.state = {}
        
    def get_comics(self):
        """
        Main method. Kicks off the other methods so we can just call it and
        fetch/store only what needs to be fetched/stored.
        """
        self.get_json_urls()
        self.check_datastore()
        self.diff_sets()
        self.storage_logic()

        # Just for debugging and testing
        self.state['json'] = self.urls_from_json
        self.state['datastore'] = self.urls_from_datastore
        self.state['difference'] = self.difference
        self.state['json_count'] = len(self.urls_from_json)
        self.state['datastore_count'] = len(self.urls_from_datastore)
        self.state['difference_count'] = len(self.difference)

    def check_datastore(self):
        """
        Checks the datastore to see if the URLs that are pulled from the
        JSON query are already present.
        """
        query = db.Query(RabiaStore)
        query.filter("url IN ", self.urls)

        # The fetch method requires a limit argument
        results = query.fetch(limit=len(self.urls))

        # List comprehension to build a list of results
        urls_from_datastore = [each.url for each in results]

        # Turn it into a Python set
        self.urls_from_datastore = Set(urls_from_datastore)

    def get_json_urls(self):
        """
        Gets the JSON URLs and stores them both in a standard list and
        in a Python set. We store them in a standard list because the
        Datastore API can only handle a list as opposed to a Python set.
        """
        gi = GetImageURLs(self.json_url)
        self.urls = gi.get_image_url()

        # Turn it into a Python set
        self.urls_from_json = Set(self.urls)

    def diff_sets(self):
        """
        This method performs the actual 'diffing'
        """
        self.difference = self.urls_from_json - self.urls_from_datastore

    def store_comics(self, comics_to_store):
        """
        This method accepts a set/list of comic URLs to fetch and store.
        Loops through the list, creates a new instance for each comic
        and stores each instance.
        """
        for comic in comics_to_store:
            # urlfetch library is unique to Google App Engine
            image = urlfetch.fetch(comic)

            # Datastore
            rabia = RabiaStore()
            rabia.encoding = image.headers['content-type']
            rabia.comic = image.content
            rabia.url = comic
            rabia.put()

    def storage_logic(self):
        """
        This method implements the logic to determine whether we are just
        inserting unique comics or whether we are performing a primer write
        to the datastore to get some initial values.

        This method will call the storage method and pass it the appropriate
        data set.
        """
        if len(self.difference) > 0:
            self.store_comics(self.difference)
        elif len(self.urls_from_datastore) == 0:
            self.store_comics(self.urls_from_json)
        else:
            self.state['if_block_loc'] = str("Nothing to do here!")

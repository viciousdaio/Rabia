#!/usr/bin/python

import urllib2
from django.utils import simplejson

class GetImageURLs:
    def __init__(self, json_url):
        """
        This class will pull down all of the URLs for a given subreddit
        .json URL.
        """
        self.json_url = json_url
        self.image_url_list = []

    def query_json(self):
        """
        Performs the JSON query.
        We discard the data we are not interested in so that we don't have
        to worry about parsing it.
        """
        self.result = simplejson.load(urllib2.urlopen(self.json_url))
        self.result = self.result['data']['children']

    def process_urls(self):
        """
        To download from imgur.com, we need to attach a file extension
        to the end of the URL so it downloads a comic instead of visiting
        their landing page for that comic.

        Alternatively, if the URL does have a file extension,
        keep calm and carry on.

        I chose to use .png, but this choice was totally arbitrary.
        """
        link_extension = '.jpg', '.JPG', '.png', '.PNG', '.gif', '.GIF'
        self.query_json()

        for each in self.result:
            url = each['data']['url']
            if url.endswith(link_extension):
                self.image_url_list.append(url)
            else:
                self.image_url_list.append(url + ".png")

    def get_image_url(self):
        """
        Kicks off the JSON query and URL processing.
        Returns a list of processed URLs.
        """
        self.process_urls()
        return self.image_url_list

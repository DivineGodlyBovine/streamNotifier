from html.parser import HTMLParser
import requests
import json

class twitchHtmlParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        if data[2:10] == '@context':
            dictionary = json.loads(data)
            self.data = dictionary['@graph'][0]['description']
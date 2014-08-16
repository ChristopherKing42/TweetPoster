import re
import json

import requests
from bs4 import BeautifulSoup

import TweetPoster


class ImageHost(object):

    url_re = None

    def extract(self, url):
        """
        Takes a URL, rehosts an image and returns a new URL.
        """
        raise NotImplementedError

    @classmethod
    def rehost(self, image_url):
        try:
            r = requests.post(
                'http://api.imgur.com/2/upload.json',
                params={
                    'key': TweetPoster.config['imgur']['key'],
                    'image': image_url
                }
            )
            if not r.status_code == 200:
                print r.json()['error']['message']
                return None

            return r.json()['upload']['links']['original']
        except (ValueError, requests.exceptions.RequestException):
            return None


class PicTwitterCom(object):

    @classmethod
    def extract(self, url):
        if not url.endswith(':large'):
            url = url + ':large'

        return ImageHost.rehost(url)


class Instagram(ImageHost):

    url_re = 'https?://instagram.com/p/[\w_-]+/'

    def extract(self, url):
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException:
            return None

        j = re.search('("display_src":".*?")', r.content)
        if j:
            j = json.loads('{' + j.group(1) + '}')
            return self.rehost(j['display_src'])


class YFrog(ImageHost):

    url_re = 'https?://yfrog.com/\w+'

    def extract(self, url):
        url = url.replace('://', '://twitter.')
        try:
            r = requests.get(url, params={'sa': 0})
        except requests.exceptions.RequestException:
            return None

        soup = BeautifulSoup(r.content)
        photo = soup.find(id='input-direct')['value']

        return self.rehost(photo)


class Twitpic(ImageHost):

    url_re = 'https?://twitpic.com/\w+'

    def extract(self, url):
        url = url + '/full'

        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content)
        except:
            return None

        img = soup.find(id='media-full').find('img')
        return self.rehost(img['src'])


class Puush(ImageHost):

    url_re = 'https?://puu.sh/[\w0-9]+'

    def extract(self, url):
        return self.rehost(url)


class Facebook(ImageHost):

    url_re = 'https?://facebook.com/photo.php\?fbid=[0-9]+$'

    def extract(self, url):
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException:
            return None

        soup = BeautifulSoup(r.content)
        img = soup.find(id='fbPhotoImage')
        return self.rehost(img['src'])

import requests
from lxml import etree
from pixivapi import Client, Size, Illustration


class Post(object):
    """Get info on a post on yande.re."""

    def __init__(self, board, post_id):
        if not isinstance(post_id, int) and not post_id.isdigit():
            raise TypeError

        req = requests.get('https://' + board + '/post.json',
                           params={'tags': 'id:' + str(post_id) + ' limit:1',
                                   'api_version': '2', 'filter': '1',
                                   'include_tags': '1', 'include_votes': '1',
                                   'include_pools': '1'})
        self.post_json = req.json()
        self.post_info = self.post_json['posts'][0]
        self.post_tags = self.post_json['tags']
        self.post_id = int(post_id)
        self.board = board

    @property
    def rating(self):
        return self.post_info['rating']

    @property
    def tags(self):
        return self.post_info['tags']

    @property
    def width(self):
        return self.post_info['width']

    @property
    def height(self):
        return self.post_info['height']

    @property
    def dimensions(self):
        return str(self.width) + 'x' + str(self.height)

    @property
    def parent_id(self):
        if self.post_info['parent_id'] is not None:
            return self.post_info['parent_id']
        else:
            raise Exception

    @property
    def uploader(self):
        return self.post_info['author']

    @property
    def preview(self):
        return self.post_info['preview_url']

    @property
    def file(self):
        return self.post_info['file_url']

    @property
    def jpeg(self):
        return self.post_info['jpeg_url']

    @property
    def source(self):
        s = self.post_info['source']
        return s if s else None


class DanPost(Post):
    """Get info on a post on danbooru."""

    def __init__(self, post_id):
        if not isinstance(post_id, int) and not post_id.isdigit():
            raise TypeError

        req = requests.get('http://danbooru.donmai.us/post/index.json',
                           params={'tags': 'id:' + str(post_id)})
        self.post_json = req.json()
        self.post_info = self.post_json[0]
        self.post_id = int(post_id)
        del self.post_json


class IQDB(object):
    """
    Given an image url, find similar images on danbooru using iqdb.
    An image is defined to match if the similarity is greater than the cutoff.
    The matching image's danbooru id can also be obtained.
    """

    def __init__(self, image_url):
        self.cutoff = 90.0
        url = 'http://danbooru.iqdb.org/index.xml?url='
        tree = etree.parse(url + image_url)
        self.root = tree.getroot()

    @property
    def similarity(self):
        return float(self.root.xpath('/matches/match')[0].attrib['sim'])

    @property
    def id(self):
        return int(self.root.xpath('/matches/match/post')[0].attrib['id'])

    @property
    def match(self):
        if self.similarity >= self.cutoff:
            return True
        else:
            return False




class Pixiv(object):

    """
    Get the direct, full-size image url on pixiv, given an url with
    'member_illust' in it.
    The direct image url can then be used with Artist and DanArtist to find an
    artist's name.
    Requires a logged in requests session.
    """

    def __init__(self, url, id):
        self.url = url
        self.pxClient = Client()
        self.pxClient.login("", "")

        self.illustration = self.pxClient.fetch_illustration(id)

    @property
    def source(self):
        return self.url

    @property
    def file(self):
        return self.illustration.image_urls[Size.ORIGINAL]

    @property
    def tags(self):
        return []

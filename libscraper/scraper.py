from fixtures import targets
from parser import BaseParser
from utils import Logger

class Scraper(object):

    def __init__(self, verbose=False):
        self.logger = Logger(verbose=verbose)
        self._targets = targets
        self._parser = None

    def urlinfo(self, url):
        """
        Initializes Parser Model.
        Returns URL target information if a match against known patterns is found.

        """
        if not self._parser:
            self._parser = BaseParser(self)
        info = self._parser.urlinfo(url, init=True)
        if info.has_key('module'):
            self._parser = info['module'].Parser(self)
            self.logger.debug('Using model "%s"' % self._parser.name)
        return info

    def parse(self, url, headers=None, proxy=None):
        """ Returns Tree object """
        if not self._parser:
            self._parser = BaseParser(self)
        return self._parser.parse(url, headers, proxy)
            
    def get_deals(self, url):
        if not url:
            return []
        self.urlinfo(url) # initialize parser model
        return self._parser.get_deals(url)

    def get_deal(self, url=''):
        if not url:
            return {}
        self.urlinfo(url) # initialize parser model
        return self._parser.get_deal(url)

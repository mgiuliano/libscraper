"""
The Parser module provides the tools required to parse URLs.

"""
import importlib
import hashlib
import pkg_resources
import re
import random
import sys
import urllib2
from lxml import etree
from libscraper.exceptions import TargetPatternNotFound


class Tree(object):

    def __init__(self, code=500, ptype='--', url='--', root=None, msg=''):
        self._ptype = ptype
        self._code = code
        self._url = url
        self._root = root
        self._msg = msg

    def __str__(self):
        prt = self._msg if self._root is None else self._root
        return "[{:s}] {:d} \"{:s}\" {!s}".format(self._ptype, self._code, self._url, prt)


class BaseParser(object):

    def __init__(self, scraper):
        self.scraper = scraper
        self._targets = scraper._targets

    def urlinfo(self, url, init=False):
        """
        Extract information from a raw URL.
        Attempts to match a URL to a known site pattern.

        Returns Parser model if found.

        """
        url = url.split('?').pop(0) # Remove any querystring
        match = None
        for target in self._targets:
            for pattern in target._patterns:
                s = pattern.search(url)
                if s is not None:
                    match = target.get_info()
                    match['info'] = list(s.groups())
                    break
            if init and match:
                parser_model = match['parser'] + '.py'
                models = pkg_resources.resource_listdir('models', '')
                if parser_model in models:
                    # Load module
                    module = importlib.import_module('.'+parser_model[:-3], 'models')
                    # Replace parser with Parser instance
                    parser = module.Parser(self.scraper)                    
                    match['parser'] = parser
                    # Load info from fixtures
                    match.update(parser.get_urlinfo(match))
                break
        if not match:
            raise TargetPatternNotFound()
            return {}
        if not init:
            match.update(self.get_urlinfo(match))
        return match

    def __connect(self, url, headers=None, proxy=None):
        timeout = 10 # set timeout at 10 seconds
        request = urllib2.Request(url)
        if headers is not None:
            for header in headers:
                request.add_header(header['name'], header['value'])
        user_agents = [
            "Mozilla/5.0 (Linux i686)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.60 Safari/537.1",
        ]
        request.add_header('User-agent', user_agents[random.randint(0, len(user_agents)-1)])
        if proxy is not None:
            proxy_handler = urllib2.ProxyHandler({'http':proxy})
            opener = urllib2.build_opener(proxy_handler)
        else:
            opener = urllib2.build_opener()
        r = opener.open(request, timeout=timeout)
        return r

    def get_hash(self, hashbag=[]):
        if not hashbag:
            return None
        return hashlib.sha256(','.join([str(i) for i in hashbag])).hexdigest()

    def parse(self, url, headers=None, proxy=None):
        """
        Parse URL to a Tree object.
        All URLs are parsed as XML/XHTML, defaulting to HTML when an XML syntax error is found.

            -- headers      list of request HTTP headers
            -- proxy        proxy format: "IP:port"

        """
        try:
            response = self.__connect(url, headers, proxy)
        except urllib2.HTTPError as e:
            self.scraper.logger.debug(sys.exc_info())
            return Tree(url=url, code=e.code, msg=e.msg)
        except urllib2.URLError as e:
            self.scraper.logger.debug(sys.exc_info())
            return Tree(url=url, code=404, msg=e.reason)
        except Exception as e:
            self.scraper.logger.debug(sys.exc_info())
            return Tree(url=url, msg=e)
        try:
            output = response.read()
        except Exception as e:
            self.scraper.logger.debug(sys.exc_info())
            return Tree(url=url, msg=e)
        try:
            ptype = 'XML'
            root = etree.fromstring(output, etree.XMLParser(encoding='utf-8'))
        except etree.XMLSyntaxError:
            try:
                ptype = 'HTML'
                root = etree.fromstring(output, etree.HTMLParser(encoding='utf-8'))
            except Exception as e:
                self.scraper.logger.debug(sys.exc_info())
                return Tree(url=url, msg=e)
        except Exception as e:
            self.scraper.logger.debug(sys.exc_info())
            return Tree(url=url, msg=e)
        if type(root) is not etree._Element:
            root = None
        return Tree(ptype=ptype, code=response.code, url=response.geturl(), root=root)

    def get_deals(self, url):
        """
        The method should gather the following information:
            - title         Main headline
            - headline      Sub-headline
            - link          Full URI
            - rel_id        Local ID (integer)
            - pubDate       Publication date (datetime.datetime)
            - description   Additional description
            - site          Site name
            - locale        Locale code
            - location      Location
            - category      Category
            - hashid        SHA256 hash (used to uniquely identify a deal)

        """
        return []

    def get_deal(self, url):
        """
        The method should gather the following information:
            - status        If the deal is sold out or expired
            - merchant      Merchant name
            - merchant_url  Merchant site URL
            - addresses     A list of address lines (as Dictionaries)
            - rrp           Displayed (or computed) RRP
            - price         Displayed price
            - volume        Displayed sales amount

        """
        return {}

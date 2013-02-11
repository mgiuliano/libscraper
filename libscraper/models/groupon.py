"""
Groupon (EU) Model.

"""
import datetime
import re
from lxml import etree
from libscraper import utils
from libscraper.parser import BaseParser
from libscraper.exceptions import ElementMissing

class Parser(BaseParser):

    name = 'Groupon (EU)'


    def get_urlinfo(self, info):
        """ Map data from fixtures """
        data = {}
        if info.has_key('info') and info['info']:
            # Location
            location = info['info'][0]
            if location:
                data['location'] = utils.capitalize(re.sub(r'[-_]', ' ', location))
            else:
                data['location'] = 'National'
            if info['locmap'].has_key(location):
                data['location'] = info['locmap'][location]['location']
                data['category'] = info['locmap'][location]['category']
            # Rel ID
            data['rel_id'] = info['info'][1]
        return data


    def get_deals(self, url):
        """
        The Groupon Europe RSS feed lists all deals.
        Some RSS items include more than one offering, which are represented as multiple deals.

        """
        deals = []
        tree = self.parse(url=url)
        if tree._root is None:
            return [] # The parsing failed (usually caused by connection/network issues)

        if tree._ptype != 'XML':
            return [] # The Groupon parser requires an XML-formatted URL

        if tree._code == 200:
            info = self.urlinfo(url)
            for item in tree._root.xpath('/rss/channel/item'):
                title = utils.get_text(item.xpath('title')[0])
                pubDate = utils.get_text(item.xpath('pubDate')[0])[:-4] # Remove ' GMT'
                pubDate = datetime.datetime.strptime(pubDate, '%a, %d %b %Y %X')
                link = utils.strip_qs(utils.get_text(item.xpath('link')[0]))
                link_base = "/".join(link.split('/')[:-1])
                description = etree.HTML(item.xpath('description')[0].text)
                if len(description.xpath('//ul/a')) > 1:
                    for itm in description.xpath('//ul'):
                        deal = {}
                        deal['title'] = utils.get_text(itm.xpath('a')[0])
                        deal['headline'] = utils.get_text(itm.xpath('br')[0], with_tail=True)
                        deal['link'] = utils.strip_qs(itm.xpath('a')[0].get('href'))
                        info = self.urlinfo(deal['link'])
                        deal['rel_id'] = info['rel_id']
                        deal['pubDate'] = pubDate
                        deal['site'] = info['site']
                        deal['locale'] = info['locale']
                        deal['location'] = info['location']
                        deal['category'] = info['category']
                        hashbag = [
                            deal['title'],
                            deal['headline'],
                            deal['pubDate'],
                            deal['rel_id'],
                            deal['site'],
                            deal['locale'],
                            deal['location'],
                            deal['category']
                        ]
                        deal['hashid'] = self.get_hash(hashbag)
                        deals.append(deal)
                else:
                    deal = {}
                    deal['title'] = title
                    deal['headline'] = utils.get_text(description)
                    deal['link'] = link
                    info = self.urlinfo(link)
                    deal['rel_id'] = info['rel_id']
                    deal['pubDate'] = pubDate
                    deal['site'] = info['site']
                    deal['locale'] = info['locale']
                    deal['location'] = info['location']
                    deal['category'] = info['category']
                    hashbag = [
                        deal['title'],
                        deal['headline'],
                        deal['pubDate'],
                        deal['rel_id'],
                        deal['site'],
                        deal['locale'],
                        deal['location'],
                        deal['category']
                    ]
                    deal['hashid'] = self.get_hash(hashbag)
                    deals.append(deal)
        return deals


    def get_deal(self, url):
        """
        All deals use the same layout.
        Groupon uses different URLs poiting to the same deal. The URL format defines the HTMLformat displayed.
        
        """
        deal = {}
        tree = self.parse(url=url)
        if tree._root is not None and tree._code == 200:
            try:
                tag = tree._root.xpath('//input[@id="currentTimeLeft"]').pop()
                deal['status'] = 1
            except IndexError: # Expired / Sold Out
                deal['status'] = 0
            else:
                try:
                    tag = tree._root.xpath('//div[@class="merchantContact"]').pop()
                except IndexError:
                    raise ElementMissing('{:s}:://div[@class="merchantContact"]'.format(url))
                else:
                    try:
                        deal['merchant'] = utils.get_text(tag.xpath('//h2[@class="subHeadline"]')[0])
                    except IndexError:
                        raise ElementMissing('{:s}:merchant://h2[@class="subHeadline"]'.format(url))
                    else:
                        try:
                            deal['merchant_url'] = tag.xpath('a').pop().get('href')
                        except IndexError:
                            pass
                        address = self.__extract_address_lines(tag)
                        if address:
                            deal['addresses'] = [address]
                try:
                    tag = tree._root.xpath('//div[@id="contentDealBuyBox"]/span[@class="price"]/span[@class="noWrap"]').pop()
                except IndexError:
                    raise ElementMissing('{:s}:price://div[@id="contentDealBuyBox"]/span[@class="price"]/span[@class="noWrap"]'.format(url))
                else:
                    price = utils.extract_float_from_tag(tag)
                    deal['price'] = price
                    try:
                        tag = tree._root.xpath('//div[@id="contentDealBuyBox"]/table[@class="savings"]//tr[@class="row2"]/td')[1]
                        _savings = utils.extract_float_from_tag(tag)
                    except IndexError:
                        _savings = 0.0
                    deal['rrp'] = price + _savings
                    try:
                        tag = tree._root.xpath('//span[@id="jDealSoldAmount"]').pop()
                    except IndexError:
                        raise ElementMissing('{:s}:sales://span[@id="jDealSoldAmount"]'.format(url))
                    else:
                        deal['volume'] = int(utils.extract_float_from_tag(tag))
        return deal


    def __extract_address_lines(self, tag):
        raw_address = []
        for a in utils.extract_lines_from_tag(tag):
            raw_address.extend([utils.strip_white_spaces(s) for s in a.split(',')])
        return raw_address

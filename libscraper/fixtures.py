"""
Target Patterns.
Patterns within a target need to be ordered using the most specific first.

Optional location mapping allows specific assignment of known location strings
to actual location name and/or category, using the following format:
    locmap = {
        'loc-code': {
            'location': <Location>,
            'category': <Category>
        },
        ...
    }

"""
import re

class Target(object):

    def __init__(self, site='', locale='', category='', parser='', patterns=[], locmap={}):
        self._site_name = site
        self._locale = locale
        self._category = category
        self._parser = parser
        self._patterns = []
        for pattern in patterns:
            self._patterns.append(re.compile(r"{:s}".format(pattern)))
        self._locmap = locmap

    def get_info(self):
        return {
            'site': self._site_name,
            'locale': self._locale,
            'category': self._category,
            'parser': self._parser,
            'locmap': self._locmap,
            'unicode': self.tostring(),
        }

    def tostring(self):
        return "{:s} [{:s}] {:s}".format(self._site_name, self._locale, self._category)

targets = [

    ### Groupon UK ###
    Target(
        site='Groupon', # Groupon UK (Getaways)
        locale='en_GB', 
        category='Getaways', 
        parser='groupon',
        patterns=[
            'http://www.groupon.co.uk/deals/groupon-getaways/[\w-]+/(\d+)'
        ]
    ),
    Target(
        site='Groupon', # Groupon UK (All other Channels)
        locale='en_GB',
        parser='groupon',
        patterns=[
            'http://10.1.29.10/~michael/dealstracker/GrouponUK.xml',    # FEED [DEV]
            'http://api.groupon.de/feed/api/v1/deals/oftheday/UK',      # FEED
            'http://www.groupon.co.uk/deals/([\w-]+)/[\w-]+/(\d+)'
        ],
        locmap={
            'national-deal': {'location': 'National', 'category': 'Goods'},
            'birmingham-special': {'location': 'Birmingham', 'category': 'Special'},
            'london-special': {'location': 'London', 'category': 'Special'},
            'manchester-special': {'location': 'Manchester', 'category': 'Special'},
            'events': {'location': 'National', 'category': 'Events'},
            'groupon-getaways': {'location': 'National', 'category': 'Getaways'},
        }
    ),


    #Target(
    #    site='Groupon', # Groupon FR (All Channels)
    #    locale='fr_FR',
    #    parser='groupon',
    #    patterns=[
    #        'http://www.groupon.fr/deals/([\w-]+)/[\w-]+/(\d+)'
    #    ],
    #    locmap={
    #        'bordeaux-extra': {'location': 'Bordeaux Metropole'},
    #        'toulouse-extra': {'location': 'Grand Toulouse'},
    #        'marseille-extra': {'location': 'Marseille Region'},
    #        'nantes-extra': {'location': 'Nantes Metropole'},
    #        'nice-extra': {'location': 'Nice Riviera'},
    #        'voyages': {'location': 'National', 'category': 'Getaways'},
    #    }
    #),

]

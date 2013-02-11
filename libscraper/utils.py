"""
Common tools and helpers.

"""
import inspect
import re
from lxml import etree

float_re = re.compile(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")


class Logger(object):

    def __init__(self, verbose=False):
        self.verbose = verbose

    def debug(self, msg):
        if self.verbose:
            print msg


def strip_qs(url):
    """ Strip URL from its querystring """
    return url.split('?').pop(0)

def bytestr(s, encoding='utf-8', errors='strict'):
    """ Returns a bytestring version of 's', encoded as specified in 'encoding'. """
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([bytestr(arg, encoding, errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

def surestr(s):
    """
    Most TCP services use str types; 
    as str cannot be eval()ed to unicode directly, we must manually remove the unicode representation
    (turned to actual string)... i.e. when real string in wrapped within u'...'

    """
    s = bytestr(s)
    try:
        if s[:2] == "u'":
            s = s[2:-1]
    except:
        pass
    return s.lstrip("'").rstrip("'")

def capitalize(data):
    return " ".join(["{:s}{:s}".format(d[0].upper(), d[1:]) for d in data.split(" ")])

def strip_white_spaces(data):
    value = bytestr(data)
    value = re.sub(r'\r|\n|\xc2\xa0', ' ', value)
    value = re.sub(r'\s\s+', ' ', value)
    if value:
        return value.strip()
    return ''

def get_text(element, with_tail=False):
    value = etree.tostring(element, method='text', with_tail=with_tail, encoding='utf-8')
    value = strip_white_spaces(value)
    return bytestr(value)

def extract_lines_from_tag(tag, exclude_tags=('a','iframe'), include_tags=None):
    """
    Parses an element an returns all the text in an array.
    Tags can be specifically exluded from the result.
    When a list of tags to include is given, it takes precedence over the exclude list.

    """
    lines = []
    value = bytestr(strip_white_spaces(tag.text))
    if value and value != 'None':
        lines.append(value)
    value = bytestr(strip_white_spaces(tag.tail))
    if value and value != 'None':
        lines.append(value)
    for e in tag:
        if include_tags:
            if e.tag not in include_tags:
                continue
        elif e.tag in exclude_tags:
            continue
        value = bytestr(strip_white_spaces(e.text))
        if value and value != 'None':
            lines.append(value)
        value = bytestr(strip_white_spaces(e.tail))
        if value and value != 'None':
            lines.append(value)
        if len(e):
            newlines = extract_lines_from_tag(e, exclude_tags=exclude_tags, include_tags=include_tags)
            for line in newlines:
                if line not in lines:
                    lines.append(line)
    return lines

def clean_address_lines(address_lines, locale):
    """
    Converts a list of address fields to a dictionary.
    The dictionary will contained the cleaned Postcode and Phone number if found.
    The method first detects which locale to use to extract formatted addresses.

    Clean addresses MUST have a valid postcode.

    """
    code = locale[3:].lower()
    method = "clean_{:s}_address_lines".format(code)
    module = inspect.getmodule(inspect.stack()[0][0])
    if not hasattr(module, method):
        return {}
    else:
        address = getattr(module, method)(address_lines)
        if not address.has_key('postcode'):
            return {} # No postcode
        else:
            lines = []
            for line in address['address']:
                addr = re.sub(address['postcode'], '', line).strip()
                if addr:
                    lines.append(addr)
            address['address'] = lines
            address['locale'] = locale
            return address

def clean_gb_address_lines(address_lines):
    outcode_pattern = '[A-PR-UWYZ]([0-9]{1,2}|([A-HIK-Y][0-9](|[0-9]|[ABEHMNPRVWXY]))|[0-9][A-HJKSTUW])'
    incode_pattern = '[0-9][ABD-HJLNP-UW-Z]{2}'
    postcode_re = re.compile(r'(GIR 0AA|%s %s)' % (outcode_pattern, incode_pattern))
    space_re = re.compile(r' *(%s)$' % incode_pattern)
    phone_digits_re = re.compile(r'([0-9]{11})')
    invalid_values_re = re.compile("|".join(["None",]))
    excluded_values_re = re.compile(r'[\|\.]|{:s}'.format("|".join(["Returns:"])))
    clean_address = {'address': []}
    for line in address_lines:
        m = phone_digits_re.search(re.sub(r'\s\s*', '', line))
        if m:
            clean_address.update({'phone': u'{!s}'.format(m.group(1))})
            continue
        postcode = space_re.sub(r' \1', line.upper().strip())
        m = postcode_re.search(postcode)
        if m:
            clean_address.update({'postcode': u'{!s}'.format(m.group(1))})
        value = excluded_values_re.sub('', line).lstrip().rstrip()
        if not invalid_values_re.search(value):
            clean_address['address'].append(u'{!s}'.format(value.decode('utf-8')))
    return clean_address

#def clean_fr_address_lines(address_lines):
#    phone_digits_re = re.compile(r'^0\d(\s|\.)?(\d{2}(\s|\.)?){3}\d{2}$')
#    postal_code_re = re.compile(r'(\d{5})')
#    excluded_values_re = re.compile(r'[\|\.]|{:s}'.format("|".join([])))
#    invalid_values_re = re.compile("|".join(["None",]))
#    clean_address = {'address': []}
#    for line in address_lines:
#        value = smart_unicode(line)
#        phone_value = re.sub('(\.|\s)', '', value)
#        m = phone_digits_re.search(phone_value)
#        if m:
#            clean_address.update({
#                'phone': u'{:s} {:s} {:s} {:s} {:s}'.format(
#                                                            phone_value[0:2],
#                                                            phone_value[2:4],
#                                                            phone_value[4:6],
#                                                            phone_value[6:8],
#                                                            phone_value[8:10]
#                                                           )
#            })
#            continue
#        m = postal_code_re.search(value)
#        if m:
#            clean_address.update({'postcode': m.group(1)})
#        value = excluded_values_re.sub('', value).lstrip().rstrip()
#        if not invalid_values_re.search(value):
#            clean_address['address'].append(value)
#    return clean_address

def extract_float_from_tag(tag):
    """
    Clean HTML element containing number, then returns the float value.
    Strips HTML entities, tags, and whitespaces.

    @param lxml._Element data
        the lxml Element object
    @return float data
        the number extracted from the element

    """
    entities = ['&#13;', '&#160;', '&#163;', '&#8364;']
    pattern = "|".join("{:s}".format(re.escape(entity)) for entity in entities)
    data = strip_white_spaces(re.sub(pattern, '', etree.tostring(tag)))
    #try:
    #    data = data.replace(self.locale.currency, '')
    #except AttributeError:
    #    pass
    pattern = re.compile(r'<.*?>')
    data = pattern.sub(' ', data)
    # Extract number
    return extract_float_from_string(data)

def extract_float_from_string(data):
    """
    Extract number from string

    @param string data
        the clean string stripped from HTML tags, entities and special characters
    @return float data
        the number extracted from the element

    """
    data = data.replace('. ', '.') # handle special case for PoinX: format '10. 00' (dot followed by space)
    decimals = digits = thousands = '0'
    pattern = re.compile(r"""
        \b(\d+)         # leading digits (first group): makes up first part of the number (1, 10, 100, 1000, ... or 1 reprenting a thousand)
        \D?(\d{0,3})    # following digits: composed of 0 to 3 digits, representing hundreds (represent either hundreds of thousand-split number, or decimals)
        \D?(\d{0,2})    # closing digits: represents closing decimals
    """, re.VERBOSE)
    matches = pattern.search(data)
    if matches is not None:
        results = matches.groups()
        has_group_1 = len(results[0]) > 0 and True or False
        has_group_2 = len(results[1]) > 0 and True or False
        has_group_3 = len(results[2]) > 0 and True or False

        # Analyse matching groups:

        # 1. are there any decimals (always in 3rd group)
        decimals = has_group_3 and results[2] or '0'

        # 2. check second group value and length
        #   we are only interested in this group if it is set
        digits = has_group_2 and results[1] or '0'
        if has_group_2:
            # when this group is set, it could either represent the decimal digits or the number
            if len(digits) >= 3 or decimals != '0':
                # decimal digits cannot be represented with more than 2 digits
                # it also cannot represent decimals if they have already been found earlier
                # i.e.: this group represents the hundreds - do nothing
                pass
            else:
                # the group represents the decimal digits
                decimals = digits
                digits = '0'
        # append extra '0' to single decimals (i.e.: 0.9 -> 0.90; whithout this tep, 0.9 would become 0.09)
        if len(decimals) < 2:
            decimals += '0'

        # 3. check first group
        if not has_group_2 and not has_group_3:
            # when this group is only one set, it represent the whole number
            digits = results[0]
        elif has_group_2 and not has_group_3:
            # this case has already been handled (equivalent to group 2 representing digits)
            # if digits have nbot yet been set, this group represents the digits
            if digits == '0':
                digits = results[0]
            else:
                thousands = results[0]
        else:
            # otherwise, the group represent the thousand digit
            thousands = results[0]

        # Recompose number
        return ( float(thousands) * 1000 ) + float(digits) + ( float(decimals) / 100 )

    else:
        return 0.0

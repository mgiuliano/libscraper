"""
Exceptions specific to the Scraper library.

"""

class TargetPatternNotFound(Exception):
    pass

class ElementMissing(Exception):
    """
    ElementMissing should provide the relevent information associated with the element.
    This includes:
        - For which URL this happened
        - What the element was supposed to be
        - What data was this element supposed to contain

    One way of doing this is to consistently send the following when constructing the Exception parameter:
        ElementMissing('<url>:<data>:<xpath-expression>')
        e.g.: ElementMissing('{:s}:price://div[@class="price"]'.format(url))

    """
    pass

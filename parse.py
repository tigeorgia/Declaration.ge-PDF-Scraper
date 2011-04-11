#!/usr/bin/python
# vim: set fileencoding=utf-8
"""Income declarations parser.

Parses an income declaration from http://declaration.ge, converted
to HTML using pdf2xml.
"""
import sys
import getopt
import html5lib
import lxml
from BeautifulSoup import BeautifulSoup #Deprecated but still the best
import datetime

from incomeExceptions import BlankDeclarationError, MalformedDeclarationError
from discard import discard

def main():
# parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
# process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
# process arguments
    for arg in args:
        parse(arg)

def parse(path):
    try:
        f = open(path)
    except IOError as e:
        print("Could not find file."+e)
        return

    doc = html5lib.parse(f,treebuilder="beautifulsoup", encoding="utf-8")
    output(doc)

def is_mkhedruli(char):
    chars = [u'ღ',u'ჯ',u'უ',u'კ',u'ე',u'ნ',u'გ',u'შ',u'წ',u'ზ',u'ხ',u'ც',u'ჟ',u'დ',u'ლ',u'ო',u'რ',u'პ',u'ა',u'თ',u'ვ',u'ძ',u'ფ',u'ჭ',u'ჩ',u'ყ',u'ს',u'მ',u'ი',u'ტ',u'ქ',u'ბ',u'ჰ']
    return char in chars

# Search through headings for one that successfully
# converts to an int, return that.
def discover_num(page):
    # Big text
    headings = page.findAll(name='span', attrs={"class": "ft1"})
    for head in headings:
        txt = head.contents[0]
        try:
            return int(txt)
        except ValueError:
            continue
    raise MalformedDeclarationError("Could not find a page number")

def position_from_style(style_str):
    rules = [ rule.split(u":") for rule in style_str.split(u";")]
    pos = {}
    
    for rule in rules:
        if rule[0] == u"top":
            pos[rule[0]] = rule[1]
        elif rule[0] == u"left":
            pos[rule[0]] = rule[1]
    print pos
    return pos

def clean_headers(headers,discard)
    """ Takes an array of BeautifulSoup <span> tags and returns
    an array of <span> tags excluding those found in discard"""
    clean = []
    for h in headers:
        if h.contents[0] not in discard:
            clean.append(h)
    return clean

def output(doc):
    pfx = [
        page0,
        page1,
    ] # Function for each page. Not optimal, but should
            # be resistant to minor changes in page formatting
    decl_obj = {} # Storage variable for the data.
    decl_obj["scrape_date"] = str(datetime.date.today())

    # Document pages are represented by container divs that are
    # children of root element.
    #pages = doc.findAll(name=True, recursive=False)
    root = doc.find('body')
    pages = root.findAll(name='div',recursive=False)
    
    for page in pages:
        num = discover_num(page)
        try:
            pfx[num](page,decl_obj) #Call page parsing function
            print(decl_obj)
        except BlankDeclarationError as e:
            print("Blank declaration "+str(e))
            

def page0(pg_div,decl):
    raise MalformedDeclarationError("Illegal page number")

def page1(pg_div,decl):
########################
# HEADINGS (FT1)       #
########################
    headings = pg_div.findAll(name='span', attrs={"class":"ft1"})

    decl_id, decl_date, name = None, None, None

    for head in headings:
        txt = head.contents[0]
        #print(txt)
        if txt in discard["page1"]:
            continue

        if txt.isdigit(): # Page number only
            continue
        
        if txt[0] == u'#': # Declaration id
            decl_id = u''.join(txt.split())[1:]
            continue

        if txt.find(u'/') != -1: # Decl. date
            decl_date = txt
            continue
        
        if is_mkhedruli(txt[0]):
            name = txt
            continue

    if decl_id == None:
        raise MalformedDeclarationError(u"Couldn't find declaration id")

    if decl_date == None or name == None:
        raise BlankDeclarationError(unicode(decl_id))

    else:
        decl["decl_id"] = decl_id
        decl["decl_date"] = decl_date
        decl["name"] = name

########################
# POSITION (FT5)       #
########################
    job = pg_div.find(name='span', attrs={"class":"ft5"})
    decl["position"] = job.contents[0]
    
########################
# DOB, ADDRESS (FT3)   #
########################
    headers = pg_div.findAll(name='span', attrs={"class":"ft3"})
    if len(headers) != 2:
        raise MalformedDeclarationError("Wrong number of FT3")

    pos0 = position_from_style(headers[0].parent.parent['style'])
    pos1 = position_from_style(headers[1].parent.parent['style'])

    if pos0["top"] > pos1["top"]:
        decl["work_contact"] = headers[1].contents[0]
        decl["place_dob"] = headers[0].contents[0]
    else:
        decl["work_contact"] = headers[0].contents[0]
        decl["place_dob"] = headers[1].contents[0]
########################
# FAMILY (FT4)         #
########################
    
    all_ft3 = pg_div.findAll(name='span', attrs={"class":"ft3"})

    headers = clean_headers(all_ft3,discard["page1"])
    divs = [h.parent.parent for h in headers]
    positions = [position_from_style(d['style']) for d in divs]
    
    # Stitch together positions with header data
# Then organize everything into a 2D array (remember
# to concatenate multi-div strings) based on row height
# and center distance. Calculate centers by counting 
# characters and guessing 5.57 pixels per character.
# Calculate rows by looking at vertical separation. 
# Two lines in the same row are about 13 pix apart.
# Two lines in separate rows are about 23 pix apart.


if __name__ == "__main__":
    main()

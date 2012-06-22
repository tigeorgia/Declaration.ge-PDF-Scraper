#!/usr/bin/python
# vim: set fileencoding=utf-8
"""Income declarations parser.

Parses an income declaration from http://declaration.ge, converted
to HTML using pdf2html
"""
import sys
import getopt
#import html5lib
#from html5lib import treebuilders
from bs4 import BeautifulSoup #Deprecated but still the best
import datetime
import json
import codecs
import collections
import os.path

from incomeExceptions import BlankDeclarationError, MalformedDeclarationError
from discard import discard
from tabledetect import detect_table

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
        print "Trying to parse %s" % arg
        parse(arg)


def parse(path):
    suffix = path.split('.')[-1]
    if suffix not in ['html', 'htm']:
        return None

    try:
        f = open(path)
    except IOError as e:
        print "Could not find file."+ repr(e)
        return None
    
    doc = BeautifulSoup(f)
    #doc = html5lib.parse(f,treebuilder="beautifulsoup", encoding="utf-8")
    parsed = {"empty":True}
    try:
        parsed = output(doc,os.path.getsize(path))
        #print repr(parsed).decode("unicode-escape")
        return parsed
    except BlankDeclarationError, e:
        #print "Blank declaration: %s" %path
        scrape_date = doc.find('meta', attrs={u'name':'date'})['content'][:10]
        return {u"decl_id": e.value,u"scrape_date": scrape_date, u"empty": True}
        #pass
    except MalformedDeclarationError, e:
        #pass
        raise MalformedDeclarationError(repr(e.value)+path)
    except Exception, e:
        #pass
        raise Exception(repr(e)+path)
        #print "Very Malformed Declaration %s %s" %(repr(e),path)
    #else:
        #pass
        #print "Success. %s" %path


#def print_list(item):
#    for e in item:
#        if isinstance(e,collections.Iterable) and not isinstance(e,str):
#            print_list(e)
#        else:
#            print(e)


def output(doc,size):
    decl_obj = {} # Storage variable for the data.
    decl_obj[u"scrape_date"] = doc.find('meta', attrs={u'name':'date'})['content'][:10]

    # Document pages are represented by container divs that are
    # children of root element.
    root = doc.find(u'body')
    pages = root.findAll(name=u'div',recursive=False)
    tfx = [None,t1_family,t2_estate,t3_chattel,t4_securities,t5_deposits,t6_cash,t7_entrepreneur,t8_wages,t9_contracts,t10_gifts,t11_misc]
    
    for page in pages:
        pnum = discover_num(page)
        if pnum == 1: #Page 1 has special headers
            page1_headers(page,decl_obj,size)

        # Once headers are parsed, handle tables.
        ft2s = page.findAll(name=u'span',attrs={u"class": u"ft02"})
        tnum = detect_table(pnum,ft2s)
        if tnum == 0:
            if pnum != 1:# Page 1 is only one allowed no table
                raise MalformedDeclarationError("No table detected on %d"%pnum)
            else:
                pass # Skip to the next page.
        else:
            tfx[tnum](page,decl_obj,size) #Parse table
     
    return decl_obj
    #print "Successful"


def is_mkhedruli(char):
    chars = [u'ღ',u'ჯ',u'უ',u'კ',u'ე',u'ნ',u'გ',u'შ',u'წ',u'ზ',u'ხ',u'ც',u'ჟ',u'დ',u'ლ',u'ო',u'რ',u'პ',u'ა',u'თ',u'ვ',u'ძ',u'ფ',u'ჭ',u'ჩ',u'ყ',u'ს',u'მ',u'ი',u'ტ',u'ქ',u'ბ',u'ჰ']
    return char in chars


# Search through headings for one that successfully
# converts to an int, return that.
def discover_num(page):
    # Big text
    headings = page.findAll(name=u'span', attrs={u"class": u"ft01"})
    for head in headings:
        txt = head.contents[0]
        try:
            return int(txt)
        except ValueError:
            continue
    raise MalformedDeclarationError("Could not find a page number")


def position_from_style(style_str):
    """ Constructs a list of positions in the format:
    {'top': y, 'left': x}, where x and y are integers,
    given a CSS style attribute with the format:
    'key:value;key:value;...'"""
    rules = [ rule.split(u":") for rule in style_str.split(u";")]
    pos = {}
    
    for rule in rules:
        if rule[0] == u"top":
            pos[rule[0]] = int(rule[1])
        elif rule[0] == u"left":
            pos[rule[0]] = int(rule[1])
    #print pos
    return pos


def init_field(key,coll,val):
    try:
        a = coll[key]
    except KeyError:
        coll[key] = val


def clean_headers(headers,drop):
    """ Takes an array of BeautifulSoup <span> tags and returns
    an array of <span> tags excluding those found in drop"""
    clean = []
    for h in headers:
        if h.contents[0] not in drop:
            clean.append(h)
    return clean


def de_htmlize(html_str):
    """Removes html escaping."""
    return html_str.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')


def guess_ctr(txt,left):
    """Guesses the center of a string based on its left position
    and number of characters"""
    char_width = 5.57 # For Georgian script, 10px.
    return (char_width*len(txt)/2)+left


def create_columns(data,sep):
    """Merge data into columns if centers are less than sep apart.
    Requires that the incoming data be sorted l-r by center.
    What this does is output an array of arrays, one for each column.
    It checks the distance between the rightmost column center
    and the center of the item being considered, and if the
    distance is less than sep, the item is appended to the end of
    the rightmost column array, and its center is set to the same
    value as the first item in the column array. If the value is
    greater than sep, a new column is created with the object as its
    only item."""
    out = []
    for d in data:
        if len(out) == 0:
            out.append([d])
        else:
            if abs(out[-1][0][u"pos"][u"ctr"] - d[u"pos"][u"ctr"]) < sep:
                out[-1].append(d) # Add to column, ensure equal centers
                out[-1][-1][u"pos"][u"ctr"] = out[-1][0][u"pos"][u"ctr"]
            else:
                out.append([d])
    #print repr(out).decode("unicode-escape")
    return out


def merge_rows(data,sep):
    """Merges data in columns into rows if the vertical separation
    is less than sep. Columns must be sorted top-to-bottom. Modifies
    data in place."""
    delete_later = []
    for a in data: # Data is array of arrays representing columns.
        #print("Before merge: "+str(len(a)))
        base = 0 # Index of item to merge into.
        btop = a[base][u"pos"][u"top"] # Top of bottom line of base item
        for i in range(len(a)):
            if base != i:
                # If the two lines are close together, merge them
                if abs(a[i][u"pos"][u"top"] - btop) < sep:
                    a[base][u"txt"] += " "+a[i][u"txt"]
                    btop = a[i][u"pos"][u"top"]
                    delete_later.append(a[i])
                else: # Move the base to i, and look for merges there
                    base = i
                    btop = a[base][u"pos"][u"top"]
        for d in delete_later:
            a.remove(d)
        del delete_later[:]
        #print("After merge: "+str(len(a)))


# Assumes that the only blank columns will be at the end
# I hope that is accurate.
def assign_names(names,columns):
    out = {}
    for i in range(len(names)):
        if i < len(columns):
            out[names[i]] = columns[i]
        else:
            out[names[i]] = []
    return out


# Searches a column for a row that matches
# height given in base, with a tolerance of sep.
def search_column(base,col,sep):
    for r in col:
        if abs(base[u"pos"][u"top"] - r[u"pos"][u"top"]) < sep:
            return r[u"txt"]
    return u''


def parse_table(pg_div,drop,column_titles):

    all_ft4 = pg_div.findAll(name=u'span', attrs={u"class":u"ft04"})
# Clean out the strings we want to ignore
    headers = clean_headers(all_ft4,drop)
    divs = [h.parent.parent for h in headers]
    positions = [position_from_style(d[u'style']) for d in divs]
    #print("Found %d items total;" %len(all_ft4))
    #print("Kept %d items" %len(headers))

    txt_pos = []
    # Stitch together positions with header data
    for i in range(len(headers)): # i indexes two arrays
        txt = de_htmlize(headers[i].contents[0])
        pos = positions[i]
        pos[u"ctr"] = guess_ctr(txt,pos[u"left"])
        txt_pos.append({u"txt": txt, u"pos": pos})
    #print(txt_pos)

    # Sort based on horizontal centers
    txt_pos.sort(key=lambda c: c[u"pos"][u"ctr"])
    columns = create_columns(txt_pos,50)
    #print("Detected %d columns" %len(columns))
    # 1.Sort each column by 'top'
    for a in columns:
        a.sort(key=lambda c: c[u"pos"][u"top"])

    # 2. Merge nearby lines of text into one table row
    merge_rows(columns, 16)

    fields = assign_names(column_titles,columns)
    # 3.Assume len(columns[0]) = num records
    # 4.Compare tops to assign cells to rows or skip empties
    parsed_table = []

    #print(len(fields["name"]))
    #print(len(fields[column_titles[0]]))
    for row in fields[column_titles[0]]:
        parsed_table.append({})
        for title in column_titles:
            parsed_table[-1][title] = search_column(row,fields[title],10)

    return parsed_table


def page0(pg_div,decl):
    raise MalformedDeclarationError("Illegal page number")


def check_blank (pg_div, decl_id, decl_date, name, size):
    if decl_date or name:
        return

    # Raise if the date or name is blank AND the size is small.
    # 24260 seems to be about what a truly blank declaration takes up
    if (decl_date == None or name == None) and size < 24300:
        raise BlankDeclarationError(unicode(decl_id))

    # Raise if date is blank AND "official hasn't filled in report yet" is present
    notfilled = u"თანამდებობის პირის ქონებრივი მდგომარეობის დეკლარაციის შევსება არაა დასრულებული"
    ft2s = pg_div.findAll(name=u'span', attrs={u"class":u"ft02"})
    for ft2 in ft2s:
        if ft2.contents[0] == notfilled:
            raise BlankDeclarationError(unicode(decl_id))


def page1_ft5s (pg_div, decl):
    ft5s = pg_div.findAll(name=u'span', attrs={u"class":u"ft05"})
    if len(ft5s) == 2:
        # part 1 + <br> + part 2
        decl[u"position"] = ft5s[0].contents[0] + ' ' + ft5s[0].contents[2]
        decl[u"work_contact"] = ft5s[1].contents[0] + ' ' + ft5s[1].contents[2]
    else:
        raise MalformedDeclarationError("Wrong number of FT5s on page 1")


def page1_headers(pg_div,decl,size):
########################
# HEADINGS (FT1)       #
########################
    headings = pg_div.findAll(name=u'span', attrs={u"class":u"ft01"})

    decl_id, decl_date, name = None, None, None

    for head in headings:
        txt = head.contents[0]
        if txt in discard[u"page1"]:
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

    check_blank(pg_div, decl_id, decl_date, name, size)
    decl[u"decl_id"] = decl_id
    decl[u"decl_date"] = decl_date
    decl[u"name"] = name

########################
# POSITION (FT5)       #
########################
    job = pg_div.find(name=u'span', attrs={u"class":u"ft05"})
    if job != None: #The job might also be in the FT3s
        decl[u"position"] = job.contents[0]
########################
# DOB, ADDRESS (FT3)   #
########################
    headers = pg_div.findAll(name=u'span', attrs={u"class":u"ft03"})
    divs = [h.parent.parent for h in headers]
    positions = [position_from_style(d[u'style']) for d in divs]

    txt_pos = []
    # Stitch together positions with header data
    for i in range(len(headers)): # i indexes two arrays
        txt = headers[i].contents[0]
        pos = positions[i]
        txt_pos.append({u"txt": txt, u"pos": pos})

    txt_pos.sort(key=lambda c: c[u"pos"][u"top"])

    if len(headers) == 3: # There's a job
        decl[u"position"] = txt_pos[0]["txt"]
        decl[u"work_contact"] = txt_pos[1]["txt"]
        decl[u"place_dob"] = txt_pos[2]["txt"]
    elif len(headers) == 2:
        decl[u"work_contact"] = txt_pos[0]["txt"]
        decl[u"work_contact"] = txt_pos[1]["txt"]
    elif len(headers) == 1: # if contains <br>, then pdftohtml marks it as ft05
        decl[u"place_dob"] = headers[0].contents[0]
        page1_ft5s(pg_div, decl)
    else:
        raise MalformedDeclarationError("Wrong number of FT3s")


def page1_headers_t1(pg_div,decl,size):
    page1_headers(pg_div,decl,size)
    t1_family(pg_div,decl,size)


def t1_family(pg_div,decl,size):
########################
# FAMILY (FT4)         #
########################
    init_field(u"family",decl,[])
    column_titles = [u"name",u"surname",u"pob",u"dob",u"relation"]
    decl[u"family"].extend(parse_table(pg_div,discard[u"page1"],column_titles))


def t2_estate(pg_div,decl,size):
    init_field(u"real_estate",decl,[])
    column_titles = [u"name_shares",u"prop_type",u"loc_area",u"co_owners"]
    decl[u"real_estate"].extend(parse_table(pg_div,discard[u"page2"],column_titles))


def t3_chattel(pg_div,decl,size):
    init_field(u"chattel",decl,[])
    column_titles = [u"name_shares",u"prop_type",u"description",u"co_owners"]
    decl[u"chattel"].extend(parse_table(pg_div,discard[u"page3"],column_titles))


def t4_securities(pg_div,decl,size):
    init_field(u"securities",decl,[])
    column_titles = [u"name",u"issuer",u"type",u"price",u"quantity"]
    decl[u"securities"].extend(parse_table(pg_div,discard[u"page4"],column_titles))


def t5_deposits(pg_div,decl,size):
    init_field(u"deposits",decl,[])
    column_titles = [u"name",u"bank",u"type",u"balance"]
    decl[u"deposits"].extend(parse_table(pg_div,discard[u"page5"],column_titles))


def t6_cash(pg_div,decl,size):
    init_field(u"cash",decl,[])
    column_titles = [u"name",u"amt_currency"]
    decl[u"cash"].extend(parse_table(pg_div,discard[u"page6"],column_titles))


def t7_entrepreneur(pg_div,decl,size):
    init_field(u"entrepreneurial",decl,[])
    column_titles = [u"name",u"corp_name_addr",u"particn_type",u"register_agency",u"particn_date",u"income_rec"]
    decl[u"entrepreneurial"].extend(parse_table(pg_div,discard[u"page7"],column_titles))


def t8_wages(pg_div,decl,size):
    init_field(u"wages",decl,[])
    column_titles = [u"name",u"desc_workplace",u"desc_job",u"income_rec"]
    decl[u"wages"].extend(parse_table(pg_div,discard[u"page8"],column_titles))


def t9_contracts(pg_div,decl,size):
    init_field(u"contracts",decl,[])
    column_titles = [u"name",u"desc_value",u"date_period_agency",u"financial_result"]
    decl[u"contracts"].extend(parse_table(pg_div,discard[u"page9"],column_titles))


def t10_gifts(pg_div,decl,size):
    init_field(u"gifts",decl,[])
    column_titles = [u"name",u"desc_value",u"giver_rel"]
    decl[u"gifts"].extend(parse_table(pg_div,discard[u"page10"],column_titles))


def t11_misc(pg_div,decl,size):
    init_field(u"other_inc_exp",decl,[])
    column_titles = [u"recip_issuer",u"type",u"amount"]
    decl[u"other_inc_exp"].extend(parse_table(pg_div,discard[u"page11"],column_titles))



if __name__ == "__main__":
    main()

#!/usr/bin/python
# vim: set fileencoding=utf-8

#Asset declaration scraper -- scrapes and processes http://declaration.ge
#Copyright 2012 Transparency International Georgia http://transparency.ge
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Import income declaration reports into couchdb database.

Usage:
$ python db.py DIRECTORY

DIRECTORY holds the reports as PDF + converted to HTML
"""

import os, sys, getopt, hashlib, marshal
import couchdb
from uuid import uuid4 # couchdb doc: uuids client-side, HTTP POST not idempotent

import parse
from incomeExceptions import BlankDeclarationError, MalformedDeclarationError



# database configuration 
DB = {
    'url': 'http://127.0.0.1:5984',
    'name': 'declarations',
}



def parse_opts ():
    """Parse command-line options.
    
    @return list of directories to look for declarations to add
    """
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

    return args



def get_db ():
    """Get database object.

    Looks in the global DB dictionary for the database server URL and the
    database name.

    @return database object
    """
    # don't catch exeptions, we want to crash here
    couch = couchdb.client.Server(DB['url'])
    return couch[DB['name']]



def mkhash (doc):
    """Create a hash value of the scraped data

    @param doc document containing scraped data
    @return string message digest of the scraped data
    """
    # remove scrape date from hash
    hashdoc = doc.copy()
    del hashdoc['scrape_date']

    # (c)pickling yields different hash on same data...
    #dump = cPickle.dumps(hashdoc)
    dump = marshal.dumps(hashdoc)
    return hashlib.sha256(dump).hexdigest()



def add_to_db (db, doc):
    """Add given document to database.

    Or not if it already exxists. Also, be verbose about the action taken.

    @param db database object
    @param doc declaration document
    @return boolean if document was added
    """
    view = db.view('basic/by_decl_id')
    hits = view[doc['decl_id']]

    if len(hits) > 0: # decl_id exists already
        msg = "Duplicate declaration %s... " % doc['decl_id']

        hashes = [db[h.id]['hash'] for h in hits if 'hash' in db[h.id]]
        if doc['hash'] in hashes:
            print msg + "Hash has not changed, skipping."
            return False
        else:
            print msg + "New hash, adding new document."
    else:
        print "Adding declaration %s" % doc['decl_id']

    uuid = uuid4().hex
    db[uuid] = doc
    return True



def file_ok (filename):
    """Check if given filename is a file we want to work with.

    @param filename name of file to check
    @return boolean if file is ok
    """
    if os.path.isdir(filename):
        return False

    suffix = filename.split('.')[-1]
    if suffix not in ['html', 'htm']:
        return False

    return True



def main ():
# process arguments
    args = parse_opts()
    home = os.getcwd()
    db = get_db()
    tot_ct = prs_ct = add_ct = 0
    for arg in args:
        files = os.listdir(arg)
        os.chdir(arg)
        for f in files:
            if not file_ok(f): continue

            tot_ct += 1
            try:
                doc = parse.parse(f)
                prs_ct += 1
                if doc:
                    doc['hash'] = mkhash(doc)
                    if add_to_db(db, doc):
                        add_ct += 1
            except MalformedDeclarationError:
                print "Malformed Declaration: %s" % repr(f)
        os.chdir(home)

    print "Considered %d files. Successfully parsed %d, added %d new documents to db." % (tot_ct, prs_ct, add_ct)



if __name__ == "__main__":
    main()

import couchdb
import parse
from incomeExceptions import BlankDeclarationError, MalformedDeclarationError
import os, sys, getopt

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
    home = os.getcwd()
    couch = couchdb.client.Server("http://127.0.0.1:5984")
    db = couch["declarations"]
    tot_ct = 0
    prs_ct = 0
    add_ct = 0
    for arg in args:
        files = os.listdir(arg)
        os.chdir(arg)
        rows = db.view('basic/by_decl_id')
        for f in files:
            tot_ct += 1
            try:
                uuid = couch.uuids()[0]
                doc = parse.parse(f)
                prs_ct += 1
# Don't copy declarations we've already scraped.
                if len(rows[doc["decl_id"]]) == 0:
                    db[uuid] = doc
                    add_ct += 1
            except MalformedDeclarationError:
                print "Malformed Declaration: %s"%repr(f)
        os.chdir(home)

    print("Considered %d files. Parsed %d, added %d new files to db." %(tot_ct,prs_ct,add_ct))

if __name__ == "__main__":
    main()

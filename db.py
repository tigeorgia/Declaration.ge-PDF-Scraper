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
    i = 0
    for arg in args:
        files = os.listdir(arg)
        os.chdir(arg)
        for f in files:
            try:
                uuid = couch.uuids()[0]
                doc = parse.parse(f)
                db[uuid] = doc
            except MalformedDeclarationError:
                pass
        os.chdir(home)

if __name__ == "__main__":
    main()

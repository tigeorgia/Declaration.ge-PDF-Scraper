#!/usr/bin/env python
"""
Retrieve data from views (as defined in forexport.json) and write them as CSV files
to disk.

Usage: csv.py OUTDIR
"""
import sys, os, couchdb

DB = {
    'url': 'http://localhost:5984',
    'name' : 'd12'
}
VIEW_ROOT = 'forexport/'
VIEWS = [
    'biography', 'other_incl_expenses', 'property', 'wages', 'real_estate',
    'entrepreneurial', 'gifts', 'cash', 'deposits', 'contracts', 'family',
    'securities'
]
CSV = {
    'sep': '|',
    'ext': '.csv'
}



def get_rows (db, name):
    """DB returns duplicates by scrape_date, so we have to filter it here.

       keys[0] == decl_id
       keys[1] == scrape_date
    """
    # descending=True makes the rows with latest scrape_date first
    view = db.view(VIEW_ROOT + name, descending=True)
    filtered = []
    scrape_date = ''
    decl_id = ''
    for row in view.rows:
        if decl_id != row.key[0]: # next doc
            decl_id = row.key[0]
            scrape_date = row.key[1]

        if row.key[1] == scrape_date:
            filtered.append(row)

    return filtered



def run_view (db, outdir, name):
    """Write the rows of a single view into a CSV file."""
    csv = outdir + name + CSV['ext']
    print 'Writing %s' % csv

    rows = get_rows(db, name)
    out = []
    for row in rows:
        data = []
        for k in row.key:
            if k: data.append(k.encode('utf-8'))
        for v in row.value:
            if v: data.append(v.encode('utf-8'))
        out.append(CSV['sep'].join(data))

    with open(csv, 'w') as fh:
        fh.write("\n".join(out))
        fh.write("\n")



def run (outdir):
    """Run the CSV writing process."""
    couch = couchdb.client.Server(DB['url'])
    db = couch[DB['name']]

    for name in VIEWS:
        run_view(db, outdir, name)



if __name__ == '__main__':
    try:
        outdir = sys.argv[1]
        if outdir[-1] != os.sep: outdir += os.sep
    except IndexError:
        print __doc__
        sys.exit(1)

    run(outdir)

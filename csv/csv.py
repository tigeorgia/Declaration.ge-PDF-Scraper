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
Retrieve data from views (as defined in forexport.json) and write them as CSV files
to disk.

Usage: csv.py OUTDIR
"""
import sys, os, couchdb

DB = {
    'url': 'http://localhost:5984',
    'name' : 'declarations'
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
        data = ''
        for k in row.key:
            if k: data += k.encode('utf-8')
            data += CSV['sep']
        for v in row.value:
            if v: data += v.encode('utf-8')
            data += CSV['sep']
        out.append(data[:-1])

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

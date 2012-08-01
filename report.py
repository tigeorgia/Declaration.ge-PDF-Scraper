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
Show differences in the same declaration between the latest two scrape runs.
The output format used is HTML.

Usage:
$ python report.py > result.html
"""

import sys, datetime
from db import get_db
from dictdiffer import DictDiffer

TRCLASS = ['odd', 'even']

def print_header ():
    title = 'Declaration Income - Diff Report, %s' % datetime.date.today()

    output = []
    output.append('<html><head>')
    output.append('<title>%s</title>' % title)
    output.append('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />')
    output.append('<style type="text/css">')
    output.append('h2 { margin-top: 50px; }')
    output.append('table { width: 100%; }')
    output.append('td { vertical-align: top; padding-bottom: 50px; }')
    output.append('tr.odd { background-color: #eee; }')
    output.append('tr.even { background-color: #ddd; }')
    output.append('</style></head><body>')
    output.append('<h1>%s</h1>' % title)
    print "\n".join(output)



def print_footer (diffcount, total):
    output  = []
    output.append('<p>Found differences in %d out of %d declarations</p>' % (diffcount, total))
    output.append('</body></html>')
    print "\n".join(output)




def upformat (data):
    if not data: return ''
    output = []

    if isinstance(data, list):
        for d in data:
            output.append('<p>')
            if isinstance(d, dict):
                for k, v in d.iteritems():
                    output.append(' %s: %s<br />' % (k.encode('utf-8'), v.encode('utf-8')))
            else:
                output.append(' ' + d.encode('utf-8'))
            output.append('</p>')
    elif isinstance(data, basestring):
        output.append(' ' + data.encode('utf-8'))
    else:
        output.append(' ' + repr(data))

    return "\n".join(output)



def flatten (data):
    output = []
    for d in data:
        for k, v in d.items():
            output.append(k + ': ' + v)
    return "\n".join(output)



def report_changed (current, past, keys):
    output = []
    excluded = ['_id', '_rev', 'hash', 'scrape_date']

    if len(keys) <= len(excluded):
        return output

    output.append('<h3>Changed between %s and %s</h3>' % (past['scrape_date'], current['scrape_date']))
    output.append('<table>')
    output.append('<th>Type</th>')
    output.append('<th>Scrape %s</th>' % past['scrape_date'])
    output.append('<th>Scrape %s</th>' % current['scrape_date'])

    trclass_idx = 1
    for k in keys:
        if k in excluded: continue
        trclass_idx = (trclass_idx + 1) % 2
        output.append('<tr class="%s">' % TRCLASS[trclass_idx])
        output.append(' <td>%s</td>' % k.encode('utf-8'))
        output.append(' <td>%s</td>' % upformat(past[k]))
        output.append(' <td>%s</td>' % upformat(current[k]))
        output.append('</tr>')
    output.append('</table>')

    return output



def report_added (current, keys):
    output = []

    if len(keys) > 0:
        output.append('<h3>Added by %s</h3>' % current['scrape_date'])
        output.append('<table>')
        trclass_idx = 1
        for k in keys:
            trclass_idx = (trclass_idx + 1) % 2
            output.append('<tr class="%s">' % TRCLASS[trclass_idx])
            output.append(' <td>%s</td>' % k.encode('utf-8'))
            output.append(' <td>' + upformat(current[k]) + '</td>')
            output.append('</tr>')
        output.append('</table>')

    return output



def report_removed (past, keys):
    output = []

    if len(keys) > 0:
        output.append('<h3>Removed since %s</h3>' % past['scrape_date'])
        output.append('<table>')
        trclass_idx = 1
        for k in keys:
            trclass_idx = (trclass_idx + 1) % 2
            output.append('<tr class="%s">' % TRCLASS[trclass_idx])
            output.append(' <td>%s</td>' % k.encode('utf-8'))
            output.append(' <td>' + upformat(past[k]) + '</td>')
            output.append('</tr>')
        output.append('</table>')

    return output



def get_pastcurrent (docs):
    past = {}
    current = {}
    for doc in docs:
        if not past:
            past = doc
            continue

        dt_doc = datetime.datetime.strptime(doc['scrape_date'], '%Y-%m-%d')
        dt_past = datetime.datetime.strptime(past['scrape_date'], '%Y-%m-%d')

        if not current:
            if dt_doc > dt_past:
                current = doc
            else:
                current = past
                past = doc
            continue

        dt_current = datetime.datetime.strptime(current['scrape_date'], '%Y-%m-%d')
        if dt_doc > dt_current:
            past = current
            current = doc
            continue

        if dt_doc > dt_past:
            past = doc
            continue

    return past, current



def print_report (docs):
    if not docs or len(docs) < 2: return 0

    name = ''
    for doc in docs:
        if 'name' in doc:
            name = doc['name'].encode('utf-8')
            break
    output = ['<h2>Differences for declaration %s, %s</h2>' % (docs[0]['decl_id'], name)]

    past, current = get_pastcurrent(docs)

    differ = DictDiffer(current, past)
    output += report_changed(current, past, differ.changed())
    output += report_added(current, differ.added())
    output += report_removed(past, differ.removed())
    output.append('<hr />')

    print "\n".join(output)
    return 1



print_header()
db = get_db()
# use something sorted to iterate on
view = db.view('basic/by_decl_id')
decl_id = None
docs = []
diffcount = 0
total = 0
#for row in view.rows[6777:6780]:
#for row in view.rows[6600:]:
for row in view.rows:
    if row.key != decl_id: # new declaration
        if int(row.key) % 100 == 0:# progress indicator
            sys.stderr.write('.')
            sys.stderr.flush()

        diffcount += print_report(docs)
        total += 1
        docs = []
        decl_id = row.key

    if 'hash' in db[row.id]:
        docs.append(db[row.id])

print_footer(diffcount, total)


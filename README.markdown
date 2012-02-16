Declaration.ge Scraper Suite
============================

[BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/ "Beautiful Soup") is required.

In order to scrape a PDF file downloaded from
[declaration.ge](http://declaration.ge/ "Declaration.ge"), you
will first need to convert it to HTML. To do this, download
[poppler](http://poppler.freedesktop.org/ "pdf to html") and install it. It
contains pdftohtml which is used by scripts/tohtml.
Tested with pdftohtml from poppler 0.16.7, as found in Ubuntu 11.10.

Download the reports:

$ ./scripts/download reports/

Convert them to HTML:

$ ./scripts/tohtml reports/ reports/

Then run:

$ python ./parse.py reports/report-ID.html

to parse the HTML into a Python object. What you do with that object is up to
you. Or to import all reports into a couchdb:

$ python ./db.py reports/

db.py will take a directory of HTML (+ PDF) files, parse them (+ build a hash
of the PDF files), and load them into a CouchDB database.


CSV
---
It also ships with a few tools to export the contents of the database to CSV.

Edit variables HOST and DB in couchctl to connect to your couchdb.
Then install the design document for CSV export into the database (once!):

$ ./scripts/couchctl upview DATABASE csv/forexport.json

Edit dictionary DB in csv/csv.py to connect to your couchdb.
Then you can repeatedly run a python script to collect the CSV data and dump it into a directory:

$ ./csv/csv.py csvdata/


Reports
-------
Once you have gathered some data, you can run the reporting tool to see
differences between the latest two scrape runs. It will output HTML:

$ python ./report.py > result.html


Enjoy.

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

$ scripts/download reports/

Convert them to HTML:

$ scripts/tohtml reports/ reports/

Then run:

$ python parse.py reports/report-ID.html

to parse the HTML into a Python object. What you do with that object is up to
you. Or run:

$ python db.py reports/

db.py will take a directory of HTML (+ PDF) files, parse them (, build a hash
of the PDF files), and load them into a CouchDB database.



It also ships with a few tools to export the contents of the database to CSV.
Install the design document csv/forexport.json into the database:

$ scripts/couchctl upview DATABASE forexport

Then you can run a python script to collect the CSV data and dump it into a directory:

$ csv/csv.py csvdata/


Enjoy.

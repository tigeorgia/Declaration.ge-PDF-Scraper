Declaration.ge Scraper Suite
============================

[BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/ "Beautiful Soup") is required.

NOTE: [declaration.ge](http://declaration.ge "Declaration.ge") recently
added a bunch of archival documents in the form of scanned PDFs. This
created a gap in the database IDs for the non-scanned PDFs that are
downloaded by the download script. To get both sets, you will need to
run the download script twice. The first time, call the script with arguments
'<directory> 0 1000' and the second time '<directory> 43000 1000'.

NOTE: [declaration.ge](http://declaration.ge "Declaration.ge") was
recently updated to include English declarations. The download script
will download Georgian and English declarations into separate folders
("en" and "ka"), but the parse script does not work for English
at the moment, only Georgian. You will need to point the scripts
at reports/ka in order to target the Georgian files only.

In order to scrape a PDF file downloaded from
[declaration.ge](http://declaration.ge/ "Declaration.ge"), you
will first need to convert it to HTML. You will need to use
[poppler](http://poppler.freedesktop.org/ "pdf to html"), which 
contains pdftohtml which is used by scripts/tohtml. However, not all
versions of pdftohtml are guaranteed to work. The source for poppler
0.16.7 is included for your convenience; just follow the compile
instructions and you will be able to find the compiled pdftohtml binary
under poppler-0.16.7/utils. You'll need to change the PDFTOHTML path in
the tohtml script accordingly.

If you just want to scrape everything and output to CSV, simply build
poppler and then run 

scripts/full.sh

Download the reports:

$ ./scripts/download reports/

Convert them to HTML:

$ ./scripts/tohtml reports/ka/ reports/ka/

Then run:

$ python ./parse.py reports/ka/report-ID.html

to parse the HTML into a Python object. What you do with that object is up to
you. Or to import all reports into a couchdb:

$ python ./db.py reports/ka

db.py will take a directory of HTML (+ PDF) files, parse them (+ build a hash
of the PDF files), and load them into a CouchDB database.

Or to dump directly to CSV (pipe-delimited):
$ python ./file_output.py reports/ka

CSV
---
You can directly export to CSV using file_output.py (see above), and a few 
tools are provided to export the contents of a CouchDB database to CSV.

Edit variables HOST and DB in couchctl to connect to your couchdb.
Then install the design document for CSV export into the database (once!):

$ ./scripts/couchctl upview csv/forexport.json

Edit dictionary DB in csv/csv.py to connect to your couchdb.
Then you can repeatedly run a python script to collect the CSV data and dump it into a directory:

$ ./csv/csv.py csvdata/


Reports
-------
Once you have gathered some data, you can run the reporting tool to see
differences between the latest two scrape runs. It will output HTML:

$ python ./report.py > result.html


Enjoy.

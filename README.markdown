The code in this repository operates on HTML files, NOT PDF files.
In order to scrape a PDF file downloaded from [declaration.ge](http://declaration.ge/ "Declaration.ge"), you
will first need to convert it to HTML. To do this, download and run [pdftohtml](http://pdftohtml.sourceforge.net/ "pdf to html")
with the following flags:

pdftohtml -enc "UTF-8" -i -q -c -hidden -noframes infile.pdf outfile.html

Then, you can run python parse.py outfile.html to parse the HTML into a Python
object. What you do with that object is up to you. db.py will take a directory
of HTML files, parse them, and load them into a CouchDB database, if you have
CouchDB installed.

[BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/ "Beautiful Soup") is required.

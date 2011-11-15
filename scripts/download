#!/bin/bash
#
# Download reports on income declarations from declaration.ge
#
# It runs in an infinite loop, counting IDs up. It is stopped if there had
# been 1000 consecutive failed IDs to download.
#
# It takes one optional parameter:
# $1 - directory to write PDF files to
#
#############################################################################

SRC="http://declaration.ge/csb/report/report.seam?id="
STOP=1000
CURL=/usr/bin/curl

#############################################################################

# Setup session
# No longer needed thanks to my awesome blog post.
#curl -c cookies.txt http://declaration.ge
#curl -c cookies.txt -b cookies.txt http://declaration.ge/csb/main.seam
#curl -c cookies.txt -b cookies.txt http://declaration.ge/csb/public.seam
#curl -c cookies.txt -b cookies.txt -d "" http://declaration.ge/csb/public.seam

if [ -n "$1" ]; then
    echo "Entering $1"
    cd $1
fi

c=0
miss=0
while [ $miss -le $STOP ]
do
    echo "Trying report ID $c"
	$CURL --progress-bar --output report-$c.pdf "$SRC$c" 
	if [ ! -e report-$c.pdf ]
	then
		miss=`expr $miss + 1`
	else
		miss=0
	fi
	c=`expr $c + 1`
	#echo $c, $miss
done

if [ -n "$1" ]; then
    echo "Leaving $1"
    cd -
fi

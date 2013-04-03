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
Convert income declaration reports into flat files.

Usage:
$ python db.py DIRECTORY

DIRECTORY holds the reports as PDF + converted to HTML
Output files will be written to DIRECTORY as well
"""

import os, sys, getopt, hashlib, marshal
import codecs
import parse
from incomeExceptions import BlankDeclarationError, MalformedDeclarationError

# This specifies the ordering of the resulting CSV file.
output_ordering = {
    u"header":[
    # First four columns of all files
    # Added for documentation purposes, the header is specified manually.
        u"decl_id",
        u"scrape_date",
        u"name",
        u"decl_date",
    ],
    u"biography":[
        # Added for documentation purposes, the ordering of biography.csv
        # is specified manually.
        u"position",
        u"work_contact",
        u"place_dob",
    ],
    u"family":[
        u"name",
        u"surname",
        u"pob",
        u"dob",
        u"relation",
    ],
    u"real_estate":     [
        u"name_shares",
        u"prop_type",
        u"loc_area",
        u"co_owners",
    ],
    u"chattel":[
        u"name_shares",
        u"prop_type",
        u"description",
        u"co_owners",
    ],
    u"securities":[
        u"name",
        u"issuer",
        u"type",
        u"price",
        u"quantity",
    ],
    u"deposits":[
        u"name",
        u"bank",
        u"type",
        u"balance",
    ],
    u"cash":[
        u"name",
        u"amt_currency",
    ],
    u"entrepreneurial":[
        u"name",
        u"corp_name_addr",
        u"particn_type",
        u"register_agency",
        u"particn_date",
        u"income_rec",
    ],
    u"wages":[
        u"name",
        u"desc_workplace",
        u"desc_job",
        u"income_rec",
    ],
    u"contracts":[
        u"name",
        u"desc_value",
        u"date_period_agency",
        u"financial_result",
    ],
    u"gifts":[
        u"name",
        u"desc_value",
        u"giver_rel",
    ],
    u"other_inc_exp":[
        u"recip_issuer",
        u"type",
        u"amount",
    ],
}

def parse_opts ():
    """Parse command-line options.
    
    @return list of directories to look for declarations to add
    """
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

    return args


def file_ok (filename):
    """Check if given filename is a file we want to work with.

    @param filename name of file to check
    @return boolean if file is ok
    """
    if os.path.isdir(filename):
        return False

    suffix = filename.split('.')[-1]
    if suffix not in ['html', 'htm']:
        return False

    return True

def output_csv(parsed,sep,files):
    """Output a declaration's Python object into CSV files.

    @param parsed the Python object containing the parsed declaration data
    @param sep a string denoting the separator / delimiter
    @param files a dictionary of file objects corresponding to the tables
    within the declaration object. The values for each table will be
    appended to these file objects.
    """
    header_array = []
    for item in [parsed[u"decl_id"],parsed[u"scrape_date"],parsed[u"biography"][0]["name"],parsed[u"decl_date"]]:
        if item:
            header_array.extend([item,sep])
        else:
            header_array.extend([u"",sep])
    header = ''.join(header_array)
    # For each output file (corresponding to tables in the declaration)
    #print header
    for table in files.iterkeys():
        # For each line in the table
        for row in parsed[table]:
            line = ''
            # Append each column's value in the specified order
            for key in output_ordering[table]:
                fld = row[key] if row[key] else u""
                line = line + fld + sep
            files[table].write(header+sep+line[:-1]+"\n")
        
def main ():
# process arguments
    args = parse_opts()
    home = os.getcwd()
    tot_ct = prs_ct = 0
    
# set up output files
    #TODO: Allow specifying at runtime
    filenames = ["biography","family","real_estate","property","securities",
                "deposits","cash","entrepreneurial","wages","contracts",
                "gifts","other_incl_expenses"]
    fieldnames = ["biography","family","real_estate","chattel","securities",
                 "deposits","cash","entrepreneurial","wages","contracts",
                 "gifts","other_inc_exp"]
    ext = ".csv"
    sep = "|"
    out_files = {}

    for arg in args:
        files = os.listdir(arg)
        os.chdir(arg)
        for filename,fieldname in zip(filenames,fieldnames):
            out_files[fieldname] = codecs.open(filename+ext,'a',encoding='utf-8-sig')
        for f in files:
            if not file_ok(f): continue

            tot_ct += 1
            try:
                doc = parse.parse(f)
                prs_ct += 1
                if doc and not doc[u"empty"]:
                    if output_csv(doc,sep,out_files):
                        add_ct += 1
            except MalformedDeclarationError:
                print "Malformed Declaration: %s" % repr(f)
        os.chdir(home)

    for f in out_files.itervalues():
        f.close()
    print "Considered %d files. Successfully parsed %d." % (tot_ct, prs_ct)



if __name__ == "__main__":
    main()

#!/usr/bin/python

from tracker import cot
import datetime
import cgi

print 'Content-Type: text/plain'
print ''

# Temp hack to test last report fetch
#update_last_cot_report (datetime.date (2009, 10, 13))
form = cgi.FieldStorage ()

if not form.has_key ("year"):
    print "You must specify year to fetch"
    exit (0)

year = int (form["year"].value)

print "Result: ", cot.process_cot_year_archive (year)

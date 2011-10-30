#!/usr/bin/python

from tracker import  cot
import datetime

print 'Content-Type: text/html'
print ''

print "<html><body>"

# Temp hack to test last report fetch
#update_last_cot_report (datetime.date (2009, 10, 20))

last = cot.COT_Last.all ().fetch (1)
if len (last) == 0:
    from_date = datetime.date (1900, 1, 1)
else:
    from_date = last[0].date

print 'From date: ', from_date, "<br>"
to_date = cot.COT_Last_Provider ().get ()
print 'To date: ', to_date, "<br>"

if from_date == to_date:
    print 'Nothing to fetch<br>'
elif (to_date - from_date).days < 14:
    print 'Fetch only the last report. Result = ', process_last_cot_report (), "<br>"
else:
    print 'Before you can download periodical reports, you need to load annual data for these years:<ul>'
    for y in range (max (1995, from_date.year), to_date.year+1):
        print "<li><a href='fetch-cot-year?year=%d'>%d</a></li>" % (y, y)
    print "</ul>"

print "</body></html>"

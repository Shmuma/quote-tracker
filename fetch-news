#!/usr/bin/python

from tracker import news

print 'Content-Type: text/plain'
print ''

res = news.fetch_week ()
skipped = new = 0

for obj in res:
    if news.record_exists (obj):
        skipped += 1
    else:
        new += 1
        obj.save ()
print "Total = %d, skipped = %d, saved = %d" % (len (res), skipped, new)

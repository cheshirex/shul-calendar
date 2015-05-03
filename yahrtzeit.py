#!/usr/bin/python
# -*- coding: UTF-8 -*-

import hebcalendar
import sys
import codecs
import itertools
from convertdate import hebrew, gregorian, utils

def usage():
	print 'yahrtzeit.py Yahrtzeit Generation script'
	print 'Usage: yahrtzeit.py <Jewish year> <name of data file>'

dates = {}

if len(sys.argv) != 3:
	usage()
	sys.exit(1)

year = int(sys.argv[1])

inputFile = sys.argv[2]

# Read in file, build DB of dates
for line in codecs.open(inputFile, encoding='utf-8'):
	# Throw away anything after a comment character
	line = line.split('#')[0].strip()
	
	if len(line) == 0:
		continue
		
	name, date, info = [x.strip() for x in line.split(',', 3)]
	
	date = date.split('.', 3)
	
	if not hebrew.leap(year) and date[1] == '13':
		date[1] = '12'
	
	jd = hebrew.to_jd(year, int(date[1]), int(date[0]))
	
	if jd not in dates:
		dates[jd] = []
	
	dates[jd].append({'name': name, 'info': info, 'date': date})

# Get full date list from hebcalendar, filter for shabbat, chag
hebcalendar.setFilter(['shabbat', 'chag', 'RH', 'YK'])
holidays = hebcalendar.getYear(year, 'Israel')

# Okay, now I have a dict of shabbat/chagim, and a separate dict of yahrtzeits. Need to work through them both.

lastShabbat = 0
lastShabbatName = ''

yahrtzeits = sorted(dates)

out = codecs.open('yahrtzeitsFor%d.txt' % year, 'w', encoding='utf-8')

for shabbat in sorted(holidays):
	day = holidays[shabbat]
	name = u', '.join(a['hebrew'] for a in day['fullnames'])
	greg = '%04d.%02d.%02d' % day['gregorian']
	heb = '%04d.%02d.%02d' % day['hebrew']
	name += u' - %s / %s:' % (greg, heb)
	
	yDates = [y for y in yahrtzeits if y > lastShabbat and y <= shabbat]

	if len(yDates) > 0:
		out.write(lastShabbatName + u'\n')
		for date in sorted(yDates):
			for y in dates[date]:
				out.write(u"* %s - %s - %s\n" % (y['name'], '.'.join(reversed(y['date'])), y['info']))


	lastShabbat = shabbat
	lastShabbatName = name
	

	
	
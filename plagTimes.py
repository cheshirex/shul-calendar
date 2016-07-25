#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import codecs

from lib import hebcalendar, times

location = 'Israel'

maariv = u'20:10'

year = int(sys.argv[1])
month = None
if len(sys.argv) > 2:
	month = int(sys.argv[2])

monthName = None
holidays = None
if month:
	holidays = hebcalendar.getMonth(year, month, location)
else:
	holidays = hebcalendar.getYear(year, location)

times.setLocation('Givat Zeev','Israel',31.86,35.17,'Asia/Jerusalem',0)

out = codecs.open('plag.txt', 'w', encoding='utf-8')

for jd in sorted(holidays):
	day = holidays[jd]
	if day['date'].weekday() == hebcalendar.weekday['shabbat']:
		dayTimes = times.getTimes(day['date'])
		shabbatName = None
		for fullname in day['fullnames']:
			if (u'שבת' in fullname['hebrew'] or u'פסח' in fullname['hebrew']) and not any(x in fullname['hebrew'] for x in (u'הגדול', u'חזון', u'נחמו')):
				shabbatName = fullname['hebrew']
		
		if shabbatName == None:
			continue
		
		out.write(shabbatName + ": " + dayTimes['plagMincha'].strftime("%H:%M") + '\n')
	
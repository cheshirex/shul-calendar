#!/usr/bin/python
# -*- coding: UTF-8 -*-

#import times
import hebcalendar
import sys
import datetime
import io
from oleHelper import *

from convertdate import hebrew, utils

year = int(sys.argv[1])

location = 'Israel'
holidays = hebcalendar.getYear(year, location)

# Excel version
sheet = createSheet()

row = 2

for jd in sorted(holidays):
	day = holidays[jd]
	shlishit = True

	if any(x in day['type'] for x in ('RH','YK','shabbat','chag','purim')):
		if 'purim' in day['type']:
			# four megillah readings
			text = u'אסתר - קריאה %s'
			for a in (u"א' בלילה", u"ב' בלילה", u"א' ביום", u"ב' ביום"):
				setRow(sheet, row, day['hebrewWritten'], text % a, False)
				row += 1
			continue

		names = []
		for name in day['fullnames']:
			# If the name contains "of chol hamoed", it's just the day count, so skip it
			if u'דחוה"מ' in name['hebrew'] or u'סליחות' in name['hebrew'] or u'בעומר' in name['hebrew'] or u'ערב' in name['hebrew']:
				continue
			# Take out "Shabbat" or "Parshat"
			name = name['hebrew'].replace(u'שבת ', u'').replace(u'פרשת ',u'')

			if u'ראש חודש' in name:
				name = u'ראש חודש'

			if u'דחנוכה' in name:
				name = u'חנוכה'

			if u'פורים' in name:
				name = u'אסתר - קריאה '

			names.append(name)


		text = ' - '.join(a for a in reversed(names))

		if u'שבועות' in text:
			setRow(sheet, row, day['hebrewWritten'], text, False)
			row += 1
			setRow(sheet, row, day['hebrewWritten'], u"מגילת רות - מנין א'", False)
			row += 1
			setRow(sheet, row, day['hebrewWritten'], u"מגילת רות - מנין ב'", False)
			row += 1
			continue

		# If shabbat/chag, add megillah
		elif day['date'].weekday() == hebcalendar.weekday['shabbat'] and (u'סוכות' in text or u'פסח' in text):
			# add megillah
			setRow(sheet, row, day['hebrewWritten'], text, False)
			row += 1
			megillah = None
			if u'סוכות' in text:
				megillah = u'קהלת'
			else:
				megillah = u'שיר השירים'
			setRow(sheet, row, day['hebrewWritten'], u"מגילת %s" % megillah, False)
			row += 1
			continue

		elif 'chag' in day['type'] or ('shabbat' in day['type'] and 'CH' in day['type']):
			# Name of chag, cross out seudah shlishit
			shlishit = False

		setRow(sheet, row, day['hebrewWritten'], text, shlishit)
		row += 1

saveSheet(sheet, year)
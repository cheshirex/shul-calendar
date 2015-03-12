#!/usr/bin/python
# -*- coding: UTF-8 -*-

#import times
import calendar
import sys
import datetime
import io

from convertdate import hebrew, utils

year = int(sys.argv[1])

location = 'Israel'
holidays = calendar.getYear(year, location)

file = io.open('parsha_signup.csv','w',encoding='utf8')
# Insert BOM marker to ensure the file is seen as UTF8
file.write(u'\ufeff')
file.write(u'%s, %s, %s, %s\n' % (u'תאריך', u'פרשה', u'בעל קורא', u'תורם סעודה שלישית'))

for jd in sorted(holidays):
	day = holidays[jd]
	
	if any(x in day['type'] for x in ('RH','YK','shabbat','chag','purim')):
		if 'purim' in day['type']:
			# four megillah readings
			text = day['hebrewWritten'] + ',' + u'אסתר - קריאה %s' + ',,' + 'XXXXXXXXX'
			file.write(text % u"א' בלילה" + '\n')
			file.write(text % u"ב' בלילה" + '\n')
			file.write(text % u"א' ביום" + '\n')
			file.write(text % u"ב' ביום" + '\n')
			continue
			
		text = day['hebrewWritten'] + ','
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
		
		
		text += ' - '.join(a for a in reversed(names)) + ',,'
		
		if u'שבועות' in text:
			text += 'XXXXXXXXX'
			text += '\n' + day['hebrewWritten'] + ',' + u"מגילת רות - מנין א'" + ',,' + 'XXXXXXXXX'
			text += '\n' + day['hebrewWritten'] + ',' + u"מגילת רות - מנין ב'" + ',,' + 'XXXXXXXXX'
		
		# If shabbat/chag, add megillah
		elif day['date'].weekday() == calendar.weekday['shabbat'] and (u'סוכות' in text or u'פסח' in text):
			# add megillah
			text += 'XXXXXXXXX'
			megillah = None
			if u'סוכות' in text:
				megillah = u'קהלת'
			else:
				megillah = u'שיר השירים'
			text += '\n' + day['hebrewWritten'] + ',' + u"מגילת %s" % megillah + ',,' + 'XXXXXXXXX'
		
		elif 'chag' in day['type'] or ('shabbat' in day['type'] and 'CH' in day['type']):
			# Name of chag, cross out seudah shlishit
			text += 'XXXXXXXXX'
			
		
			
		file.write(text + '\n')
		
file.close()
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import hebcalendar
import sys
import codecs
import uuid
import datetime

numbers = ['', u'אחד', u'שנים', u'שלושה', u'ארבעה', u'חמשה', u'ששה', u'שבעה', u'שמונה', u'תשעה']
numbersTen = ['', u'עשר', u'עשרים', u'שלושים', u'ארבעים']

def getSfirahText(day):
	text = u"בָּרוּךְ אַתָּה ה' אֱלהֵינוּ מֶלֶךְ הָעולָם, אֲשֶׁר קִדְּשָׁנוּ בְּמִצְותָיו וְצִוָּנוּ עַל סְפִירַת הָעומֶר"
	text += u'\\n'

	if day == 1:
		text += u'היום יום אחד בעומר'
	elif day == 2:
		text += u'היום שני ימים בעומר'
	elif day == 10:
		text += u'היום עשרה ימים, שהם שבוע אחד ושלשה ימים בעומר'
	else:
		text += u'היום '
		text += numbers[day % 10]

		if day % 10 and day > 20:
			text += u' ו'
		if day > 10:
			if day < 20:
				text += u' '
			text += numbersTen[day / 10]
			text += u' יום'
		else:
			text += u' ימים'

		if day >= 7:
			text += u', שהם '
			if day / 7 == 1:
				text += u'שבוע אחד'
			elif day / 7 == 2:
				text += u'שני שבועות'
			else:
				text += numbers[day / 7]
				text += u' שבועות'
			if day % 7 == 1:
				text += u' ויום אחד'
			elif day % 7 == 2:
				text += u' ושני ימים'
			elif day % 7:
				text += u' ו'
				text += numbers[day % 7]
				text += u' ימים'
		text += u' בעומר'

	text += u'\\n'
	text += u"הָרַחֲמָן, הוּא יַחֲזִיר לָנוּ עֲבודַת בֵּית הַמִּקְדָּשׁ לִמְקומָהּ בִּמְהֵרָה בְּיָמֵינוּ, אָמֵן סֶלָה"

	text += u'\\n\\nהערות ל:\\ndan.bernst@gmail.com'

	return text

myUuid = uuid.UUID('{023e9cde-ab09-4611-a43f-dac7b1ce77b3}')

def usage():
	print 'sfirah.py Sfirah calendar Generation script'
	print 'Usage: sfirah.py <Jewish year>'


if len(sys.argv) != 2:
	usage()
	sys.exit(1)

year = int(sys.argv[1])
hebcalendar.setFilter(['omer'])
sfirah = hebcalendar.getYear(year, 'Israel')

out = codecs.open('sfirahFor%d.ics' % year, 'w', encoding='utf-8')

out.write('BEGIN:VCALENDAR\r\n')
out.write('VERSION:2.0\r\n')
out.write('PRODID:sfirahCalendarGenerator_by_Daniel_Bernstein\r\n')

dayCounter = 1

for day in sorted(sfirah):
	date = sfirah[day]['gregorian']
	date = datetime.date(date[0],date[1],date[2]) - datetime.timedelta(days=1)
	greg = date.strftime('%Y%m%d')
	out.write('BEGIN:VEVENT\r\n')
	out.write('UID:%s\r\n' % uuid.uuid3(myUuid, '%d' % dayCounter).hex)
	timestamp = ':%sT203000' % greg
	out.write('DTSTART%s\r\n' % timestamp)
	out.write('DTEND%s\r\n' % timestamp)
	out.write(u'SUMMARY:ספירת העומר\r\n')
	text = getSfirahText(dayCounter)
	out.write('DESCRIPTION:%s\r\n' % text)
	out.write('CONTACT:dan.bernst@gmail.com\r\n')
	out.write('BEGIN:VALARM\r\n')
	out.write('TRIGGER:-PT0M\r\n')
	out.write('ACTION:DISPLAY\r\n')
	out.write('DESCRIPTION:%s\r\n' % text)
	out.write('END:VALARM\r\n')
	out.write('END:VEVENT\r\n')
	dayCounter += 1

out.write('END:VCALENDAR\r\n')

out.close()
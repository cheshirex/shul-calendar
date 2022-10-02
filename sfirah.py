#!/usr/bin/python
# -*- coding: UTF-8 -*-

import hebcalendar
import sys
import codecs
import uuid
import datetime

numbers = ['', u'אחד', u'שנים', u'שלושה', u'ארבעה', u'חמשה', u'ששה', u'שבעה', u'שמונה', u'תשעה']
numbersTen = ['', u'עשר', u'עשרים', u'שלושים', u'ארבעים']


def get_sfirah_text(cur_day):
	output = u"בָּרוּךְ אַתָּה ה' אֱלהֵינוּ מֶלֶךְ הָעולָם, אֲשֶׁר קִדְּשָׁנוּ בְּמִצְותָיו וְצִוָּנוּ עַל סְפִירַת הָעומֶר"
	output += u'\\n'

	if cur_day == 1:
		output += u'היום יום אחד בעומר'
	elif cur_day == 2:
		output += u'היום שני ימים בעומר'
	elif cur_day == 10:
		output += u'היום עשרה ימים, שהם שבוע אחד ושלשה ימים בעומר'
	else:
		output += u'היום '
		output += numbers[cur_day % 10]

		if cur_day % 10 and cur_day > 20:
			output += u' ו'
		if cur_day > 10:
			if cur_day < 20:
				output += u' '
			output += numbersTen[cur_day // 10]
			output += u' יום'
		else:
			output += u' ימים'

		if cur_day >= 7:
			output += u', שהם '
			if cur_day // 7 == 1:
				output += u'שבוע אחד'
			elif cur_day // 7 == 2:
				output += u'שני שבועות'
			else:
				output += numbers[cur_day // 7]
				output += u' שבועות'
			if cur_day % 7 == 1:
				output += u' ויום אחד'
			elif cur_day % 7 == 2:
				output += u' ושני ימים'
			elif cur_day % 7:
				output += u' ו'
				output += numbers[cur_day % 7]
				output += u' ימים'
		output += u' בעומר'

	output += u'\\n'
	output += u"הָרַחֲמָן, הוּא יַחֲזִיר לָנוּ עֲבודַת בֵּית הַמִּקְדָּשׁ לִמְקומָהּ בִּמְהֵרָה בְּיָמֵינוּ, אָמֵן סֶלָה"

	output += u'\\n\\nהערות ל:\\ndan.bernst@gmail.com'

	return output


myUuid = uuid.UUID('{023e9cde-ab09-4611-a43f-dac7b1ce77b3}')


def usage():
	print('sfirah.py Sfirah calendar Generation script')
	print('Usage: sfirah.py <Jewish year>')


if len(sys.argv) != 2:
	usage()
	sys.exit(1)

year = int(sys.argv[1])
hebcalendar.set_filter(['omer'])
sfirah = hebcalendar.get_year(year, 'Israel')

out = codecs.open('sfirahFor%d.ics' % year, 'w', encoding='utf-8')

out.write('BEGIN:VCALENDAR\r\n')
out.write('VERSION:2.0\r\n')
out.write('PRODID:sfirahCalendarGenerator_by_Daniel_Bernstein\r\n')

dayCounter = 1

for day in sorted(sfirah):
	date = sfirah[day]['gregorian']
	date = datetime.date(date[0], date[1], date[2]) - datetime.timedelta(days=1)
	greg = date.strftime('%Y%m%d')
	out.write('BEGIN:VEVENT\r\n')
	out.write('UID:%s\r\n' % uuid.uuid3(myUuid, '%d' % dayCounter).hex)
	timestamp = ':%sT203000' % greg
	out.write('DTSTART%s\r\n' % timestamp)
	out.write('DTEND%s\r\n' % timestamp)
	out.write(u'SUMMARY:ספירת העומר\r\n')
	text = get_sfirah_text(dayCounter)
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

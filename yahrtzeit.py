#!/usr/bin/python
# -*- coding: UTF-8 -*-
from pathlib import Path

from docx.enum.text import WD_COLOR_INDEX

import hebcalendar
import sys
import codecs
from convertdate import hebrew, utils

from docxHelper import DocxHelper

helper = DocxHelper()
worddoc = helper.create_doc(Path().absolute() / "emptyYahrtzeits.docx")


def usage():
	print('yahrtzeit.py Yahrtzeit Generation script')
	print('Usage: yahrtzeit.py <Jewish year> <name of data file>')


def write_entry(worddoc, parsha, data):
	helper.set_header(worddoc, {'text': parsha,
								'size': 12,
								'bold': True,
								'highlight': WD_COLOR_INDEX.BRIGHT_GREEN})
	helper.set_bullet_list(worddoc, data)
	# r.Font.Shading.BackgroundPatternColor = 50500

dates = {}

if len(sys.argv) != 3:
	usage()
	sys.exit(1)

year = int(sys.argv[1])

inputFile = sys.argv[2]

lineNum = 0

# Read in file, build DB of dates
for line in codecs.open(inputFile, encoding='utf-8-sig'):
	# Throw away anything after a comment character
	line = line.split('#')[0].strip()
	lineNum += 1
	if len(line) == 0:
		continue
		
	try:
		name, date, info = [x.strip() for x in line.split(',', 3)]
	except:
		print('Error in line: %d' % lineNum)
		sys.exit(-1)
	date = date.split('.', 3)
	
	if not hebrew.leap(year) and date[1] == '13':
		date[1] = '12'
	
	jd = hebrew.to_jd(year, int(date[1]), int(date[0]))
	
	if jd not in dates:
		dates[jd] = []
	
	dates[jd].append({'name': name, 'info': info, 'date': date})

# Get full date list from hebcalendar, filter for shabbat, chag
hebcalendar.set_filter(['shabbat', 'chag', 'RH', 'YK'])
holidays = hebcalendar.get_year(year, 'Israel')

# Okay, now I have a dict of shabbat/chagim, and a separate dict of yahrtzeits. Need to work through them both.

lastShabbat = 0
lastShabbatName = ''

yahrtzeits = sorted(dates)

# out = codecs.open('yahrtzeitsFor%d.txt' % year, 'w', encoding='utf-8')

for shabbat in sorted(holidays):
	day = holidays[shabbat]
	name = u', '.join(a['hebrew'] for a in day['fullnames'])
	greg = '%04d.%02d.%02d' % day['gregorian']
	heb = '%04d.%02d.%02d' % day['hebrew']
	name += u' - %s / %s:' % (greg, heb)
	
	yDates = [y for y in yahrtzeits if lastShabbat <= y < shabbat]

	if len(yDates) > 0:
		# out.write(lastShabbatName + u'\n')
		parsha = lastShabbatName
		data = []
		for date in sorted(yDates):
			# utils assumes the week starts on Monday, so adjust
			weekday = hebcalendar.hebrew_day_of_week(utils.jwday(date))
			for y in dates[date]:
				data.append(u"%s: %s - %s" % (weekday, y['name'], y['info']))
				# out.write(data)
		write_entry(worddoc, parsha, data)

	lastShabbat = shabbat
	lastShabbatName = name

worddoc.save(f'yahrtzeitsFor{year}.docx')

	
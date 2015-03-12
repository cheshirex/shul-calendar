#!/usr/bin/python
# -*- coding: UTF-8 -*-

import times
import calendar
import sys
import datetime

from convertdate import hebrew, utils

from oleHelper import *
#from docxHelper import *

import win32com.client

### 
# Need to add:
# DST switch

def dstSwitch(day):
	today = day.dst().total_seconds()
	aWeekAway = times.getTimes(day + datetime.timedelta(days=7))['motzei'].dst().total_seconds()
	
	if today == aWeekAway:
		return None
	elif today != 0:
		return "winter"
	else:
		return "summer"

location = 'Israel'

holidayDone = []

maariv = u'20:10'

year = int(sys.argv[1])
month = None
if len(sys.argv) > 2:
	month = int(sys.argv[2])

monthName = None
holidays = None
if month:
	holidays = calendar.getMonth(year, month, location)
else:
	holidays = calendar.getYear(year, location)

times.setLocation('Givat Zeev','Israel',31.86,35.17,'Asia/Jerusalem',0)

worddoc = createDoc()

for jd in sorted(holidays):
	day = holidays[jd]
	dayTimes = times.getTimes(day['date'])
	if monthName == None:
		monthName = calendar.getHebrewMonth(month, 'english')
	
	dstActive = dayTimes['motzei'].dst().total_seconds() != 0
	
	gregDate = day['date'].strftime("%d.%m.%y")

	column1 = []
	column2 = []

	# Holiday types:
	# shabbat
	# chag
	# fast
	# RH (Rosh Hashanah)
	# YK (Yom Kippur)
	# CH (Chol Hamoed)
	# purim
	# SP (Shushan Purim)
	# erevPesach
	if 'RH' in day['type']:
		minchaErev = dayTimes['candleLighting'] + datetime.timedelta(minutes=5)
		shacharit = "07:30"
		dafYomi = "06:45"
		minchaK = dayTimes['motzei'] - datetime.timedelta(minutes=(70 + dayTimes['motzei'].minute % 5))
		
		# Do we say tashlich today?
		tashlich = (day['hebrew'][2] == 1 and day['date'].weekday() != calendar.weekday['shabbat']) \
			or (day['hebrew'][2] == 2 and day['date'].weekday() == calendar.weekday['sunday'])
		
		# Special case -- Erev Rosh Hashana needs to be put on the calendar even though it's technically for 
		# the preceding year
		if day['hebrew'][2] == 1:
			erevDay = day['date'] - datetime.timedelta(days=1)
			header = u'ערב ראש השנה (כ"ט באלול '
			header += erevDay.strftime("%d.%m.%y")
			header += u')'
			setHeader(worddoc, {'text': header})

			column1.append((u"סליחות א'", "05:00"))
			column1.append((u"סליחות ב'", "07:00"))
			if erevDay.weekday() == calendar.weekday['wednesday']:
				column1.append(({'text': u'עירוב תבשילין', 'italic': True},))

			column2.append((u"שחרית מנין א'", "06:05"))
			column2.append((u"שחרית מנין ב'", "08:00"))
			
			createPopulateTable(worddoc, column1, column2)
			setHeader(worddoc, {'text': '\n'})
			
			column1 = []
			column2 = []

		header = u"%s (%s - %s)" % (', '.join(a['hebrew'] for a in day['fullnames']), day['hebrewWritten'], gregDate)
		setHeader(worddoc, {'text': header})
		
		if day['hebrew'][2] == 2:
			column1.append((u"הדלקת נרות אחרי", dayTimes['motzei'].strftime("%H:%M")))
		else:
			column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
		if day['hebrew'][2] == 1:
			column1.append((u"מנחה וערבית", minchaErev.strftime("%H:%M")))
		else:
			column1.append((u"ערבית", dayTimes['motzei'].strftime("%H:%M")))
		column1.append((u"שיעור בדף יומי", dafYomi))
		column1.append((u"שחרית", shacharit))
		# If it's not Erev Shabbat, add motzei chag line
		if day['hebrew'][2] == 2 and dayTimes['noon'].weekday() != calendar.weekday['friday']:
			column1.append((u'ערבית ומוצ"ח', dayTimes['motzei'].strftime("%H:%M")))
		
		if dayTimes['candleLighting'].weekday() != calendar.weekday['shabbat']:
			column2.append((u"תקיעת שופר (משוער)", "09:30"))
		if dayTimes['candleLighting'].weekday() != calendar.weekday['shabbat']:
			column2.append((u"תקיעה שנייה לאחר התפילה",))
		column2.append((u"חצות היום", dayTimes['noon'].strftime("%H:%M")))
		if tashlich:
			column2.append((u"מנחה ותשליח", minchaK.strftime("%H:%M")))
		else:
			column2.append((u"מנחה", (minchaK + datetime.timedelta(minutes=20)).strftime("%H:%M")))
			
		createPopulateTable(worddoc, column1, column2)
		setHeader(worddoc, {'text': '\n'})
		
	elif 'YK' in day['type']:
		minchaErev = dayTimes['candleLighting'] + datetime.timedelta(minutes=5)
		shacharit = "08:00"
		dafYomi = "07:15"
		minchaK = dayTimes['motzei'] - datetime.timedelta(minutes=(70 + dayTimes['motzei'].minute % 5))
		
		setHeader(worddoc, {'text': u"%s (%s - %s)" % (', '.join(a['hebrew'] for a in day['fullnames']), day['hebrewWritten'], gregDate)})
		
		column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
		column1.append((u"כל נדרי וערבית", minchaErev.strftime("%H:%M")))
		column1.append((u"שיעור אחרי שיר הייחוד",))
		column1.append((u"שיעור בדף יומי", dafYomi))
		column1.append((u"שחרית", shacharit))

		column2.append((u'יזכור (משוער)', "10:30"))
		column2.append((u"מנחה", (dayTimes['sunset'] - datetime.timedelta(hours=2, minutes=(15 + dayTimes['motzei'].minute % 5))).strftime("%H:%M")))
		column2.append((u"נעילה (משוער)", (dayTimes['sunset'] - datetime.timedelta(minutes=(60 + dayTimes['sunset'].minute % 5))).strftime("%H:%M")))
		column2.append((u"ערבית ומוצאי חג", dayTimes['motzei'].strftime("%H:%M")))
		
		createPopulateTable(worddoc, column1, column2)
		setHeader(worddoc, {'text': '\n'})
		
	# Shabbat or chag, unless it's Shabbat and 2nd day RC for next month
	elif ('shabbat' in day['type'] or 'chag' in day['type']) and \
		month == day['hebrew'][1]:
	
		# Mincha Erev Shabbat / Chag is 5 minutes after candle lighting
		minchaErev = dayTimes['candleLighting'] + datetime.timedelta(minutes=5)
		# Mincha Ktana is 1:10 before maariv, rounded back to 5 minutes
		minchaK = dayTimes['motzei'] - datetime.timedelta(minutes=(70 + dayTimes['motzei'].minute % 5))
		parentChildLearning = minchaK - datetime.timedelta(minutes=40)
		minchaG = "12:30"
		shacharit = "08:00"
		dafYomi = "07:15"
		isFirstDayPesach = day['hebrew'][1] == 1 and day['hebrew'][2] == 15
		if dstActive:
			minchaG = "13:30"
			shacharit = "08:30"
			dafYomi = "07:45"
		simchatTorah = any([name['english'] == 'Simchat Torah' for name in day['names']])
		chanukah = any([name['english'] == 'Chanukah' for name in day['names']])
		yizkor = None
		if 'yizkor' in day:
			if location == 'Israel' and simchatTorah:
				yizkor = "11:45"
			else:
				yizkor = "10:00"
		
		lateMaariv = dayTimes['motzei'] + datetime.timedelta(minutes=35)
		dayBeforeIsChag = (jd - 1) in holidays and any([x in holidays[jd-1]['type'] for x in ('shabbat','chag','RH')])

		shabbatName = None
		otherName = []
		
		for fullname in day['fullnames']:
			if (u'שבת' in fullname['hebrew'] or u'פסח' in fullname['hebrew']) and not any(x in fullname['hebrew'] for x in (u'הגדול', u'חזון', u'נחמו')):
				shabbatName = fullname['hebrew']
			elif u'סליחות' not in fullname['hebrew']:
				otherName.append(fullname['hebrew'])
		
		header = None
		dayName = ''
		if 'chag' in day['type']:
			dayName = u'יום %s, ' % calendar.hebrewDayOfWeek(day['date'].weekday())
		if shabbatName:
			header = u"%s (%s%s - %s)" % (shabbatName, dayName, day['hebrewWritten'], gregDate)
			if len(otherName):
				header += u' - ' + u', '.join(a for a in otherName)
		else:
			header = u"%s (%s - %s)" % (', '.join(a['hebrew'] for a in day['fullnames']), day['hebrewWritten'], gregDate)
		
		setHeader(worddoc, {'text': header})
		
		if day['date'].weekday() == calendar.weekday['friday']:
			column1.append(({'text': u'עירוב תבשילין', 'italic': True},))
			column2.append(('',),)
		
		if chanukah:
			mincha = "13:30 / " + minchaErev.strftime("%H:%M")
			column1.append((u"מנחה", mincha))
			column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
			column1.append((u"קבלת שבת וערבית", (dayTimes['candleLighting'] + datetime.timedelta(minutes=15)).strftime("%H:%M")))
		elif dayBeforeIsChag:
			if not 'shabbat' in day['type']:
				column1.append((u"הדלקת נרות אחרי", dayTimes['motzei'].strftime("%H:%M")))
				column1.append((u"ערבית", dayTimes['motzei'].strftime("%H:%M")))
			else:
				column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
				column1.append((u"קבלת שבת וערבית", (dayTimes['candleLighting'] + datetime.timedelta(minutes=15)).strftime("%H:%M")))
		elif day['date'].weekday() == calendar.weekday['shabbat']:
			column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
			column1.append((u"מנחה וקבלת שבת", minchaErev.strftime("%H:%M")))
		else:
			column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
			column1.append((u"מנחה וערבית", minchaErev.strftime("%H:%M")))
		if isFirstDayPesach:
			column1.append(((u'חצות הלילה'), (dayTimes['noon'] + datetime.timedelta(hours=12)).strftime("%H:%M")))
		column1.append((u"שיעור בדף יומי", dafYomi))
		if not isFirstDayPesach:
			column1.append((u"שחרית", shacharit))
		if 'shabbat' in day['type'] and day['mevarchim']:
			column1.append(({'text': u"שיעור לנשים אחרי התפילה", 'bold': True},))

		if isFirstDayPesach:
			column2.append((u"שחרית", shacharit))
		if yizkor:
			column2.append((u'יזכור (משוער)', yizkor))
		column2.append((u"מנחה גדולה", minchaG))
		if 'shabbat' in day['type'] and not yizkor:
			column2.append((u"לימוד הורים וילדים", parentChildLearning.strftime("%H:%M")))
		if not 'chag' in day['type'] and not 'CH' in day['type']:
			name = u'מנחה קטנה וס"ש'
		else:
			name = u"מנחה קטנה"
		column2.append((name, minchaK.strftime("%H:%M")))
		if 'shabbat' in day['type']:
			motzei = dayTimes['motzei'].strftime("%H:%M")
			if chanukah:
				# As per Rav Moti's statement, we'll do Maariv 7 minutes early on Chanukah
				column2.append((u'ערבית', '%s / %s' % ((dayTimes['motzei'] - datetime.timedelta(minutes=7)).strftime("%H:%M"),lateMaariv.strftime("%H:%M"))))
				column2.append((u'מוצאי שבת', motzei))
			else:
				column2.append((u'ערבית ומוצ"ש', '%s / %s' % (motzei, lateMaariv.strftime("%H:%M"))))
		elif day['date'].weekday() != calendar.weekday['friday']:
			column2.append((u'ערבית ומוצ"ח', dayTimes['motzei'].strftime("%H:%M")))
		
		switch = dstSwitch(dayTimes['motzei'])
		if 'shabbat' in day['type'] and switch:
			clock = None
			if switch == "summer":
				clock = u"קיץ"
			else:
				clock = u"חורף"
			column1.append(({'text': u'מוצ"ש עוברים לשעון %s' % clock, 'bold': True},))
		
		createPopulateTable(worddoc, column1, column2)
		setHeader(worddoc, {'text': '\n'})
		
	elif 'RC' in day['type']:
		name = [x['hebrew'] for x in day['names'] if u'ראש' in x['hebrew']][0]
		if name not in holidayDone:
			holidayDone.append(name)
			desc = u''
			twoDay = day['hebrew'][2] == 30
			if twoDay:
				desc += u'ימי ' + calendar.hebrewDayOfWeek(day['date'].weekday()) + u' - ' + calendar.hebrewDayOfWeek(day['date'].weekday()+1) + u' - '
				desc += name + u" "
				desc += holidays[jd+1]['date'].strftime("%d.%m.%y")
				desc += u' - ' + day['date'].strftime("%d.%m.%y")
			else:	
				desc += u'יום ' + calendar.hebrewDayOfWeek(day['date'].weekday()) + u' - '
				desc += name + u" "
				desc += day['date'].strftime("%d.%m.%y") 
			if day['date'].weekday() not in (calendar.weekday['friday'], calendar.weekday['shabbat']):
				desc += u' - שחרית ב05:50'
				
			setHeader(worddoc, {'text': desc})
	
	elif 'HR' in day['type']:
		setHeader(worddoc, {'text': u"%s (%s - %s)" % (', '.join(a['hebrew'] for a in day['fullnames']), day['hebrewWritten'], gregDate)})
		
		column1.append((u"קריאת משנה תורה בליל הושענה רבה אחרי ערבית",))
		column1.append((u"שחרית מנין א' ", '05:30'))
		
		column2.append((None, ))
		column2.append((u"שחרית מנין ב'", '07:30'))
		createPopulateTable(worddoc, column1, column2)
		setHeader(worddoc, {'text': '\n'})

	elif 'CH' in day['type']:
		name = [x['hebrew'] for x in day['names'] if u'חוה"מ' in x['hebrew']][0]
		if name not in holidayDone:
			holidayDone.append(name)
			
			dayLast = jd
			while True:
				nextDay = holidays[dayLast+1]
				if not any([u'חוה"מ' in x['hebrew'] for x in nextDay['names']]):
					break
				dayLast += 1

			lastCH = holidays[dayLast]
				
			#any([name['english'] == 'Simchat Torah' for name in day['names']])
			desc = name + u' ימי ' + calendar.hebrewDayOfWeek(day['date'].weekday()) + u' - ' + calendar.hebrewDayOfWeek(lastCH['date'].weekday()) + u', '
			desc += calendar.hebrewNumber(day['hebrew'][2]-1) + u' - ' + calendar.hebrewDate(lastCH['hebrew'][1], lastCH['hebrew'][2], 'hebrew')
			desc += " (" + lastCH['date'].strftime("%d.%m.%y") + ' - ' + day['date'].strftime("%d.%m.%y") + ')'
			
			# Want: חוה"מ פסח - ימי ד'- א', ט"ז - כ' בניסן (20.4.14 –16.4.14) 
			
			desc += u'\n'
			setHeader(worddoc, {'text': desc})
			text = u'שחרית: 06:00 / 07:05 / 08:10'
			text += u' • ' 
			text += u'מנחה וערבית: ' 
			text += (dayTimes['sunset'] - datetime.timedelta(minutes=(15 + dayTimes['sunset'].minute % 5))).strftime("%H:%M")
			text += u' • '
			text += u'ערבית: '
			text += maariv
			text += u'\n'
			setHeader(worddoc, {'text': text, 'size': 12, 'bold': False})
			setHeader(worddoc, {'text': '\n'})
		
	elif 'fast' in day['type']:
		text = u', '.join(a['hebrew'] for a in day['fullnames'])
		text += u' ('
		text += u"יום %s, %s - %s" % (calendar.hebrewDayOfWeek(day['date'].weekday()), day['hebrewWritten'], gregDate)
		text += u') '
		text += u'\n'
	
		setHeader(worddoc, {'text': text})
		mincha = (dayTimes['sunset'] - datetime.timedelta(minutes=(25 + dayTimes['sunset'].minute % 5))).strftime("%H:%M")
		maariv = (dayTimes['fastEnds'] - datetime.timedelta(minutes=(dayTimes['fastEnds'].minute % 5))).strftime("%H:%M")
		
		column1.append((u"תחילת הצום", dayTimes['fastBegins'].strftime("%H:%M")))
		column1.append((u"שחרית", "05:50"))
		column1.append((u"מנחה", mincha))
		
		column2.append((u"ערבית", maariv))
		column2.append((u"סוף הצום", dayTimes['fastEnds'].strftime("%H:%M")))
		createPopulateTable(worddoc, column1, column2)
		setHeader(worddoc, {'text': '\n'})
		
	elif 'esther' in day['type']:
		text = u', '.join(a['hebrew'] for a in day['fullnames'])
		text += u' ('
		text += u"יום %s, %s - %s" % (calendar.hebrewDayOfWeek(day['date'].weekday()), day['hebrewWritten'], gregDate)
		text += u') '
		text += u'\n'
	
		setHeader(worddoc, {'text': text})
		mincha = (dayTimes['sunset'] - datetime.timedelta(minutes=(25 + dayTimes['sunset'].minute % 5))).strftime("%H:%M")
		maariv = (dayTimes['fastEnds'] - datetime.timedelta(minutes=(dayTimes['fastEnds'].minute % 5))).strftime("%H:%M")
		
		column1.append((u"תחילת הצום", dayTimes['fastBegins'].strftime("%H:%M")))
		column1.append((u"שחרית", "05:50"))
		
		column2.append((u"מנחה", mincha))
		column2.append((u"סוף הצום", dayTimes['fastEnds'].strftime("%H:%M")))
		createPopulateTable(worddoc, column1, column2)
		setHeader(worddoc, {'text': '\n'})
		
	elif 'gedaliah' in day['type']:
		slichot = u"סליחות עשרת ימי תשובה: 05:30 / 07:30" + u"\n"
		
		if day['date'].weekday() != calendar.weekday['sunday']:
			setHeader(worddoc, {'text': slichot})
			setHeader(worddoc, {'text': '\n'})
	
		text = u', '.join(a['hebrew'] for a in day['fullnames'])
		text += u' ('
		text += u"יום %s, %s - %s" % (calendar.hebrewDayOfWeek(day['date'].weekday()), day['hebrewWritten'], gregDate)
		text += u') '
		text += u'\n'
	
		setHeader(worddoc, {'text': text})
		mincha = (dayTimes['sunset'] - datetime.timedelta(minutes=(25 + dayTimes['sunset'].minute % 5))).strftime("%H:%M")
		maariv = (dayTimes['fastEnds'] - datetime.timedelta(minutes=(dayTimes['fastEnds'].minute % 5))).strftime("%H:%M")
		
		column1.append((u"תחילת הצום", dayTimes['fastBegins'].strftime("%H:%M")))
		column1.append((u"סליחות ושחרית", "05:30"))
				
		column2.append((u"מנחה", mincha))
		column2.append((u"ערבית", maariv))
		column2.append((u"סוף הצום", dayTimes['fastEnds'].strftime("%H:%M")))
		createPopulateTable(worddoc, column1, column2)
		setHeader(worddoc, {'text': '\n'})

		if day['date'].weekday() == calendar.weekday['sunday']:
			setHeader(worddoc, {'text': slichot})
			setHeader(worddoc, {'text': '\n'})
	
	elif '9av' in day['type']:
		setHeader(worddoc, {'text': u"%s (%s - %s)" % (', '.join(a['hebrew'] for a in day['fullnames']), day['hebrewWritten'], gregDate)})
		
		column1.append((u"תחילת הצום", dayTimes['sunset'].strftime("%H:%M")))
		column1.append((u"ערבית ואיכה", "20:10"))
		column1.append((u"שחרית", "07:00"))
		
		column2.append((u"מנחה", (dayTimes['fast9avEnds']- datetime.timedelta(minutes=70)).strftime("%H:%M")))
		column2.append((u"ערבית", (dayTimes['fast9avEnds']- datetime.timedelta(minutes=5)).strftime("%H:%M")))
		column2.append((u"סוף הצום", dayTimes['fast9avEnds'].strftime("%H:%M")))
		createPopulateTable(worddoc, column1, column2)
		setHeader(worddoc, {'text': '\n'})
		
	elif 'purim' in day['type']:
		maariv = dayTimes['fastEnds'] - datetime.timedelta(minutes=(5 + dayTimes['motzei'].minute % 5))
		if day['date'].weekday() == calendar.weekday['sunday']:
			# If Purim is Motzei Shabbat, give 30 minutes before Maariv
			maariv = dayTimes['motzei'] + datetime.timedelta(minutes=(30 + dayTimes['motzei'].minute % 5))
		secondReading = maariv + datetime.timedelta(hours=2)
		setHeader(worddoc, {'text': u"%s (יום %s, %s - %s)" % (', '.join(a['hebrew'] for a in day['fullnames']), calendar.hebrewDayOfWeek(day['date'].weekday()), day['hebrewWritten'], gregDate)})
		
		column1.append((u"ערבית וקריאת מגילה", maariv.strftime("%H:%M")))
		column2.append((u"שחרית וקריאת מגילה", "07:00"))
		
		column1.append((u"קריאה שניה", secondReading.strftime("%H:%M")))
		column2.append((u"קריאה שניה", "09:30"))
		
		column2.append(( u"מנחה", "13:00"))
		createPopulateTable(worddoc, column1, column2)
		setHeader(worddoc, {'text': '\n'})
		
	elif 'chanuka' in day['type']:
		if 'chanuka' not in holidayDone:
			holidayDone.append('chanuka')
			
			chanuka1 = hebrew.to_jd(year, 9, 25)
			chanuka8 = chanuka1 + 7
			
			# Times according to first day of chanuka.
			dayTimes = times.getTimes(day['date'] - datetime.timedelta(days=(jd - chanuka1)))
			
			day8 = holidays[chanuka8]
						
			desc = u''
			desc += u"חנוכה, ימים " + calendar.hebrewDayOfWeek(day8['date'].weekday()) + '-' + calendar.hebrewDayOfWeek(day8['date'].weekday()) + ' '
			desc +=	u'אור לכ"ה כסלו ' + (day8['date']-datetime.timedelta(days=7)).strftime("%d.%m.%y") + u" עד " 
			desc +=	calendar.hebrewDayOfMonth(day8['hebrew'][2] - 1) + u"טבת "
			desc += day8['date'].strftime("%d.%m.%y")

			setHeader(worddoc, {'text': desc})
			
			column1.append((u"שחרית מנין א'", "05:50"))
			column1.append((u"שחרית מנין ב'", "08:00"))

			column2.append((u"מנחה", (dayTimes['sunset'] - datetime.timedelta(minutes=(15 + dayTimes['sunset'].minute % 5))).strftime("%H:%M")))
			column2.append((u"ערבית", maariv))
			
			for d in range(int(jd-0.5),int(chanuka8+0.5)):
				if holidays[d+0.5]['date'].weekday() == calendar.weekday['friday']:
					# There's a Friday in Chanuka (well, duh, but specifically for the case of Tevet)
					column1.append((u"שחרית מנין א' ביום ו'", "06:00"))
			createPopulateTable(worddoc, column1, column2)
			setHeader(worddoc, {'text': '\n'})
		
	elif 'erevPesach' in day['type']:
		setHeader(worddoc, {'text': u"%s (יום %s, %s - %s)" % (', '.join(a['hebrew'] for a in day['fullnames']), calendar.hebrewDayOfWeek(day['date'].weekday()), day['hebrewWritten'], gregDate)})
		
		column1.append((u"סוף זמן אכילת חמץ", dayTimes['chametzEating'].strftime("%H:%M")))
		column2.append((u"סוף זמן שריפת חמץ", dayTimes['chametzBurning'].strftime("%H:%M")))
		createPopulateTable(worddoc, column1, column2)
		setHeader(worddoc, {'text': '\n'})
	elif 'erevRH' in day['type']:
		desc = u'סליחות: '
		desc += u"%s (%s - %s)" % (', '.join(a['hebrew'] for a in day['fullnames']), day['hebrewWritten'], gregDate)
		desc += u': 07:00 / 05:00\n'
		setHeader(worddoc, {'text': desc})
		setHeader(worddoc, {'text': '\n'})
	elif 'slichot' in day['type']:
		name = day['names'][0]
		if name not in holidayDone:
			holidayDone.append(name)
			
			dayLast = jd
			while True:
				nextDay = holidays[dayLast+1]
				if not 'slichot' in nextDay['type']:
					break
				dayLast += 1

			first = holidays[jd+1]
			if utils.jwday(dayLast) == calendar.weekday['shabbat']:
				dayLast -= 1
			last = holidays[dayLast]
			
			desc = u'סליחות: מוצ"ש '
			desc += u' ('
			desc += u"יום %s, %s - %s" % (calendar.hebrewDayOfWeek(day['date'].weekday()), day['hebrewWritten'], gregDate)
			desc += u'): '
			desc += u'שעה ' + (dayTimes['noon'] - datetime.timedelta(hours=12 ,minutes=(dayTimes['noon'].minute % 5))).strftime("%H:%M")
			desc += u'\n'
			setHeader(worddoc, {'text': desc})
			setHeader(worddoc, {'text': '\n'})
			
			desc = u"סליחות: "
			
			desc += u' ימי ' + calendar.hebrewDayOfWeek(first['date'].weekday()) + u' - ' + calendar.hebrewDayOfWeek(last['date'].weekday()) + u', '
			desc += calendar.hebrewNumber(first['hebrew'][2]-1) + u' - ' + calendar.hebrewDate(last['hebrew'][1], last['hebrew'][2], 'hebrew')
			desc += " (" + last['date'].strftime("%d.%m.%y") + ' - ' + first['date'].strftime("%d.%m.%y") + '): '
			desc += u'07:40 / 05:40'
			desc += u'\n'
			setHeader(worddoc, {'text': desc})
			setHeader(worddoc, {'text': '\n'})
	elif 'rain' in day['type']:
		header = u"אור ל-ז' חשון בערבית "
		header += day['date'].strftime("(%d.%m.%y)")
		text = ' - '
		text += u'מתחילים לומר "ותן טל ומטר לברכה"'
		setHeader(worddoc, {'text': text})
		setHeader(worddoc, {'text': '\n'})
	elif 'omer' in day['type'] and len(day['type']) == 1:
		pass
	else:
		text = u', '.join(a['hebrew'] for a in day['fullnames'])
		text += u' ('
		text += u"יום %s, %s - %s" % (calendar.hebrewDayOfWeek(day['date'].weekday()), day['hebrewWritten'], gregDate)
		text += u') '
		text += u'\n'
		setHeader(worddoc, {'text': text})
		setHeader(worddoc, {'text': '\n'})


saveDoc(worddoc, monthName, year)
	
	

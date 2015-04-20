#!/usr/bin/python
# -*- coding: UTF-8 -*-

##Daylight saving time considerations
##Daily times
##Birkat Hachama
#Additional functionality should allow
##Generate a shabbat schedule
##Generate a monthly schedule
##Configuration of minyan times

from convertdate import hebrew, gregorian, utils
import datetime
import arrow

externalDays = []
filter = []

weekday = {'sunday': 6,
		   'monday': 0,
		   'tuesday': 1,
		   'wednesday': 2,
		   'thursday': 3,
		   'friday': 4,
		   'shabbat': 5}

year = None
location = None

language = ['english','hebrew']
numbers = [u"א'",  u"ב'",  u"ג'",  u"ד'",  u"ה'",  u"ו'",  u"ז'",  u"ח'",  u"ט'",  u"י'", 
		   u'י"א', u'י"ב', u'י"ג', u'י"ד', u'ט"ו', u'ט"ז', u'י"ז', u'י"ח', u'י"ט', u"כ'",
		   u'כ"א', u'כ"ב', u'כ"ג', u'כ"ד', u'כ"ה', u'כ"ו', u'כ"ז', u'כ"ח', u'כ"ט', u"ל'",
		   u'ל"א', u'ל"ב', u'ל"ג', u'ל"ד', u'ל"ה', u'ל"ו', u'ל"ז', u'ל"ח', u'ל"ט', u"מ'",
		   u'מ"א', u'מ"ב', u'מ"ג', u'מ"ד', u'מ"ה', u'מ"ו', u'מ"ז', u'מ"ח', u'מ"ט']

days = [u'ראשון',u'שני',u'שלישי',u'רביעי',u'חמישי',u'שישי',u'שביעי',u'שמיני']		   
		   
def hebrewNumber(number):
	return numbers[number]
	
def hebrewDayOfWeek(number):
	# Expect the day of week as a number from datetime.weekday()
	number = (number + 1) % 7
	if number == 6:
		return u"שבת"
	else:
		return hebrewNumber(number)
	
def hebrewDayOfMonth(number):
	return hebrewNumber(number) + u" ב"
	
def hebrewDayOfChag(number, holiday):
	return hebrewNumber(number) + u" ד" + holiday
	
def englishDayOfChag(number, holiday):
	return u"%s - Day %d" % (holiday, number+1)

def getYearType():
	days = hebrew.year_days(year)
	length = None
	if days in (353, 383):
		length = 'short'
	elif days in (354, 384):
		length = 'normal'
	elif days in (355, 385):
		length = 'long'
	
	rh = utils.jwday(hebrew.to_jd(year, 7, 1))
	
	pesach = utils.jwday(hebrew.to_jd(year, 1, 15))
	
	return (rh, length, pesach)

def leapJoin(type):
	return not hebrew.leap(year)
	
def vayakhel(type):
	return not hebrew.leap(year) and not (type[0] == weekday['thursday'] and type[2] == weekday['sunday'])
	
def behar(type):
	return not hebrew.leap(year) and not (type[0] == weekday['thursday'] and type[2] == weekday['shabbat'])
	
def nitzavim(type):
	return type[0] not in (weekday['monday'],weekday['tuesday'])
	
def chukat(type):
	return location == 'Diaspora' and type[2] == weekday['thursday']
	
def matot(type):
	split = hebrew.leap(year) and type[0] == weekday['thursday']
	if location == 'Israel' and not split:
		if type in ((weekday['monday'], 'long', weekday['shabbat']), (weekday['tuesday'], 'normal', weekday['shabbat']),
					(weekday['thursday'], 'short', weekday['sunday']), (weekday['thursday'], 'long', weekday['tuesday'])):
			split = True
	return not split

months = (   {'english': u'Nisan',    'hebrew': u'ניסן'},
             {'english': u'Iyar',     'hebrew': u'אייר'},
		     {'english': u'Sivan',    'hebrew': u'סיון'},
		     {'english': u'Tamuz',    'hebrew': u'תמוז'},
		     {'english': u'Av',       'hebrew': u'אב'},
		     {'english': u'Elul',     'hebrew': u'אלול'},
		     {'english': u'Tishrei',  'hebrew': u'תשרי'},
		     {'english': u'Cheshvan', 'hebrew': u'חשון'},
		     {'english': u'Kislev',   'hebrew': u'כסלו'},
		     {'english': u'Tevet',    'hebrew': u'טבת'},
		     {'english': u'Shvat',    'hebrew': u'שבט'},
		     {'english': u'Adar',     'hebrew': u'אדר'},
			 # leap year
		     {'english': u'Adar I',   'hebrew': u"אדר א'"},
		     {'english': u'Adar II',  'hebrew': u"אדר ב'"})

# Parshiot are joined as follows:
# Vayakhel-Pekudei: joined in regular years, except when Rosh Hashana is Thursday, Pesach is Sunday
# Tazria-Metzora: In regular years
# Acharei Mot-Kedoshim: In regular years
# Behar-Bechukotai: In regular years, except in Israel when Rosh Hashana is Thursday and Pesach is Shabbat
# Matot-Masei: Whatever is needed to ensure Devarim is read just before Tisha B'Av
# Netzavim-Vayelech: If Rosh Hashana is not Monday or Tuesday
# Chukat-Balak: In Diaspora if Pesach is on a Thursday
parshiot = ( {'english': u'Vayelech',     'hebrew': u'וילך'},
		     {'english': u"Ha'azinu",      'hebrew': u'האזינו'},
			 # deliberately leaving off וזאת הברכה
			 {'english': u"B'reshit",     'hebrew': u'בראשית'},
		     {'english': u'Noach',        'hebrew': u'נח'},
		     {'english': u'Lech Lecha',   'hebrew': u'לך לך'},
		     {'english': u'Vayeira',      'hebrew': u'וירא'},
		     {'english': u'Chayei Sarah', 'hebrew': u'חיי שרה'},
		     {'english': u'Toldot',       'hebrew': u'תולדות'},
		     {'english': u'Vayetze',      'hebrew': u'ויצא'},
		     {'english': u'Vayishlach',   'hebrew': u'וישלח'},
		     {'english': u'Vayeshev',     'hebrew': u'וישב'},
		     {'english': u'Miketz',       'hebrew': u'מקץ'},
		     {'english': u'Vayigash',     'hebrew': u'ויגש'},
		     {'english': u'Vayechi',      'hebrew': u'ויחי'},
		     {'english': u'Shmot',        'hebrew': u'שמות'},
		     {'english': u"Va'era",       'hebrew': u'וארא'},
		     {'english': u'Bo',           'hebrew': u'בא'},
		     {'english': u"B'shalach",    'hebrew': u'בשלח'},
		     {'english': u'Yitro',        'hebrew': u'יתרו'},
		     {'english': u'Mishpatim',    'hebrew': u'משפטים'},
		     {'english': u'Truma',        'hebrew': u'תרומה'},
		     {'english': u'Tetzave',      'hebrew': u'תצוה'},
		     {'english': u'Ki Tisa',      'hebrew': u'כי תשא'},
		     {'english': u'Vayakhel',     'hebrew': u'ויקהל', 'join': vayakhel},
		     {'english': u"P'kudei",      'hebrew': u'פקודי'},
		     {'english': u'Vayikra',      'hebrew': u'ויקרא'},
		     {'english': u'Tzav',         'hebrew': u'צו'},
		     {'english': u'Shmini',       'hebrew': u'שמיני'},
		     {'english': u'Tazria',       'hebrew': u'תזריע', 'join': leapJoin},
		     {'english': u'Metzora',      'hebrew': u'מצורע'},
		     {'english': u'Acharei Mot',  'hebrew': u'אחרי מות', 'join': leapJoin},
		     {'english': u"K'doshim",     'hebrew': u'קדושים'},
		     {'english': u'Emor',         'hebrew': u'אמר'},
		     {'english': u"B'har",        'hebrew': u'בהר', 'join': behar},
		     {'english': u"B'chukotai",   'hebrew': u'בחוקתי'},
		     {'english': u'Bamidbar',     'hebrew': u'במדבר'},
		     {'english': u'Naso',         'hebrew': u'נשא'},
		     {'english': u"B'ha'alotcha", 'hebrew': u'בהעלותך'},
		     {'english': u'Shlach Lecha', 'hebrew': u'שלח לך'},
		     {'english': u'Korach',       'hebrew': u'קרח'},
		     {'english': u'Chukat',       'hebrew': u'חקת', 'join': chukat},
		     {'english': u'Balak',        'hebrew': u'בלק'},
		     {'english': u'Pinchas',      'hebrew': u'פינחס'},
		     {'english': u'Matot',        'hebrew': u'מטות', 'join': matot},
		     {'english': u'Masei',        'hebrew': u'מסעי'},
		     {'english': u"Dvarim",       'hebrew': u'דברים'},
		     {'english': u"Va'etchanan",  'hebrew': u'ואתחנן'},
		     {'english': u'Ekev',         'hebrew': u'עקב'},
		     {'english': u"Re'e",         'hebrew': u'ראה'},
		     {'english': u'Shoftim',      'hebrew': u'שופטים'},
		     {'english': u'Ki Tetzei',    'hebrew': u'כי תצא'},
		     {'english': u'Ki Tavo',      'hebrew': u'כי תבוא'},
		     {'english': u'Nitzavim',     'hebrew': u'נצבים', 'join': nitzavim},
			 {'english': u'Vayelech',     'hebrew': u'וילך'}
		    )
			 
def getHebrewMonth(month, language):			 
	if hebrew.leap(year) and month in (12,13):
		return months[month][language]
	else:
		return months[month-1][language]

def hebrewNextMonth(month):
	next = month + 1
	if (hebrew.leap(year) and month == 13) or (not hebrew.leap(year) and month == 12):
		next = 1
	return next
		
def hebrewDate(month, day, language):
	date = ''
	if language == 'hebrew':
		date += hebrewDayOfMonth(day-1)
		date += getHebrewMonth(month, language)
	else:
		date += "%d %s" % (day, getHebrewMonth(month,language))
	return date

def deferToSunday(julianDate):
	if utils.jwday(julianDate) == weekday['shabbat']:
		return julianDate + 1
	else:
		return julianDate

def precedingThursday(julianDate):
	if utils.jwday(julianDate) == weekday['shabbat']:
		return julianDate - 2
	else:
		return julianDate
		
def holocaustDay(julianDate):
	if utils.jwday(julianDate) == weekday['shabbat']:
		return julianDate + 1
	elif utils.jwday(julianDate) == weekday['friday']:
		return julianDate - 1
	else:
		return julianDate
		
def remembranceDay(julianDate):
	if utils.jwday(julianDate) == weekday['friday']:
		return julianDate - 2
	elif utils.jwday(julianDate) == weekday['thursday']:
		return julianDate - 1
	elif utils.jwday(julianDate) == weekday['sunday']:
		return julianDate + 1
	else:
		return julianDate
		
def independanceDay(julianDate):
	if utils.jwday(julianDate) == weekday['shabbat']:
		return julianDate - 2
	elif utils.jwday(julianDate) == weekday['friday']:
		return julianDate - 1
	elif utils.jwday(julianDate) == weekday['monday']:
		return julianDate + 1
	else:
		return julianDate
		
def candle(day, language):
	fullname = ''
	if language == 'english':
		fullname = u'Chanukah - %d candle' % (day+1)
		if day != 0:
			fullname += 's'
	else:
		fullname = u'חנוכה - נר '
		fullname += days[day]
	return fullname
	
def omer(day, language):
	fullname = ''
	if language == 'english':
		fullname = u'Omer - Day %d' % (day+1)
	else:
		fullname = hebrewDayOfMonth(day)
		fullname += u"עומר"
	return fullname

# Holidays:
## Candle lighting vs. candle lighting after - should be able to tell by 'chag' flag
## Need special handling to deal with Erev Pesach on Shabbat
holidayDefs = ({'month': 7, 'day':1, 'name':{'english': u'Rosh Hashanah','hebrew':u'ראש השנה'}, 'length':2, 'type': 'RH'},
               {'month': 7, 'day':3, 'name':{'english': u'Fast of Gedaliah', 'hebrew': u'צום גדליה'}, 'length':1, 'offset': deferToSunday, 'type': 'gedaliah'},
			   {'month': 7, 'day':9, 'name':{'english': u'Erev Yom Kippur', 'hebrew': u'ערב יום כפור'}, 'length':1, 'type': 'other'},
			   {'month': 7, 'day':10,'name':{'english': u'Yom Kippur', 'hebrew': u'יום כפור'}, 'length':1, 'type': 'YK'},
			   {'month': 7, 'day':14,'name':{'english': u'Erev Sukkot', 'hebrew': u'ערב סוכות'}, 'length':1, 'type': 'erev'},
			   {'month': 7, 'day':15,'name':{'english': u'Sukkot', 'hebrew': u'סוכות'}, 'length':1, 'location': 'Israel', 'type': 'chag'},
			   {'month': 7, 'day':15,'name':{'english': u'Sukkot', 'hebrew': u'סוכות'}, 'length':2, 'location': 'Diaspora', 'type': 'chag'},
			   {'month': 7, 'day':16,'name':{'english': u'Chol Hamoed Sukkot', 'hebrew': u'חוה"מ סוכות'}, 'length':5, 'location': 'Israel', 'type': 'CH'},
			   {'month': 7, 'day':17,'name':{'english': u'Chol Hamoed Sukkot', 'hebrew': u'חוה"מ סוכות'}, 'length':4, 'location': 'Diaspora', 'type': 'CH'},
			   {'month': 7, 'day':21,'name':{'english': u'Hoshana Raba', 'hebrew': u'הושענע רבה'}, 'length':1, 'type': 'HR'},
			   {'month': 7, 'day':22,'name':{'english': u'Simchat Torah', 'hebrew': u'שמחת תורה'}, 'length':1, 'location': 'Israel', 'type': 'chag', 'yizkor': True},
			   {'month': 7, 'day':22,'name':{'english': u'Shmini Atzeret', 'hebrew': u'שמיני עצרת'}, 'length':1, 'location': 'Diaspora', 'type': 'chag', 'yizkor': True},
			   {'month': 7, 'day':23,'name':{'english': u'Simchat Torah', 'hebrew': u'שמחת תורה'}, 'length':1, 'location': 'Diaspora', 'type': 'chag'},
			   {'month': 8, 'day':6, 'name':{'english': u"Start saying v'Ten Tal Umatar", 'hebrew': u'מתחילים לומר "ותן טל ומטר לברכה"'}, 'length':1, 'location': 'Israel', 'type': 'rain'},
			   {'month': 9, 'day':25,'name':{'english': u'Chanukah', 'hebrew': u'חנוכה'}, 'length':8, 'type': 'chanuka'}, #'override': candle, 
			   {'month': 10,'day':10,'name':{'english': u'Fast of 10 Tevet', 'hebrew': u'צום עשרה בטבת'}, 'length':1, 'offset': deferToSunday, 'type': 'fast'},
			   {'month': 11,'day':15,'name':{'english': "Tu B'Shvat", 'hebrew': u'ט"ו בשבט'}, 'length':1, 'type': 'other'},
			   {'month': 12,'day':13,'name':{'english': u'Fast of Esther', 'hebrew': u'תענית אסתר'}, 'length':1, 'offset': precedingThursday, 'leap': False, 'type': 'esther'},
			   {'month': 12,'day':14,'name':{'english': u'Purim', 'hebrew': u'פורים'}, 'length':1, 'leap': False, 'type': 'purim'},
			   {'month': 12,'day':15,'name':{'english': u'Shushan Purim', 'hebrew': u'שושן פורים'}, 'length':1, 'leap': False, 'type': 'SP'},
			   {'month': 12,'day':14,'name':{'english': u'Purim Katan', 'hebrew': u'פורים קטן'}, 'length':1, 'leap': True, 'type': 'other'},
			   {'month': 12,'day':15,'name':{'english': u'Shushan Purim Katan', 'hebrew': u'פורים קטן דשושן'}, 'length':1, 'leap': True, 'type': 'other'},
			   {'month': 13,'day':13,'name':{'english': u'Fast of Esther', 'hebrew': u'תענית אסתר'}, 'length':1,'offset': precedingThursday, 'leap': True, 'type': 'esther'},
			   {'month': 13,'day':14,'name':{'english': u'Purim', 'hebrew': u'פורים'}, 'length':1, 'leap': True, 'type': 'purim'},
			   {'month': 13,'day':15,'name':{'english': u'Shushan Purim', 'hebrew': u'שושן פורים'}, 'length':1, 'leap': True, 'type': 'SP'},
			   {'month': 1, 'day':14,'name':{'english': u'Fast of the Firstborn', 'hebrew': u'תענית בכורות'}, 'length':1, 'offset': precedingThursday, 'type': 'other'},
			   {'month': 1, 'day':14,'name':{'english': u'Erev Pesach', 'hebrew': u'ערב פסח'}, 'length':1, 'type': 'erevPesach'},
			   {'month': 1, 'day':15,'name':{'english': u'Pesach', 'hebrew': u'פסח'}, 'length':1, 'location': 'Israel', 'type': 'chag'},
			   {'month': 1, 'day':15,'name':{'english': u'Pesach', 'hebrew': u'פסח'}, 'length':2, 'location': 'Diaspora', 'type': 'chag'},
			   {'month': 1, 'day':16,'name':{'english': u'Omer', 'hebrew': u'עומר'}, 'length':49, 'override': omer, 'type': 'omer'},
			   {'month': 1, 'day':16,'name':{'english': u'Chol Hamoed Pesach', 'hebrew': u'חוה"מ פסח'}, 'length':5, 'location': 'Israel', 'type': 'CH'},
			   {'month': 1, 'day':17,'name':{'english': u'Chol Hamoed Pesach', 'hebrew': u'חוה"מ פסח'}, 'length':4, 'location': 'Diaspora', 'type': 'CH'},
			   {'month': 1, 'day':21,'name':{'english': u'Pesach', 'hebrew': u'פסח'}, 'length':1, 'location': 'Israel', 'dayAdjust': 6, 'type': 'chag', 'yizkor': True},
			   {'month': 1, 'day':21,'name':{'english': u'Pesach', 'hebrew': u'פסח'}, 'length':2, 'location': 'Diaspora', 'dayAdjust': 5, 'type': 'chag', 'yizkor': True},
			   {'month': 1, 'day':27,'name':{'english': u'Holocaust Remembrance Day', 'hebrew': u'יום השואה'}, 'length':1, 'offset': holocaustDay, 'type': 'other'},
			   {'month': 2, 'day':4, 'name':{'english': u'Yom Hazikaron', 'hebrew': u'יום הזיכרון לחללי צה"ל'}, 'length':1, 'offset': remembranceDay, 'type': 'other'},
			   {'month': 2, 'day':5, 'name':{'english': u'Independence Day', 'hebrew': u'יום העצמאות'}, 'length':1, 'offset': independanceDay, 'type': 'other'},
			   {'month': 2, 'day':28,'name':{'english': u'Jerusalem Day', 'hebrew': u'יום ירושלים'}, 'length':1, 'type': 'other'},
			   {'month': 2, 'day':18,'name':{'english': u'Lag BaOmer', 'hebrew': u'ל"ג בעומר'}, 'length':1, 'type': 'other'},
			   {'month': 3, 'day':5, 'name':{'english': u'Erev Shavuot', 'hebrew': u'ערב שבועות'}, 'length':1, 'type': 'erev'},
			   {'month': 3, 'day':6, 'name':{'english': u'Shavuot', 'hebrew': u'שבועות'}, 'length':1, 'location': 'Israel', 'type': 'chag', 'yizkor': True},
			   {'month': 3, 'day':6, 'name':{'english': u'Shavuot', 'hebrew': u'שבועות'}, 'length':2, 'location': 'Diaspora', 'type': 'chag', 'yizkor': True},
			   {'month': 4, 'day':17,'name':{'english': u'Fast of 17 Tamuz', 'hebrew': u'תענית י"ז תמוז'}, 'length':1, 'offset': deferToSunday, 'type': 'fast'},
			   {'month': 5, 'day':9, 'name':{'english': "Tisha B'Av", 'hebrew': u'תשעה באב'}, 'length':1, 'offset': deferToSunday, 'type': '9av'},
			   {'month': 5, 'day':15,'name':{'english': "Tu B'Av", 'hebrew': u'ט"ו באב'}, 'length':1, 'type': 'other'},
			   {'month': 6, 'day':29,'name':{'english': u'Erev Rosh Hashanah', 'hebrew':u'ערב ראש השנה'}, 'length':1, 'type': 'erevRH'})

def getHolidays(holidays, holidayList):
	engName = None
	hebName = None
	for holiday in holidayList:
		if 'leap' in holiday and holiday['leap'] != hebrew.leap(year):
			continue
		if 'location' in holiday and holiday['location'] != location:
			continue
		for day in range(holiday['length']):
			if filter and holiday['type'] not in filter:
				continue
			jd = hebrew.to_jd(year, holiday['month'], holiday['day']) + day
			# Cover the last two days of Pesach in diaspora
			dayOfHoliday = day
			if 'dayAdjust' in holiday:
				dayOfHoliday += holiday['dayAdjust']
			if 'offset' in holiday:
				jd = holiday['offset'](jd)
			if jd in holidays:
				holidays[jd]['names'].append(holiday['name'])
				if holiday['length'] == 1 and 'dayAdjust' not in holiday:
					holidays[jd]['fullnames'].append(holiday['name'])
				else:
					if 'override' in holiday:
						engName = holiday['override'](dayOfHoliday, 'english')
						hebName = holiday['override'](dayOfHoliday, 'hebrew')
					else:
						engName = englishDayOfChag(dayOfHoliday, holiday['name']['english'])
						hebName = hebrewDayOfChag(dayOfHoliday, holiday['name']['hebrew'])
					fullname = {'english': engName, 'hebrew': hebName}
					holidays[jd]['fullnames'].append(fullname)
				if 'type' in holiday:
					holidays[jd]['type'].append(holiday['type'])
			else:
				fullName = None
				if holiday['length'] == 1:
					fullName = [holiday['name']]
				else:
					if 'override' in holiday:
						engName = holiday['override'](day, 'english')
						hebName = holiday['override'](day, 'hebrew')
					else:
						engName = englishDayOfChag(day, holiday['name']['english'])
						hebName = hebrewDayOfChag(day, holiday['name']['hebrew'])
					fullName = [{'english': engName, 'hebrew': hebName}]
				holidays[jd] = {'hebrew': hebrew.from_jd(jd), 'gregorian': gregorian.from_jd(jd), 
								'names':[holiday['name']], 'fullnames': fullName}
				holidays[jd]['date'] = datetime.date(*holidays[jd]['gregorian'])
				holidays[jd]['hebrewWritten'] = hebrewDate(holidays[jd]['hebrew'][1], holidays[jd]['hebrew'][2], 'hebrew')
				holidays[jd]['type'] = [holiday['type']]
					
			if 'mevarchim' in holiday:
				holidays[jd]['mevarchim'] = holiday['mevarchim']
				
			if 'yizkor' in holiday:
				holidays[jd]['yizkor'] = holiday['yizkor']

def getFixedHolidays(holidays):
	getHolidays(holidays, holidayDefs)
			
def getVariableHolidays(holidays):
	holidayList = []
	
	holiday = None
	end = 12
	if hebrew.leap(year):
		end = 13
	for month in range(1, end+1):
		if month == 6:
			continue
		nextMonth = month + 1
		if nextMonth > end:
			nextMonth = 1
		heb = u'ראש חודש ' + getHebrewMonth(nextMonth, 'hebrew')
		english = u'Rosh Chodesh ' + getHebrewMonth(nextMonth, 'english')
		if hebrew.month_days(year, month) == 29:
			holiday = {'month': nextMonth, 'day':1, 'name':{'english':english,'hebrew':heb}, 'length':1, 'type': 'RC'}
		else:
			holiday = {'month': month, 'day':30, 'name':{'english':english,'hebrew':heb}, 'length':2, 'type': 'RC'}
		holidayList.append(holiday)
		
	# 8th day of Chanukah
	#dayEight = hebrew.from_jd(hebrew.to_jd(year, 9, 25) + 7)
	#holiday = {'month': dayEight[1],'day':dayEight[2],'name':{'english': u'Chanukah - Day 8', 'hebrew': u'זאת חנוכה'}, 'length':1}
	#holidayList.append(holiday)
	
	# Slichot:
	# Pre RH:
	## First day of slichot is ALWAYS Sunday (Motzei, but after midnight). If RH is on Thursday or Shabbat, it's the preceding 
	## motzei. Otherwise, it's a week earlier.
	# Between RH and YK: is handled together with Fast of Gedaliah
	refDay = hebrew.to_jd(year, 6, 29)
	slichot = utils.previous_weekday(weekday['sunday'], refDay)
	if utils.jwday(refDay) in (weekday['thursday'], weekday['shabbat']):
		slichot -= 7
	slichotStart = hebrew.from_jd(slichot)
	holiday = {'month': slichotStart[1], 'day':slichotStart[2], 'name':{'english':'Slichot','hebrew':u'סליחות'}, 'length':int(refDay-slichot), 'type': 'slichot'}
	holidayList.append(holiday)
	
	# Special Shabbatot
	# Shuvah - before yom kippur (before 10 Tishrei)
	refDay = hebrew.to_jd(year, 7, 10)
	shabbat = hebrew.from_jd(utils.previous_weekday(weekday['shabbat'], refDay))
	holiday = {'month': shabbat[1], 'day':shabbat[2], 'name':{'english': u'Shabbat Shuvah', 'hebrew': u'שבת שובה'}, 'length':1, 'type': 'other'}
	holidayList.append(holiday)
	
	# Shkalim - on or before Rosh Chodesh Adar (or Adar 2) (on or before 1 Adar 2 on leap year, else on or before 1 Adar)
	if hebrew.leap(year):
		refDay = hebrew.to_jd(year, 13, 1)
	else:
		refDay = hebrew.to_jd(year, 12, 1)
	shabbat = hebrew.from_jd(utils.previous_or_current_weekday(weekday['shabbat'], refDay))
	holiday = {'month': shabbat[1], 'day':shabbat[2], 'name':{'english': u'Parshat Shkalim', 'hebrew': u'פרשת שקלים'}, 'length':1, 'type': 'other'}
	holidayList.append(holiday)
	
	# Zachor - before Purim
	if hebrew.leap(year):
		refDay = hebrew.to_jd(year, 13, 14)
	else:
		refDay = hebrew.to_jd(year, 12, 14)
	shabbat = hebrew.from_jd(utils.previous_weekday(weekday['shabbat'], refDay))
	holiday = {'month': shabbat[1], 'day':shabbat[2], 'name':{'english': u'Parshat Zachor', 'hebrew': u'פרשת זכור'}, 'length':1, 'type': 'other'}
	holidayList.append(holiday)
	
	# Hachodesh - on or before rosh chodesh Nisan
	refDay = hebrew.to_jd(year, 1, 1)
	shabbat = hebrew.from_jd(utils.previous_or_current_weekday(weekday['shabbat'], refDay))
	holiday = {'month': shabbat[1], 'day':shabbat[2], 'name':{'english': u'Parshat Hachodesh', 'hebrew': u'פרשת החודש'}, 'length':1, 'type': 'other'}
	holidayList.append(holiday)
	
	# Parah - shabbat before hachodesh
	refDay -= 7
	shabbat = hebrew.from_jd(utils.previous_or_current_weekday(weekday['shabbat'], refDay))
	holiday = {'month': shabbat[1], 'day':shabbat[2], 'name':{'english': u'Parshat Parah', 'hebrew': u'פרשת פרה'}, 'length':1, 'type': 'other'}
	holidayList.append(holiday)
	
	# Hagadol - before Pesach
	refDay = hebrew.to_jd(year, 1, 15)
	shabbat = hebrew.from_jd(utils.previous_weekday(weekday['shabbat'], refDay))
	holiday = {'month': shabbat[1], 'day':shabbat[2], 'name':{'english': u'Shabbat Hagadol', 'hebrew': u'שבת הגדול'}, 'length':1, 'type': 'other'}
	holidayList.append(holiday)
	
	# Chazon - before 9 av
	refDay = hebrew.to_jd(year, 5, 9)
	shabbat = hebrew.from_jd(utils.previous_or_current_weekday(weekday['shabbat'], refDay))
	holiday = {'month': shabbat[1], 'day':shabbat[2], 'name':{'english': u'Shabbat Chazon', 'hebrew': u'שבת חזון'}, 'length':1, 'type': 'other'}
	holidayList.append(holiday)
	
	# Nachamu - after 9 av
	# refday is already correct
	shabbat = hebrew.from_jd(utils.next_weekday(weekday['shabbat'], refDay))
	holiday = {'month': shabbat[1], 'day':shabbat[2], 'name':{'english': u'Shabbat Nacham', 'hebrew': u'שבת נחמו'}, 'length':1, 'type': 'other'}
	holidayList.append(holiday)
		
	getHolidays(holidays, holidayList)
		
def getParshiot(holidays):
	type = getYearType()
	shabbatList = []
	# If Rosh Hashana is Thursday or Shabbat, starting parsha is Ha'azinu. Otherwise it's Vayelech.
	parsha = 0
	if type[0] in (weekday['thursday'],weekday['shabbat']):
		parsha = 1
	
	# Start at first Shabbat after Rosh Hashana. 
	shabbat = utils.next_weekday(5, (hebrew.to_jd(year, 7, 1)))
	
	while parsha < len(parshiot) and hebrew.from_jd(shabbat)[0] == year:
		name = {}
		
		# For each Shabbat, advance 7 days. Check if it's chag or chol hamoed. If yes, skip a week.
		if shabbat in holidays and any([x in holidays[shabbat]['type'] for x in ('chag','RH','YK')]):
			shabbat += 7
			continue
		elif shabbat in holidays and 'CH' in holidays[shabbat]['type']:
			hebrewDay = hebrew.from_jd(shabbat)
			hebName = [x['hebrew'] for x in holidays[shabbat]['names'] if u'חוה"מ' in x['hebrew']][0]
			engName = [x['english'] for x in holidays[shabbat]['names'] if u'Chol' in x['english']][0]
			name['english'] = u'Shabbat ' + engName
			name['hebrew'] = u'שבת ' + hebName
			day = {'month': hebrewDay[1], 'day': hebrewDay[2], 'name': name, 'length':1, 'type': 'shabbat', 'mevarchim': False}
			shabbatList.append(day)
			shabbat += 7
			continue
		
		# Check if the current parsha has a join condition. If so, and the condition is true, join to the next parsha. Otherwise just use the current parsha.
		if 'join' in parshiot[parsha] and parshiot[parsha]['join'](type):
			name['english'] = u'Shabbat %s - %s' % (parshiot[parsha]['english'], parshiot[parsha+1]['english'])
			name['hebrew'] = u'שבת ' + '%s - %s' % (parshiot[parsha]['hebrew'], parshiot[parsha+1]['hebrew'])
			parsha += 1
		else:
			name['english'] = u'Shabbat ' + parshiot[parsha]['english']
			name['hebrew'] = u'שבת ' + parshiot[parsha]['hebrew']
		
		hebrewDay = hebrew.from_jd(shabbat)
		mevarchim = hebrewDay[2] >= 23 and hebrewDay[2] != 30
		day = {'month': hebrewDay[1], 'day': hebrewDay[2], 'name': name, 'length':1, 'type': 'shabbat', 'mevarchim': mevarchim}
		shabbatList.append(day)
		parsha += 1
		shabbat += 7
	
	getHolidays(holidays, shabbatList)

def getDst(year):
	dst = {}
	begin = datetime.datetime(*gregorian.from_jd(hebrew.to_jd(year,7,1)))
	end = datetime.datetime(*gregorian.from_jd(hebrew.to_jd(year,6,29)))
	
	for today in arrow.Arrow.range('day', begin, end):
		today = today.to('Asia/Jerusalem')
		tomorrow = today.replace(days=+1)
		
		if today.dst() != tomorrow.dst():
			if tomorrow.dst().total_seconds():
				dst['start'] = tomorrow.datetime
			else:
				dst['end'] = tomorrow.datetime
	return dst
	
def getHolidaysFromGregorian(holidays):
	dst = getDst(year)
	
	dayList = []
	
	for day, date in dst.iteritems():
		hebDate = hebrew.from_jd(gregorian.to_jd(date.year, date.month, date.day))
		dayList.append({'month': hebDate[1], 'day': hebDate[2], 'name': {'english': 'DST ' + day, 'hebrew': ''}, 'length':1, 'type': day + 'Dst'})
	
	getHolidays(holidays, dayList)
	
# Building this initially for yahrtzeits, but I imagine it can be used for other things as well, so
# I'll allow storing multiple lists within the list
def setExternalDays(dayList, type):
	global externalDays
	
	externalDays.append({type: dayList})
	
def getExternalDays(holidays):
	dayList = []
	
	for typeList in externalDays:
		for type in typeList:
			for entry in typeList[type]:
				date = entry['date'].split('.', 3)
				dayList.append({'month': int(date[1]), 'day': int(date[0]), 'name': {'english': '', 'hebrew': entry['info']}, 'length':1, 'type': type})
	
	getHolidays(holidays, dayList)

def setFilter(types):
	global filter
	filter = types
	
def getYear(yearIn, locationIn):
	# build list of holidays
	# add special shabbatot
	# list of dictionaries: key is Julian date, data is Hebrew date, Gregorian date, list of holidays. Gregorian will later be used to calculate times
	global year
	global location
	year = yearIn
	location = locationIn
	holidays = {}
	
	getFixedHolidays(holidays)
	
	getVariableHolidays(holidays)

	getParshiot(holidays)
	
	getHolidaysFromGregorian(holidays)
	
	getExternalDays(holidays)
	
	return holidays
	
def getMonth(yearIn, month, locationIn):
	holidaysYear = getYear(yearIn, locationIn)
	
	holidaysMonth = {}
	
	for jd, day in holidaysYear.iteritems():
		# Include everything in the given month, EXCEPT this month's Rosh 
		# Chodesh, UNLESS it's also another day (such as Shabbat Rosh Chodesh).
		# Instead, we list NEXT month's Rosh Chodesh on the schedule.
		if day['hebrew'] == (yearIn, month, 1) and day['type'] == ['RC']:
			continue
		if day['hebrew'][1] == month or \
			(day['hebrew'][1] == hebrewNextMonth(month) and \
				(('chanuka' in day['type'] and month in (9, 10)) or ('RC' in day['type'] and day['hebrew'][2] == 1))):
			holidaysMonth[jd] = day
	
	return holidaysMonth
		

if __name__ == "__main__":
	import sys

	out = open('test.txt', 'w')

	x = getYear(int(sys.argv[1]), 'Israel')

	for key in sorted(x):
		y = x[key]
		#print repr(y)
		z = '\n'
		z += repr(y['hebrew'])
		z += "\n"
		z += hebrewDate(y['hebrew'][1], y['hebrew'][2], 'hebrew')
		z += "\n"
		z += repr(y['gregorian']) + '\n'
		z += ', '.join(a['english'] for a in y['names']) + '\n'
		z += ', '.join(a['hebrew'] for a in y['names']) + '\n'
		z += ', '.join(a['english'] for a in y['fullnames']) + '\n'
		z += ', '.join(a['hebrew'] for a in y['fullnames']) + '\n'
		
		#print z
		out.write(z.encode('utf8')+'\n')

	out.close()
			
			
			
			
			
			
			
			
			
			
			
			
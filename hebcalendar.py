#!/usr/bin/python
# -*- coding: UTF-8 -*-

from convertdate import hebrew, gregorian, utils, julianday
import datetime
import arrow

external_days = []
filter = []

weekday = {
	'sunday': 6,
	'monday': 0,
	'tuesday': 1,
	'wednesday': 2,
	'thursday': 3,
	'friday': 4,
	'shabbat': 5}

year = None
location = None
# Calculate molad based on zero year - as per Ari Brodsky, take Marcheshvan 5765
moladZero = {'day': 3, 'hours': 2, 'minutes': 0, 'chalakim': 0}
moladZeroDate = {'year': 5765, 'month': 8, 'day': 1}

languages = ['english', 'hebrew']
numbers = [
	u"א'",  u"ב'",  u"ג'",  u"ד'",  u"ה'",  u"ו'",  u"ז'",  u"ח'",  u"ט'",  u"י'",
	u'י"א', u'י"ב', u'י"ג', u'י"ד', u'ט"ו', u'ט"ז', u'י"ז', u'י"ח', u'י"ט', u"כ'",
	u'כ"א', u'כ"ב', u'כ"ג', u'כ"ד', u'כ"ה', u'כ"ו', u'כ"ז', u'כ"ח', u'כ"ט', u"ל'",
	u'ל"א', u'ל"ב', u'ל"ג', u'ל"ד', u'ל"ה', u'ל"ו', u'ל"ז', u'ל"ח', u'ל"ט', u"מ'",
	u'מ"א', u'מ"ב', u'מ"ג', u'מ"ד', u'מ"ה', u'מ"ו', u'מ"ז', u'מ"ח', u'מ"ט']

days = [u'ראשון', u'שני', u'שלישי', u'רביעי', u'חמישי', u'שישי', u'שביעי', u'שמיני']


def hebrew_number(number):
	return numbers[number]


def hebrew_day_of_week(number):
	# Expect the day of week as a number from datetime.weekday()
	number = (number + 1) % 7
	if number == 6:
		return u"שבת"
	else:
		return hebrew_number(number)


def hebrew_day_of_month(number):
	return hebrew_number(number) + u" ב"


def hebrew_day_of_chag(number, holiday):
	return hebrew_number(number) + u" ד" + holiday


def english_day_of_chag(number, holiday):
	return u"%s - Day %d" % (holiday, number+1)


def get_year_type(year_for_type=None):
	if year_for_type is None:
		year_for_type = year
	days_in_year = hebrew.year_days(year_for_type)
	length = None
	if days_in_year in (353, 383):
		length = 'short'
	elif days_in_year in (354, 384):
		length = 'normal'
	elif days_in_year in (355, 385):
		length = 'long'
	
	rh = utils.jwday(hebrew.to_jd(year_for_type, 7, 1))
	
	pesach = utils.jwday(hebrew.to_jd(year_for_type, 1, 15))
	
	return rh, length, pesach


def leap_join(_year_type):
	return not hebrew.leap(year)


def vayakhel(year_type):
	return not hebrew.leap(year) and not (year_type[0] == weekday['thursday'] and year_type[2] == weekday['sunday'])


def behar(year_type):
	return not hebrew.leap(year) and not (year_type[0] == weekday['thursday'] and year_type[2] == weekday['shabbat'])


def nitzavim(_year_type):
	next_year_type = get_year_type(year + 1)
	return next_year_type[0] not in (weekday['monday'], weekday['tuesday'])


def chukat(year_type):
	return location == 'Diaspora' and year_type[2] == weekday['thursday']


def matot(year_type):
	split = hebrew.leap(year) and year_type[0] == weekday['thursday']
	if location == 'Israel' and not split:
		if year_type in (
				(weekday['monday'], 'long', weekday['shabbat']),
				(weekday['tuesday'], 'normal', weekday['shabbat']),
				(weekday['thursday'], 'short', weekday['sunday']),
				(weekday['thursday'], 'long', weekday['tuesday'])):
			split = True
	return not split


months = (
	{'english': u'Nisan',    'hebrew': u'ניסן'},
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
parshiot = (
	{'english': u'Vayelech',     'hebrew': u'וילך'},
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
	{'english': u'Tazria',       'hebrew': u'תזריע', 'join': leap_join},
	{'english': u'Metzora',      'hebrew': u'מצורע'},
	{'english': u'Acharei Mot',  'hebrew': u'אחרי מות', 'join': leap_join},
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


def get_hebrew_month(month, language):
	if hebrew.leap(year) and month in (12, 13):
		return months[month][language]
	else:
		return months[month-1][language]


def hebrew_next_month(month):
	next_month = month + 1
	if (hebrew.leap(year) and month == 13) or (not hebrew.leap(year) and month == 12):
		next_month = 1
	return next_month


def hebrew_date(month, day, language):
	date = ''
	if language == 'hebrew':
		date += hebrew_day_of_month(day - 1)
		date += get_hebrew_month(month, language)
	else:
		date += "%d %s" % (day, get_hebrew_month(month, language))
	return date


def defer_to_sunday(julian_date):
	if utils.jwday(julian_date) == weekday['shabbat']:
		return julian_date + 1
	else:
		return julian_date


def preceding_thursday(julian_date):
	if utils.jwday(julian_date) == weekday['shabbat']:
		return julian_date - 2
	else:
		return julian_date


def holocaust_day(julian_date):
	if utils.jwday(julian_date) == weekday['sunday']:
		return julian_date + 1
	elif utils.jwday(julian_date) == weekday['friday']:
		return julian_date - 1
	else:
		return julian_date


def remembrance_day(julian_date):
	if utils.jwday(julian_date) == weekday['friday']:
		return julian_date - 2
	elif utils.jwday(julian_date) == weekday['thursday']:
		return julian_date - 1
	elif utils.jwday(julian_date) == weekday['sunday']:
		return julian_date + 1
	else:
		return julian_date


def independence_day(julian_date):
	if utils.jwday(julian_date) == weekday['shabbat']:
		return julian_date - 2
	elif utils.jwday(julian_date) == weekday['friday']:
		return julian_date - 1
	elif utils.jwday(julian_date) == weekday['monday']:
		return julian_date + 1
	else:
		return julian_date


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
		fullname = hebrew_day_of_month(day)
		fullname += u"עומר"
	return fullname

# Holidays:
# Candle lighting vs. candle lighting after - should be able to tell by 'chag' flag
# Need special handling to deal with Erev Pesach on Shabbat
holidayDefs = (
	{'month': 7, 'day': 1, 'name': {'english': u'Rosh Hashanah','hebrew':u'ראש השנה'}, 'length': 2, 'type': 'RH'},
	{'month': 7, 'day': 3, 'name': {'english': u'Fast of Gedaliah', 'hebrew': u'צום גדליה'}, 'length': 1, 'offset': defer_to_sunday, 'type': 'gedaliah'},
	{'month': 7, 'day': 9, 'name': {'english': u'Erev Yom Kippur', 'hebrew': u'ערב יום כפור'}, 'length': 1, 'type': 'erevYK'},
	{'month': 7, 'day': 10, 'name': {'english': u'Yom Kippur', 'hebrew': u'יום כפור'}, 'length': 1, 'type': 'YK'},
	{'month': 7, 'day': 14, 'name': {'english': u'Erev Sukkot', 'hebrew': u'ערב סוכות'}, 'length': 1, 'type': 'erev'},
	{'month': 7, 'day': 15, 'name': {'english': u'Sukkot', 'hebrew': u'סוכות'}, 'length': 1, 'location': 'Israel', 'type': 'chag'},
	{'month': 7, 'day': 15, 'name': {'english': u'Sukkot', 'hebrew': u'סוכות'}, 'length': 2, 'location': 'Diaspora', 'type': 'chag'},
	{'month': 7, 'day': 16, 'name': {'english': u'Chol Hamoed Sukkot', 'hebrew': u'חוה"מ סוכות'}, 'length': 5, 'location': 'Israel', 'type': 'CH'},
	{'month': 7, 'day': 17, 'name': {'english': u'Chol Hamoed Sukkot', 'hebrew': u'חוה"מ סוכות'}, 'length': 4, 'location': 'Diaspora', 'type': 'CH'},
	{'month': 7, 'day': 21, 'name': {'english': u'Hoshana Raba', 'hebrew': u'הושענא רבה'}, 'length': 1, 'type': 'HR'},
	{'month': 7, 'day': 22, 'name': {'english': u'Simchat Torah', 'hebrew': u'שמחת תורה'}, 'length': 1, 'location': 'Israel', 'type': 'chag', 'yizkor': True},
	{'month': 7, 'day': 22, 'name': {'english': u'Shmini Atzeret', 'hebrew': u'שמיני עצרת'}, 'length': 1, 'location': 'Diaspora', 'type': 'chag', 'yizkor': True},
	{'month': 7, 'day': 23, 'name': {'english': u'Simchat Torah', 'hebrew': u'שמחת תורה'}, 'length': 1, 'location': 'Diaspora', 'type': 'chag'},
	{'month': 8, 'day': 6, 'name': {'english': u"Start saying v'Ten Tal Umatar", 'hebrew': u'מתחילים לומר "ותן טל ומטר לברכה"'}, 'length':1, 'location': 'Israel', 'type': 'rain'},
	{'month': 9, 'day': 25, 'name': {'english': u'Chanukah', 'hebrew': u'חנוכה'}, 'length': 8, 'type': 'chanuka'},
	{'month': 10, 'day': 10, 'name': {'english': u'Fast of 10 Tevet', 'hebrew': u'צום עשרה בטבת'}, 'length': 1, 'offset': defer_to_sunday, 'type': 'fast'},
	{'month': 11, 'day': 15, 'name': {'english': u"Tu B'Shvat", 'hebrew': u'ט"ו בשבט'}, 'length': 1, 'type': 'other'},
	{'month': 12, 'day': 13, 'name': {'english': u'Fast of Esther', 'hebrew': u'תענית אסתר'}, 'length': 1, 'offset': preceding_thursday, 'leap': False, 'type': 'esther'},
	{'month': 12, 'day': 14, 'name': {'english': u'Purim', 'hebrew': u'פורים'}, 'length': 1, 'leap': False, 'type': 'purim'},
	{'month': 12, 'day': 15, 'name': {'english': u'Shushan Purim', 'hebrew': u'שושן פורים'}, 'length': 1, 'leap': False, 'type': 'SP'},
	{'month': 12, 'day': 14, 'name': {'english': u'Purim Katan', 'hebrew': u'פורים קטן'}, 'length': 1, 'leap': True, 'type': 'other'},
	{'month': 12, 'day': 15, 'name': {'english': u'Shushan Purim Katan', 'hebrew': u'פורים קטן דשושן'}, 'length': 1, 'leap': True, 'type': 'other'},
	{'month': 13, 'day': 13, 'name': {'english': u'Fast of Esther', 'hebrew': u'תענית אסתר'}, 'length': 1,'offset': preceding_thursday, 'leap': True, 'type': 'esther'},
	{'month': 13, 'day': 14, 'name': {'english': u'Purim', 'hebrew': u'פורים'}, 'length':1, 'leap': True, 'type': 'purim'},
	{'month': 13, 'day': 15, 'name': {'english': u'Shushan Purim', 'hebrew': u'שושן פורים'}, 'length': 1, 'leap': True, 'type': 'SP'},
	{'month': 1, 'day': 14, 'name': {'english': u'Fast of the Firstborn', 'hebrew': u'תענית בכורות'}, 'length': 1, 'offset': preceding_thursday, 'type': 'firstborn'},
	{'month': 1, 'day': 14, 'name': {'english': u'Erev Pesach', 'hebrew': u'ערב פסח'}, 'length': 1, 'type': 'erevPesach'},
	{'month': 1, 'day': 15, 'name': {'english': u'Pesach', 'hebrew': u'פסח'}, 'length': 1, 'location': 'Israel', 'type': 'chag'},
	{'month': 1, 'day': 15, 'name': {'english': u'Pesach', 'hebrew': u'פסח'}, 'length': 2, 'location': 'Diaspora', 'type': 'chag'},
	{'month': 1, 'day': 16, 'name': {'english': u'Omer', 'hebrew': u'עומר'}, 'length': 49, 'override': omer, 'type': 'omer'},
	{'month': 1, 'day': 16, 'name': {'english': u'Chol Hamoed Pesach', 'hebrew': u'חוה"מ פסח'}, 'length': 5, 'location': 'Israel', 'type': 'CH'},
	{'month': 1, 'day': 17, 'name': {'english': u'Chol Hamoed Pesach', 'hebrew': u'חוה"מ פסח'}, 'length': 4, 'location': 'Diaspora', 'type': 'CH'},
	{'month': 1, 'day': 21, 'name': {'english': u'Pesach', 'hebrew': u'פסח'}, 'length': 1, 'location': 'Israel', 'dayAdjust': 6, 'type': 'chag', 'yizkor': True},
	{'month': 1, 'day': 21, 'name': {'english': u'Pesach', 'hebrew': u'פסח'}, 'length': 2, 'location': 'Diaspora', 'dayAdjust': 5, 'type': 'chag', 'yizkor': True},
	{'month': 1, 'day': 27, 'name': {'english': u'Holocaust Remembrance Day', 'hebrew': u'יום השואה'}, 'length': 1, 'offset': holocaust_day, 'type': 'other'},
	{'month': 2, 'day': 4, 'name': {'english': u'Yom Hazikaron', 'hebrew': u'יום הזיכרון לחללי צה"ל'}, 'length': 1, 'offset': remembrance_day, 'type': 'other'},
	{'month': 2, 'day': 5, 'name': {'english': u'Independence Day', 'hebrew': u'יום העצמאות'}, 'length': 1, 'offset': independence_day, 'type': 'independance'},
	{'month': 2, 'day': 14, 'name': {'english': u'Pesach Sheni', 'hebrew': u'פסח שני'}, 'length': 1, 'type': 'other'},
	{'month': 2, 'day': 28, 'name': {'english': u'Jerusalem Day', 'hebrew': u'יום ירושלים'}, 'length': 1, 'type': 'jerusalem'},
	{'month': 2, 'day': 18, 'name': {'english': u'Lag BaOmer', 'hebrew': u'ל"ג בעומר'}, 'length': 1, 'type': 'other'},
	{'month': 3, 'day': 5, 'name': {'english': u'Erev Shavuot', 'hebrew': u'ערב שבועות'}, 'length': 1, 'type': 'erev'},
	{'month': 3, 'day': 6, 'name': {'english': u'Shavuot', 'hebrew': u'שבועות'}, 'length': 1, 'location': 'Israel', 'type': 'chag', 'yizkor': True},
	{'month': 3, 'day': 6, 'name': {'english': u'Shavuot', 'hebrew': u'שבועות'}, 'length': 2, 'location': 'Diaspora', 'type': 'chag', 'yizkor': True},
	{'month': 4, 'day': 17,'name': {'english': u'Fast of 17 Tamuz', 'hebrew': u'תענית י"ז תמוז'}, 'length': 1, 'offset': defer_to_sunday, 'type': 'fast'},
	{'month': 5, 'day': 9, 'name': {'english': u"Tisha B'Av", 'hebrew': u'תשעה באב'}, 'length': 1, 'offset': defer_to_sunday, 'type': '9av'},
	{'month': 5, 'day': 15,'name': {'english': u"Tu B'Av", 'hebrew': u'ט"ו באב'}, 'length': 1, 'type': 'other'},
	{'month': 6, 'day': 29,'name': {'english': u'Erev Rosh Hashanah', 'hebrew':u'ערב ראש השנה'}, 'length': 1, 'type': 'erevRH'})


def get_holidays(holidays, holiday_list):
	eng_name = None
	heb_name = None
	for holiday in holiday_list:
		if 'leap' in holiday and holiday['leap'] != hebrew.leap(year):
			continue
		if 'location' in holiday and holiday['location'] != location:
			continue
		for day in range(holiday['length']):
			jd = hebrew.to_jd(year, holiday['month'], holiday['day']) + day
			# Cover the last two days of Pesach in diaspora
			day_of_holiday = day
			if 'dayAdjust' in holiday:
				day_of_holiday += holiday['dayAdjust']
			if 'offset' in holiday:
				jd = holiday['offset'](jd)
			if jd in holidays:
				holidays[jd]['names'].append(holiday['name'])
				if holiday['length'] == 1 and 'dayAdjust' not in holiday:
					holidays[jd]['fullnames'].append(holiday['name'])
				else:
					if 'override' in holiday:
						eng_name = holiday['override'](day_of_holiday, 'english')
						heb_name = holiday['override'](day_of_holiday, 'hebrew')
					else:
						eng_name = english_day_of_chag(day_of_holiday, holiday['name']['english'])
						heb_name = hebrew_day_of_chag(day_of_holiday, holiday['name']['hebrew'])
					fullname = {'english': eng_name, 'hebrew': heb_name}
					holidays[jd]['fullnames'].append(fullname)
				if 'type' in holiday:
					holidays[jd]['type'].append(holiday['type'])
			else:
				full_name = None
				if holiday['length'] == 1:
					full_name = [holiday['name']]
				else:
					if 'override' in holiday:
						eng_name = holiday['override'](day, 'english')
						heb_name = holiday['override'](day, 'hebrew')
					else:
						eng_name = english_day_of_chag(day, holiday['name']['english'])
						heb_name = hebrew_day_of_chag(day, holiday['name']['hebrew'])
					full_name = [{'english': eng_name, 'hebrew': heb_name}]
				holidays[jd] = {
					'hebrew': hebrew.from_jd(jd), 'gregorian': gregorian.from_jd(jd),
					'names': [holiday['name']], 'fullnames': full_name}
				holidays[jd]['date'] = datetime.date(*holidays[jd]['gregorian'])
				holidays[jd]['hebrewWritten'] = \
					hebrew_date(holidays[jd]['hebrew'][1], holidays[jd]['hebrew'][2], 'hebrew')
				holidays[jd]['type'] = [holiday['type']]
					
			if 'mevarchim' in holiday:
				holidays[jd]['mevarchim'] = holiday['mevarchim']
				
			if 'yizkor' in holiday:
				holidays[jd]['yizkor'] = holiday['yizkor']

			if 'molad' in holiday:
				holidays[jd]['molad'] = holiday['molad']


def get_fixed_holidays(holidays):
	get_holidays(holidays, holidayDefs)


def get_variable_holidays(holidays):
	holiday_list = []
	
	holiday = None
	end = 12
	if hebrew.leap(year):
		end = 13
	for month in range(1, end+1):
		if month == 6:
			continue
		next_month = month + 1
		if next_month > end:
			next_month = 1
		heb = u'ראש חודש ' + get_hebrew_month(next_month, 'hebrew')
		english = u'Rosh Chodesh ' + get_hebrew_month(next_month, 'english')
		molad = get_molad(year, next_month)
		if hebrew.month_days(year, month) == 29:
			holiday = {
				'month': next_month, 'day': 1, 'name': {'english': english, 'hebrew': heb}, 'length': 1,
				'type': 'RC', 'molad': molad}
		else:
			holiday = {
				'month': month, 'day': 30, 'name': {'english': english, 'hebrew': heb}, 'length': 2,
				'type': 'RC', 'molad': molad}
		holiday_list.append(holiday)
		
	# Slichot:
	# Pre RH:
	# - First day of slichot is ALWAYS Sunday (Motzei, but after midnight). If RH is on Thursday or Shabbat, it's the
	#   preceding motzei. Otherwise, it's a week earlier.
	# Between RH and YK: is handled together with Fast of Gedaliah
	ref_day = hebrew.to_jd(year, 6, 29)
	slichot = utils.previous_weekday(weekday['sunday'], ref_day)
	if utils.jwday(ref_day) in (weekday['thursday'], weekday['shabbat']):
		slichot -= 7
	slichot_start = hebrew.from_jd(slichot)
	holiday = {
		'month': slichot_start[1], 'day': slichot_start[2], 'name': {'english': 'Slichot', 'hebrew': u'סליחות'},
		'length': int(ref_day-slichot), 'type': 'slichot'}
	holiday_list.append(holiday)
	
	# Special Shabbatot
	# Shuvah - before yom kippur (before 10 Tishrei)
	ref_day = hebrew.to_jd(year, 7, 10)
	shabbat = hebrew.from_jd(utils.previous_weekday(weekday['shabbat'], ref_day))
	holiday = {
		'month': shabbat[1], 'day': shabbat[2], 'name': {'english': u'Shabbat Shuvah', 'hebrew': u'שבת שובה'},
		'length': 1, 'type': 'other'}
	holiday_list.append(holiday)
	
	# Shkalim - on or before Rosh Chodesh Adar (or Adar 2) (on or before 1 Adar 2 on leap year,
	# else on or before 1 Adar)
	if hebrew.leap(year):
		ref_day = hebrew.to_jd(year, 13, 1)
	else:
		ref_day = hebrew.to_jd(year, 12, 1)
	shabbat = hebrew.from_jd(utils.previous_or_current_weekday(weekday['shabbat'], ref_day))
	holiday = {
		'month': shabbat[1], 'day': shabbat[2], 'name': {'english': u'Parshat Shkalim', 'hebrew': u'פרשת שקלים'},
		'length': 1, 'type': 'other'}
	holiday_list.append(holiday)
	
	# Zachor - before Purim
	if hebrew.leap(year):
		ref_day = hebrew.to_jd(year, 13, 14)
	else:
		ref_day = hebrew.to_jd(year, 12, 14)
	shabbat = hebrew.from_jd(utils.previous_weekday(weekday['shabbat'], ref_day))
	holiday = {
		'month': shabbat[1], 'day': shabbat[2], 'name': {'english': u'Parshat Zachor', 'hebrew': u'פרשת זכור'},
		'length': 1, 'type': 'other'}
	holiday_list.append(holiday)
	
	# Hachodesh - on or before rosh chodesh Nisan
	ref_day = hebrew.to_jd(year, 1, 1)
	shabbat = hebrew.from_jd(utils.previous_or_current_weekday(weekday['shabbat'], ref_day))
	holiday = {
		'month': shabbat[1], 'day': shabbat[2], 'name': {'english': u'Parshat Hachodesh', 'hebrew': u'פרשת החודש'},
		'length': 1, 'type': 'other'}
	holiday_list.append(holiday)
	
	# Parah - shabbat before hachodesh
	ref_day -= 7
	shabbat = hebrew.from_jd(utils.previous_or_current_weekday(weekday['shabbat'], ref_day))
	holiday = {
		'month': shabbat[1], 'day': shabbat[2], 'name': {'english': u'Parshat Parah', 'hebrew': u'פרשת פרה'},
		'length': 1, 'type': 'other'}
	holiday_list.append(holiday)

	# special case -- if shabbat hagadol is also erev Pesach,
	ref_day = hebrew.to_jd(year, 1, 14)
	day_of_week = julianday.to_datetime(ref_day).date().weekday()
	if weekday['shabbat'] == day_of_week:
		holiday = {
			'month': 1, 'day': 13, 'name': {'english': u'', 'hebrew': u''},
			'length': 1, 'type': 'preErevPesach'}
	holiday_list.append(holiday)

	# Hagadol - before Pesach
	ref_day = hebrew.to_jd(year, 1, 15)
	shabbat = hebrew.from_jd(utils.previous_weekday(weekday['shabbat'], ref_day))
	holiday = {
		'month': shabbat[1], 'day': shabbat[2], 'name': {'english': u'Shabbat Hagadol', 'hebrew': u'שבת הגדול'},
		'length': 1, 'type': 'other'}
	holiday_list.append(holiday)
	
	# Chazon - before 9 av
	ref_day = hebrew.to_jd(year, 5, 9)
	shabbat = hebrew.from_jd(utils.previous_or_current_weekday(weekday['shabbat'], ref_day))
	holiday = {
		'month': shabbat[1], 'day': shabbat[2], 'name': {'english': u'Shabbat Chazon', 'hebrew': u'שבת חזון'},
		'length': 1, 'type': 'other'}
	holiday_list.append(holiday)
	
	# Nachamu - after 9 av
	# refday is already correct
	shabbat = hebrew.from_jd(utils.next_weekday(weekday['shabbat'], ref_day))
	holiday = {
		'month': shabbat[1], 'day': shabbat[2], 'name': {'english': u'Shabbat Nacham', 'hebrew': u'שבת נחמו'},
		'length': 1, 'type': 'other'}
	holiday_list.append(holiday)
		
	get_holidays(holidays, holiday_list)


def get_parshiot(holidays):
	year_type = get_year_type()
	shabbat_list = []
	# If Rosh Hashana is Thursday or Shabbat, starting parsha is Ha'azinu. Otherwise it's Vayelech.
	parsha = 0
	if year_type[0] in (weekday['thursday'], weekday['shabbat']):
		parsha = 1
	
	# Start at first Shabbat after Rosh Hashana. 
	shabbat = utils.next_weekday(5, (hebrew.to_jd(year, 7, 1)))
	
	while parsha < len(parshiot) and hebrew.from_jd(shabbat)[0] == year:
		name = {}
		
		# For each Shabbat, advance 7 days. Check if it's chag or chol hamoed. If yes, skip a week.
		if shabbat in holidays and any([date in holidays[shabbat]['type'] for date in ('chag', 'RH', 'YK')]):
			shabbat += 7
			continue
		elif shabbat in holidays and 'CH' in holidays[shabbat]['type']:
			hebrew_day = hebrew.from_jd(shabbat)
			heb_name = [date['hebrew'] for date in holidays[shabbat]['names'] if u'חוה"מ' in date['hebrew']][0]
			eng_name = [date['english'] for date in holidays[shabbat]['names'] if u'Chol' in date['english']][0]
			name['english'] = u'Shabbat ' + eng_name
			name['hebrew'] = u'שבת ' + heb_name
			day = {
				'month': hebrew_day[1], 'day': hebrew_day[2], 'name': name, 'length': 1,
				'type': 'shabbat', 'mevarchim': False}
			shabbat_list.append(day)
			shabbat += 7
			continue
		
		# Check if the current parsha has a join condition. If so, and the condition is true, join to the next
		# parsha. Otherwise just use the current parsha.
		if 'join' in parshiot[parsha] and parshiot[parsha]['join'](year_type):
			name['english'] = u'Shabbat %s - %s' % (parshiot[parsha]['english'], parshiot[parsha+1]['english'])
			name['hebrew'] = u'שבת ' + '%s - %s' % (parshiot[parsha]['hebrew'], parshiot[parsha+1]['hebrew'])
			parsha += 1
		else:
			name['english'] = u'Shabbat ' + parshiot[parsha]['english']
			name['hebrew'] = u'שבת ' + parshiot[parsha]['hebrew']
		
		hebrew_day = hebrew.from_jd(shabbat)
		mevarchim = hebrew_day[2] >= 23 and hebrew_day[2] != 30
		day = {
			'month': hebrew_day[1], 'day': hebrew_day[2], 'name': name, 'length': 1,
			'type': 'shabbat', 'mevarchim': mevarchim}
		shabbat_list.append(day)
		parsha += 1
		shabbat += 7
	
	get_holidays(holidays, shabbat_list)


def get_dst(year):
	dst = {}
	begin = datetime.datetime(*gregorian.from_jd(hebrew.to_jd(year, 7, 1)))
	end = datetime.datetime(*gregorian.from_jd(hebrew.to_jd(year, 6, 29)))
	
	for today in arrow.Arrow.range('day', begin, end):
		today = today.to('Asia/Jerusalem')
		tomorrow = today.shift(days=+1)
		
		if today.dst() != tomorrow.dst():
			if tomorrow.dst().total_seconds():
				dst['start'] = tomorrow.datetime
			else:
				dst['end'] = tomorrow.datetime
	return dst


def get_holidays_from_gregorian(holidays):
	# Disable -- for now, leave out DST information
	#dst = get_dst(year)
	dst = {}
	
	day_list = []
	
	for day, date in dst.items():
		heb_date = hebrew.from_jd(gregorian.to_jd(date.year, date.month, date.day))
		day_list.append({
			'month': heb_date[1], 'day': heb_date[2], 'name': {'english': 'DST ' + day, 'hebrew': ''},
			'length': 1, 'type': day + 'Dst'})
	
	get_holidays(holidays, day_list)


# Building this initially for yahrtzeits, but I imagine it can be used for other things as well, so
# I'll allow storing multiple lists within the list
def set_external_days(day_list, type):
	global external_days
	
	external_days.append({type: day_list})


def get_external_days(holidays):
	day_list = []
	
	for type_list in external_days:
		for type in type_list:
			for entry in type_list[type]:
				date = entry['date'].split('.', 3)
				day_list.append({
					'month': int(date[1]), 'day': int(date[0]), 'name': {'english': '', 'hebrew': entry['info']},
					'length': 1, 'type': type})
	
	get_holidays(holidays, day_list)


def set_filter(types):
	global filter
	filter = set(types)


def filter_holidays(holidays):
	if filter:
		filtered = {k: v for k, v in holidays.items() if set(v['type']).intersection(filter)}
		return filtered
	else:
		return holidays


def get_molad(year, month):
	# This will only work for dates after the reference (zero) date
	molad_year = moladZeroDate['year']
	molad_month = moladZeroDate['month']

	month_count = 0

	# Get number of months between
	while molad_year < year:
		if hebrew.leap(molad_year):
			month_count += 13
		else:
			month_count += 12
		molad_year += 1

	months_in_year = 12
	if hebrew.leap(year):
		months_in_year = 13

	while molad_month != month:
		month_count += 1
		molad_month = (molad_month + 1)
		if molad_month > months_in_year:
			molad_month = 1

	# for each month, add 1 day, 12 hours, 44 minutes, 1 chelek
	chalakim = month_count + moladZero['chalakim']
	minutes = 44 * month_count + moladZero['minutes']
	hour = 12 * month_count + moladZero['hours']
	day = month_count + moladZero['day']

	# And now normalize it
	# 18 chalakim in a minute
	minutes += chalakim // 18
	chalakim = chalakim % 18

	hour += minutes // 60
	minutes = minutes % 60

	day += hour // 24
	hour = hour % 24

	day %= 7

	return {'day': day, 'hours': hour, 'minutes': minutes, 'chalakim': chalakim}


def get_year(year_in, location_in):
	# build list of holidays
	# add special shabbatot
	# list of dictionaries: key is Julian date, data is Hebrew date, Gregorian date, list of holidays.
	# Gregorian will later be used to calculate times
	global year
	global location
	year = year_in
	location = location_in
	holidays = {}
	
	get_fixed_holidays(holidays)
	
	get_variable_holidays(holidays)

	get_parshiot(holidays)
	
	get_holidays_from_gregorian(holidays)
	
	get_external_days(holidays)

	holidays = filter_holidays(holidays)
	
	return holidays


def get_month(year_in, month, location_in):
	holidays_year = get_year(year_in, location_in)
	
	holidays_month = {}
	
	for jd, day in holidays_year.items():
		# Include everything in the given month, EXCEPT this month's Rosh 
		# Chodesh, UNLESS it's also another day (such as Shabbat Rosh Chodesh).
		# Instead, we list NEXT month's Rosh Chodesh on the schedule.
		if day['hebrew'] == (year_in, month, 1) and day['type'] == ['RC']:
			continue
		if day['hebrew'][1] == month or \
			(day['hebrew'][1] == hebrew_next_month(month) and
				(('chanuka' in day['type'] and month in (9, 10)) or ('RC' in day['type'] and day['hebrew'][2] == 1))):
			holidays_month[jd] = day
	
	return holidays_month
		

if __name__ == "__main__":
	import sys

	out = open('test.txt', 'w')

	x = get_year(int(sys.argv[1]), 'Israel')

	for key in sorted(x):
		y = x[key]
		z = '\n'
		z += repr(y['hebrew'])
		z += "\n"
		z += hebrew_date(y['hebrew'][1], y['hebrew'][2], 'hebrew')
		z += "\n"
		z += repr(y['gregorian']) + '\n'
		z += ', '.join(a['english'] for a in y['names']) + '\n'
		z += ', '.join(a['hebrew'] for a in y['names']) + '\n'
		z += ', '.join(a['english'] for a in y['fullnames']) + '\n'
		z += ', '.join(a['hebrew'] for a in y['fullnames']) + '\n'

		out.write(z.encode('utf8')+'\n')

	out.close()

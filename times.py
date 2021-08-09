#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
from astral import Astral, Location, SUN_RISING, SUN_SETTING

a = Astral()
a.solar_depression = 'civil'

loc = None

# These numbers determined in consultation with Rav Moti
candleLightingMinutes = 22
motzeiSunPosition = -8.33
fastEndsPosition = -4.9
fast9avEndsPosition = -6.45
fastStartsPosition = -16.013
misheyakirPosition = -11.5
firstDayEndPosition = -6.2
candleLightinMotzash = -6.45
ninety = datetime.timedelta(minutes=90)


def round(time, direction):
	if direction == 'forward':
		return time.replace(second=0) + datetime.timedelta(seconds=60)
	elif direction == 'backward':
		return time.replace(second=0)


def set_location(name, region, latitude, longitude, tz_name, elevation):
	global loc
	loc = Location((name, region, latitude, longitude, tz_name, elevation))


def variable_hour(date):
	GRA = loc.sunset(date=date) - loc.sunrise(date=date)
	MA = (loc.sunset(date=date) + ninety) - (loc.sunrise(date=date) - ninety)
	return {'GRA': datetime.timedelta(seconds=GRA.total_seconds()/12),
	        'MA': datetime.timedelta(seconds=MA.total_seconds()/12)}


def plag_mincha(date):
	hour = variable_hour(date)['MA']
	hour1p5 = datetime.timedelta(seconds=(hour.total_seconds() * 1.5))
	return round(motzei(date) - hour1p5, 'backward')


def motzei(date):
	return round(loc.time_at_elevation(motzeiSunPosition, SUN_SETTING, date), 'forward')


def candle_lighting_motzash(date):
	return round(loc.time_at_elevation(candleLightinMotzash, SUN_SETTING, date), 'forward')


def candle_lighting(date):
	delta = datetime.timedelta(minutes=candleLightingMinutes)
	return round(loc.sunset(date=date) - delta, 'backward')


def fast_begins(date):
	return round(loc.time_at_elevation(fastStartsPosition, SUN_RISING, date), 'backward')


def fast_ends(date):
	return round(loc.time_at_elevation(fastEndsPosition, SUN_SETTING, date), 'forward')


def fast_ends_9av(date):
	return round(loc.time_at_elevation(fast9avEndsPosition, SUN_SETTING, date), 'forward')


def misheyakir(date):
	return round(loc.time_at_elevation(misheyakirPosition, SUN_RISING, date), 'forward')


def firstDayEnds(date):
	return round(loc.time_at_elevation(firstDayEndPosition, SUN_SETTING, date), 'forward')


# Try these using 90 minutes before Hanetz to 90 minutes after shkiah, see if the times work out
def pesach_chametz_eating(date):
	hour = variable_hour(date)['MA']
	return round(loc.sunrise(date=date) - ninety + 4 * hour, 'backward')


def pesach_chametz_burning(date):
	hour = variable_hour(date)['MA']
	return round(loc.sunrise(date=date) - ninety + 5 * hour, 'backward')


def midnight(date):
	return loc.solar_noon() - datetime.timedelta(hours=12)


def get_times(date):
	data = {'motzei': motzei(date),
			'candleLighting': candle_lighting(date),
			'fastBegins': fast_begins(date),
			'fastEnds': fast_ends(date),
			'fast9avEnds': fast_ends_9av(date),
			'firstDayEnds': firstDayEnds(date),
			'chametzEating': pesach_chametz_eating(date),
			'chametzBurning': pesach_chametz_burning(date),
			'midnight': midnight(date),
			'plagMincha': plag_mincha(date),
			'candleLightingPesachMotzash': candle_lighting_motzash(date),
	        'talitTfilin': misheyakir(date)}
	data.update(loc.sun(date=date))
	return data

# times of day from Astral based on location:
# set up Astral with:
## a = Astral()
## a.solar_depression='civil' # or whatever's appropriate -- need to figure out calculations
# for locations known to Astral:
## city=a['Jerusalem']
# other locations:
## city=Location(('Givat Zeev','Israel',31.86,35.17,'Asia/Jerusalem',0))
# then:
# city.sun(date=datetime.date(2014,10,5),local=True) # returns dict with dawn, sunset, sunrise, noon, dusk
# sunrise = hanetz
# sunset = shkiah
# Erev Pesach -- times for eating and burning chametz


if __name__ == "__main__":
	import sys

	today = None
	if len(sys.argv) == 4:
		today = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
	else:
		today = datetime.datetime.today()

	set_location('Givat Zeev', 'Israel', 31.86, 35.17, 'Asia/Jerusalem', 0)
	times = get_times(today)

	print("For %s, times are: " % (today.strftime('%a %Y.%m.%d')))
	print("Misheyakir: %s" % times['talitTfilin'].strftime('%H:%M'))
	print("Sunrise: %s" % times['sunrise'].strftime('%H:%M'))
	print("Sunset: %s" % times['sunset'].strftime('%H:%M'))
	print("Plag Mincha: %s" % times['plagMincha'].strftime('%H:%M'))
	print("Candle lighting: %s" % times['candleLighting'].strftime('%H:%M'))
	print("Candle lighting first night of Pesach on motzash: %s" % times['candleLightingPesachMotzash'].strftime('%H:%M'))
	print("First day of chag ends: %s" % times['firstDayEnds'].strftime('%H:%M'))
	print("Motzei: %s" % times['motzei'].strftime('%H:%M'))
	print("Fast begins: %s" % times['fastBegins'].strftime('%H:%M'))
	print("Fast ends: %s" % times['fastEnds'].strftime('%H:%M'))
	print("Eat chametz by: %s" % times['chametzEating'].strftime('%H:%M'))
	print("Burn chametz by: %s" % times['chametzBurning'].strftime('%H:%M'))
	print("Midnight - finish afikoman before: %s" % times['midnight'].strftime('%H:%M'))

	vh = variable_hour(today)
	print("Variable hour: GRA: " + str(vh['GRA']) + ', MA: ' + str(vh['MA']))

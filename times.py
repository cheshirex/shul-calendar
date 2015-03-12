#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
from astral import Astral, Location

a = Astral()
a.solar_depression='civil'

loc = None

# These numbers determined in consultation with Rav Moti
candleLightingMinutes = 22
motzeiSunPosition = -8.33
fastEndsPosition = -4.9
fast9avEndsPosition = -6.45
fastStartsPosition = 16.013 
ninety = datetime.timedelta(minutes=90)

def round(time, dir):
	if dir == 'forward':
		return time.replace(second = 0) + datetime.timedelta(seconds=60)
	elif dir == 'backward':
		return time.replace(second = 0)

def setLocation(name, region, latitude, longitude, tzName, elevation):
	global loc
	loc = Location((name, region, latitude, longitude, tzName, elevation))

def variableHour(date):
	dayLength1 = loc.sunset(date=date) - loc.sunrise(date=date)
	dayLength2 = (loc.sunset(date=date) + ninety) - (loc.sunrise(date=date) - ninety)
	return (datetime.timedelta(seconds = dayLength1.total_seconds()/12), datetime.timedelta(seconds = dayLength2.total_seconds()/12))

# Until Astral provides a way to calculate the time for a specific position of the sun
def solarPosition(date, angle):
	if not hasattr(loc, 'astral') or not loc.astral:
		rise = loc.sunrise() #in order to ensure that an astral object is initialized
	
	time = loc.astral._calc_time(date, loc.latitude, loc.longitude, angle)
	
	return time.astimezone(loc.tz)
	
def motzei(date):
	return round(solarPosition(date, motzeiSunPosition), 'forward')

def candleLighting(date):
	delta = datetime.timedelta(minutes=candleLightingMinutes)
	return round(loc.sunset(date=date) - delta, 'backward')

def fastBegins(date):
	return round(solarPosition(date, fastStartsPosition), 'backward')
	
def fastEnds(date):
	return round(solarPosition(date, fastEndsPosition),'forward')

def fastEnds9av(date):
	return round(solarPosition(date, fast9avEndsPosition),'forward')

# Try these using 90 minutes before Hanetz to 90 minutes after shkiah, see if the times work out
def pesachChametzEating(date):
	hour = variableHour(date)[1]
	return round(loc.sunrise(date=date) - ninety + 4 * hour, 'backward')
	
def pesachChametzBurning(date):
	hour = variableHour(date)[1]
	return round(loc.sunrise(date=date) - ninety + 5 * hour, 'backward')
	
def midnight(date):
	return loc.solar_noon() - datetime.timedelta(hours = 12)

def getTimes(date):
	data = {'motzei': motzei(date),
			'candleLighting': candleLighting(date),
			'fastBegins': fastBegins(date),
			'fastEnds': fastEnds(date),
			'fast9avEnds': fastEnds9av(date),
			'chametzEating': pesachChametzEating(date),
			'chametzBurning': pesachChametzBurning(date),
			'midnight': midnight(date)}
	data = dict(loc.sun(date=date).items() + data.items())
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
	
	setLocation('Givat Zeev','Israel',31.86,35.17,'Asia/Jerusalem',0)
	times = getTimes(today)
	
	print(repr(times['candleLighting'].dst().total_seconds()))
	
	print("For %s, times are: " % (today.strftime('%a %Y.%m.%d')))
	print("Candle lighting: %s" % times['candleLighting'].strftime('%H:%M'))
	print("Motzei: %s"  % times['motzei'].strftime('%H:%M'))
	print("Fast begins: %s" % times['fastBegins'].strftime('%H:%M'))
	print("Fast ends: %s" % times['fastEnds'].strftime('%H:%M'))
	print("Eat chametz by: %s" % times['chametzEating'].strftime('%H:%M'))
	print("Burn chametz by: %s" % times['chametzBurning'].strftime('%H:%M'))
	print("Midnight - finish afikoman before: %s" % times['midnight'].strftime('%H:%M'))
	
	
	
	
	
	
	
	
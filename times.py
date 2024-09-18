#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
from typing import Optional

import astral.sun
from astral import LocationInfo, SunDirection
import pytz

# a.solar_depression = 'civil' -- no longer available, what did this do anyway?

loc: Optional[LocationInfo] = None

# These numbers determined in consultation with Rav Moti
candleLightingMinutes = 22
motzeiSunPosition = -8.33
fastEndsPosition = -4.9
fast9avEndsPosition = -6.45
fastStartsPosition = -16.013
misheyakirPosition = -11.5
firstDayEndPosition = -4.9
candleLightinMotzash = -6.45
ninety = datetime.timedelta(minutes=90)


def round_time(time, direction):
    if direction == 'forward':
        return time.replace(second=0) + datetime.timedelta(seconds=60)
    elif direction == 'backward':
        return time.replace(second=0)


def set_location(name, region, latitude, longitude, tz_name):
    global loc
    loc = LocationInfo(name=name, region=region, timezone=tz_name, latitude=latitude, longitude=longitude)


def variable_hour(times):
    gra = times['sunset'] - times['sunrise']
    ma = (times['sunset'] + ninety) - (times['sunrise'] - ninety)
    return {'GRA': datetime.timedelta(seconds=gra.total_seconds() / 12),
            'MA': datetime.timedelta(seconds=ma.total_seconds() / 12)}


def plag_mincha(times):
    hour = variable_hour(times)['MA']
    hour1p5 = datetime.timedelta(seconds=(hour.total_seconds() * 1.5))
    return round_time(motzei(times) - hour1p5, 'backward')


def motzei(times):
    return round_time(astral.sun.time_at_elevation(loc.observer,
                                                   motzeiSunPosition,
                                                   date=times['sunset'],
                                                   direction=SunDirection.SETTING),
                      'forward')


def candle_lighting_motzash(times):
    return round_time(astral.sun.time_at_elevation(loc.observer,
                                                   candleLightinMotzash,
                                                   date=times['sunset'],
                                                   direction=SunDirection.SETTING),
                      'forward')


def candle_lighting(times):
    delta = datetime.timedelta(minutes=candleLightingMinutes)
    return round_time(times['sunset'] - delta, 'backward')


def fast_begins(times):
    return round_time(astral.sun.time_at_elevation(loc.observer,
                                                   fastStartsPosition,
                                                   date=times['sunset'],
                                                   direction=SunDirection.RISING),
                      'backward')


def fast_ends(times):
    return round_time(astral.sun.time_at_elevation(loc.observer,
                                                   fastEndsPosition,
                                                   date=times['sunset'],
                                                   direction=SunDirection.SETTING),
                      'forward')


def fast_ends_9av(times):
    return round_time(astral.sun.time_at_elevation(loc.observer,
                                                   fast9avEndsPosition,
                                                   date=times['sunset'],
                                                   direction=SunDirection.SETTING),
                      'forward')


def misheyakir(times):
    return round_time(astral.sun.time_at_elevation(loc.observer,
                                                   misheyakirPosition,
                                                   date=times['sunset'],
                                                   direction=SunDirection.RISING),
                      'forward')


def first_day_ends(times):
    return round_time(astral.sun.time_at_elevation(loc.observer,
                                                   firstDayEndPosition,
                                                   date=times['sunset'],
                                                   direction=SunDirection.SETTING),
                      'forward')


# Try these using 90 minutes before Hanetz to 90 minutes after shkiah, see if the times work out
def pesach_chametz_eating(times):
    hour = variable_hour(times)['MA']
    return round_time(times['sunrise'] - ninety + 4 * hour, 'backward')


def pesach_chametz_burning(times):
    hour = variable_hour(times)['MA']
    return round_time(times['sunrise'] - ninety + 5 * hour, 'backward')


def midnight(times):
    return times['noon'] - datetime.timedelta(hours=12)


def get_times(date):
    tz = pytz.timezone(loc.timezone)
    if type(date) is datetime.date:
        date = datetime.datetime(date.year, date.month, date.day)
    date = tz.localize(date)
    times = astral.sun.sun(loc.observer, date=date)
    data = {'motzei': motzei(times),
            'candleLighting': candle_lighting(times),
            'fastBegins': fast_begins(times),
            'fastEnds': fast_ends(times),
            'fast9avEnds': fast_ends_9av(times),
            'firstDayEnds': first_day_ends(times),
            'chametzEating': pesach_chametz_eating(times),
            'chametzBurning': pesach_chametz_burning(times),
            'midnight': midnight(times),
            'plagMincha': plag_mincha(times),
            'candleLightingPesachMotzash': candle_lighting_motzash(times),
            'talitTfilin': misheyakir(times),
            'dst': bool(date.dst())}
    times.update(data)

    for key in times:
        if type(times[key]) is datetime.datetime:
            times[key] = times[key].astimezone(tz)

    return times


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

    set_location('Givat Zeev', 'Israel', 31.86, 35.17, 'Asia/Jerusalem')
    day_times = get_times(today)

    print("For %s, times are: " % (today.strftime('%a %Y.%m.%d')))
    print("Misheyakir: %s" % day_times['talitTfilin'].strftime('%H:%M'))
    print("Sunrise: %s" % day_times['sunrise'].strftime('%H:%M'))
    print("Sunset: %s" % day_times['sunset'].strftime('%H:%M'))
    print("Plag Mincha: %s" % day_times['plagMincha'].strftime('%H:%M'))
    print("Candle lighting: %s" % day_times['candleLighting'].strftime('%H:%M'))
    print(
        "Candle lighting first night of Pesach on motzash: %s" % day_times['candleLightingPesachMotzash'].strftime(
            '%H:%M'))
    print("First day of chag ends: %s" % day_times['firstDayEnds'].strftime('%H:%M'))
    print("Motzei: %s" % day_times['motzei'].strftime('%H:%M'))
    print("Fast begins: %s" % day_times['fastBegins'].strftime('%H:%M'))
    print("Fast ends: %s" % day_times['fastEnds'].strftime('%H:%M'))
    print("Fast 9 Av ends: %s" % day_times['fast9avEnds'].strftime('%H:%M'))
    print("Eat chametz by: %s" % day_times['chametzEating'].strftime('%H:%M'))
    print("Burn chametz by: %s" % day_times['chametzBurning'].strftime('%H:%M'))
    print("Midnight - finish afikoman before: %s" % day_times['midnight'].strftime('%H:%M'))

    vh = variable_hour(day_times)
    print("Variable hour: GRA: " + str(vh['GRA']) + ', MA: ' + str(vh['MA']))

    print(f"Is DST active? {day_times['dst']}")

#!/usr/bin/python
# -*- coding: UTF-8 -*-

import times
import hebcalendar
import sys
import datetime

from convertdate import hebrew, utils

from oleHelper import *
# from docxHelper import *
# import win32com.client


def PrintRoshHashana(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    minchaErev = dayTimes['candleLighting'] + datetime.timedelta(minutes=5)
    shacharit = "07:30"
    dafYomi = "06:45"

    # Do we say tashlich today?
    tashlich = (day['hebrew'][2] == 1 and day['date'].weekday() != hebcalendar.weekday['shabbat']) \
               or (day['hebrew'][2] == 2 and day['date'].weekday() == hebcalendar.weekday['sunday'])

    # Special case -- Erev Rosh Hashana needs to be put on the calendar even though it's technically for
    # the preceding year
    if day['hebrew'][2] == 1:
        erevDay = day['date'] - datetime.timedelta(days=1)
        dayName = u'יום %s, ' % hebcalendar.hebrew_day_of_week(erevDay.weekday())
        header = u'ערב ראש השנה ('
        header += dayName
        header += u'כ"ט באלול '
        header += erevDay.strftime("%d.%m.%y")
        header += u')'
        set_header(worddoc, {'text': header})

        column1.append((u"סליחות א'", "05:00"))
        column1.append((u"סליחות ב'", "07:00"))
        if erevDay.weekday() == hebcalendar.weekday['wednesday']:
            column1.append(({'text': u'עירוב תבשילין', 'italic': True, 'bold': True},))

        column2.append((u"שחרית מנין א'", "06:05"))
        column2.append((u"שחרית מנין ב'", "08:00"))

        create_populate_table(worddoc, column1, column2)
        set_header(worddoc, {'text': '\n'})

        column1 = []
        column2 = []

    dayName = u'יום %s,' % hebcalendar.hebrew_day_of_week(day['date'].weekday())
    header = u"%s (%s %s - %s)" % (
        ', '.join(a['hebrew'] for a in day['fullnames']), dayName, day['hebrewWritten'], gregDate)
    set_header(worddoc, {'text': header})

    if day['hebrew'][2] == 2:
        dayPrev = holidays[jd-1]
        dayTimesPrev = times.get_times(dayPrev['date'])
        column1.append((u"הדלקת נרות אחרי", dayTimesPrev['firstDayEnds'].strftime("%H:%M")))
    else:
        column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
    if day['hebrew'][2] == 1:
        column1.append((u"מנחה וערבית", minchaErev.strftime("%H:%M")))
    else:
        column1.append((u"ערבית", dayTimes['motzei'].strftime("%H:%M")))
    column1.append((u"שיעור בדף יומי", dafYomi))
    column1.append((u"שחרית", shacharit))

    if dayTimes['candleLighting'].weekday() != hebcalendar.weekday['shabbat']:
        column2.append((u"תקיעת שופר (משוער)", "09:30"))
        column2.append((u"תקיעה שנייה לאחר התפילה",))
    column2.append((u"חצות היום", dayTimes['noon'].strftime("%H:%M")))
    if tashlich:
        minchaK = dayTimes['sunset'] - datetime.timedelta(minutes=(35 + dayTimes['sunset'].minute % 5))
        column2.append((u"מנחה ותשליך", minchaK.strftime("%H:%M")))
    else:
        minchaK = dayTimes['sunset'] - datetime.timedelta(minutes=(20 + dayTimes['sunset'].minute % 5))
        column2.append((u"מנחה", minchaK.strftime("%H:%M")))
    # If it's not Erev Shabbat, add motzei chag line
    if day['hebrew'][2] == 2 and dayTimes['noon'].weekday() != hebcalendar.weekday['friday']:
        column2.append((u'ערבית ומוצ"ח', dayTimes['motzei'].strftime("%H:%M")))

    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})
    return


def PrintYomKippur(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    minchaErev = dayTimes['candleLighting'] + datetime.timedelta(minutes=5)
    shacharit = "08:00"
    dafYomi = "07:15"

    dayName = u'יום %s,' % hebcalendar.hebrew_day_of_week(day['date'].weekday())
    set_header(worddoc, {'text': u"%s (%s %s - %s)" % (
        ', '.join(a['hebrew'] for a in day['fullnames']), dayName, day['hebrewWritten'], gregDate)})

    column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
    column1.append((u"כל נדרי וערבית", minchaErev.strftime("%H:%M")))
    column1.append((u"שיעור לפני שיר הייחוד",))
    column1.append((u"שיעור בדף יומי", dafYomi))
    column1.append((u"שחרית", shacharit))

    column2.append((u'יזכור (משוער)', "10:30"))
    column2.append((u"מנחה", (dayTimes['sunset'] - datetime.timedelta(hours=2, minutes=(
            15 + dayTimes['sunset'].minute % 5))).strftime("%H:%M")))
    column2.append((u"נעילה (משוער)",
                    (dayTimes['sunset'] - datetime.timedelta(minutes=(60 + dayTimes['sunset'].minute % 5))).strftime(
                        "%H:%M")))
    column2.append((u"ערבית ומוצאי חג", dayTimes['motzei'].strftime("%H:%M")))

    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})
    return


def PrintErevYK(jd, day, holidays, dstActive, gregDate):
    dayName = u'יום %s,' % hebcalendar.hebrew_day_of_week(day['date'].weekday())
    set_header(worddoc, {'text': u"%s (%s %s - %s)\n" % \
                                 (', '.join(a['hebrew'] for a in day['fullnames']), dayName, day['hebrewWritten'],
                                  gregDate)})
    text = u'סליחות ושחרית: 06:00 / 08:00'
    text += u' • '
    text += u'מנחה: '
    text += u"13:30"
    text += u'\n'
    set_header(worddoc, {'text': text, 'size': 12, 'bold': False})
    set_header(worddoc, {'text': '\n'})


def PrintChag(jd, day, holidays, dstActive, gregDate):
    pass


def PrintShabbat(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    lateMaariv = dayTimes['motzei'] + datetime.timedelta(minutes=35)
    dayBeforeIsFast = (jd - 1) in holidays and 'fast' in holidays[jd - 1]['type']
    dayBeforeIsChag = (jd - 1) in holidays and any([x in holidays[jd - 1]['type'] for x in ('shabbat', 'chag', 'RH')])
    dayAfterIsChag = (jd + 1) in holidays and any([x in holidays[jd + 1]['type'] for x in ('shabbat', 'chag', 'RH')])
    dayAfterIs9Av = (jd + 1) in holidays and '9av' in holidays[jd + 1]['type']
    dayAfterIsPurim = (jd + 1) in holidays and 'purim' in holidays[jd + 1]['type']
    dayAfterIsPesach = holidays[jd]['hebrew'][1] == 1 and holidays[jd]['hebrew'][2] == 14
    earlyShabbatGadol = holidays[jd]['hebrew'][1] == 1 and holidays[jd]['hebrew'][2] == 7

    # Mincha Erev Shabbat / Chag is 5 minutes after candle lighting
    minchaErev = dayTimes['candleLighting'] + datetime.timedelta(minutes=5)
    if dayBeforeIsFast:
        # If Friday is a fast day, mincha should be 10 minutes earlier for torah reading
        minchaErev -= datetime.timedelta(minutes=10)
    # Mincha Ktana is 1:10 before maariv, rounded back to 5 minutes
    minchaK = dayTimes['motzei'] - datetime.timedelta(minutes=(70 + dayTimes['motzei'].minute % 5))
    if 'shabbat' not in day['type']:
        minchaK = dayTimes['sunset'] - datetime.timedelta(minutes=(15 + dayTimes['sunset'].minute % 5))
    if day['date'].weekday() == hebcalendar.weekday['friday']:
        minchaK = minchaErev
    parentChildLearning = minchaK - datetime.timedelta(minutes=40)
    minchaG = "12:30"
    shacharit = "08:00"
    dafYomi = "07:15"
    isFirstDayPesach = day['hebrew'][1] == 1 and day['hebrew'][2] == 15
    if dstActive:
        minchaG = "13:30"
        shacharit = "08:30"
        dafYomi = "07:45"
    if dayAfterIsPesach:
        shacharit = "07:00"
        dafYomi = "06:15"

    simchatTorah = any([name['english'] == 'Simchat Torah' for name in day['names']])
    chanukah = any([name['english'] == 'Chanukah' for name in day['names']])
    shavuot = any([name['english'] == 'Shavuot' for name in day['names']])
    isShabbatHagadol = any([name['english'] == 'Shabbat Hagadol' for name in day['names']])
    shavuotShacharit = dayTimes['sunrise'] - datetime.timedelta(minutes=20 + dayTimes['sunrise'].minute % 5)
    shavuotRut = shavuotShacharit - datetime.timedelta(minutes=20)
    yizkor = None
    if 'yizkor' in day:
        if location == 'Israel' and simchatTorah:
            yizkor = "12:15"
            shacharit = "08:00"
            dafYomi = "07:15"
        else:
            yizkor = "10:00"

    if dayAfterIs9Av:
        minchaK = datetime.time(17, 00)

    shabbatName = None
    otherName = []

    for fullname in day['fullnames']:
        if (u'שבת' in fullname['hebrew'] or u'פסח' in fullname['hebrew']) and not any(
                x in fullname['hebrew'] for x in (u'הגדול', u'חזון', u'נחמו', u'שובה')):
            shabbatName = fullname['hebrew']
        elif u'סליחות' not in fullname['hebrew']:
            otherName.append(fullname['hebrew'])

    header = None
    dayName = ''
    if 'chag' in day['type']:
        dayName = u'יום %s, ' % hebcalendar.hebrew_day_of_week(day['date'].weekday())
    if shabbatName:
        header = u"%s (%s%s - %s)" % (shabbatName, dayName, day['hebrewWritten'], gregDate)
        if len(otherName):
            header += u' - ' + u', '.join(a for a in otherName)
    else:
        header = u"%s (%s - %s)" % (', '.join(a['hebrew'] for a in day['fullnames']), day['hebrewWritten'], gregDate)
    isShabbatShuva = header.find(u'שובה') != -1

    set_header(worddoc, {'text': header})

    if day['date'].weekday() == hebcalendar.weekday['friday']:
        column1.append(({'text': u'עירוב תבשילין', 'italic': True, 'bold': True},))
        column2.append(('',), )

    if chanukah:
        mincha = "13:30 / " + minchaErev.strftime("%H:%M")
        column1.append((u"מנחה", mincha))
        column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
        column1.append(
            (u"קבלת שבת וערבית", (dayTimes['candleLighting'] + datetime.timedelta(minutes=15)).strftime("%H:%M")))
    elif dayBeforeIsChag:
        if 'shabbat' not in day['type']:
            tfilahTime = dayTimes['motzei']
            if isFirstDayPesach and day['date'].weekday() == hebcalendar.weekday['sunday']:
                tfilahTime = dayTimes['candleLightingPesachMotzash']
            column1.append((u"הדלקת נרות וערבית", tfilahTime.strftime("%H:%M")))
        elif isShabbatShuva:
            column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
            column1.append((u"קבלת שבת וערבית אחרי מנחה",))
        else:
            column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
            column1.append(
                (u"קבלת שבת וערבית", (dayTimes['candleLighting'] + datetime.timedelta(minutes=15)).strftime("%H:%M")))
    elif day['date'].weekday() == hebcalendar.weekday['shabbat']:
        column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
        column1.append((u"מנחה וקבלת שבת", minchaErev.strftime("%H:%M")))
    else:
        column1.append((u"הדלקת נרות", dayTimes['candleLighting'].strftime("%H:%M")))
        column1.append((u"מנחה וערבית", minchaErev.strftime("%H:%M")))
    if isFirstDayPesach:
        column1.append((u'חצות הלילה', (dayTimes['noon'] + datetime.timedelta(hours=12)).strftime("%H:%M")))
    if shavuot:
        column1.append((u'שיעורים כל הלילה לפי לו"ז החג',))
        column1.append((u'קריאת מגילת רות', shavuotRut.strftime("%H:%M")))
        column1.append((u'שחרית ותיקין ', shavuotShacharit.strftime("%H:%M")))
        column2.append((u"שחרית", shacharit))
    else:
        column1.append((u"שיעור בדף יומי", dafYomi))
    if not isFirstDayPesach and not shavuot:
        column1.append((u"שחרית", shacharit))
    if 'shabbat' in day['type'] and day['mevarchim']:
        column1.append(({'text': u"שיעור לנשים אחרי התפילה", 'bold': True},))
    if dayAfterIsPesach:
        column2.append((u"סוף זמן אכילת חמץ", dayTimes['chametzEating'].strftime("%H:%M")))
        column2.append((u"סוף זמן ביעור חמץ", dayTimes['chametzBurning'].strftime("%H:%M")))

    if isFirstDayPesach:
        column2.append((u"שחרית", shacharit))
    if yizkor:
        column2.append((u'יזכור (משוער)', yizkor))
    if not simchatTorah:
        column2.append((u"מנחה גדולה", minchaG))
        # if 'shabbat' in day['type'] and not yizkor and not dayAfterIs9Av:
        #	column2.append((u"לימוד הורים וילדים", parentChildLearning.strftime("%H:%M")))
        if 'chag' not in day['type'] and 'CH' not in day['type'] and not dayAfterIsChag and not dayAfterIs9Av and \
                not dayAfterIsPurim and not isShabbatShuva and not isShabbatHagadol and not earlyShabbatGadol:
            name = u'מנחה קטנה וס"ש'
        else:
            name = u"מנחה קטנה"
        if isShabbatShuva:
            minchaK -= datetime.timedelta(minutes=10)
        # if earlyShabbatGadol or (not earlyShabbatGadol and isShabbatHagadol):
        #     minchaK += datetime.timedelta(minutes=10)
        if isShabbatHagadol and dayAfterIsPesach:
            minchaK += datetime.timedelta(minutes=15)
        column2.append((name, minchaK.strftime("%H:%M")))
    else:
        column2.append((u'מנחה', u'אחרי מוסף'))
    if isShabbatShuva or earlyShabbatGadol or (isShabbatHagadol and not dayAfterIsPesach):
        # column1.append((u'דרשת הרב מוטי אחרי התפילה',))
        # column2.append((u'דרשת הרב טולידאנו', (minchaK + datetime.timedelta(minutes=20)).strftime("%H:%M")))
        column2.append((u'דרשת הרב מוטי', (minchaK + datetime.timedelta(minutes=20)).strftime("%H:%M")))
    if not (dayAfterIsChag or dayAfterIs9Av or dayAfterIsPurim):
        if 'shabbat' in day['type']:
            motzei = dayTimes['motzei'].strftime("%H:%M")
            # As of 5777, we decided NOT to do Motzei early, but instead light candles at shul
            # if chanukah:
            #	# As per Rav Moti's statement, we'll do Maariv 7 minutes early on Chanukah
            #	column2.append((u'ערבית', '%s / %s' % ((dayTimes['motzei'] - datetime.timedelta(minutes=7)).strftime("%H:%M"),lateMaariv.strftime("%H:%M"))))
            #	column2.append((u'מוצאי שבת', motzei))
            # else:
            # As of 5780, Gary asked us to stop listing late maariv -- there aren't enough participants
            # column2.append((u'ערבית ומוצ"ש', '%s / %s' % (motzei, lateMaariv.strftime("%H:%M"))))
            column2.append((u'ערבית ומוצ"ש', motzei))
        elif day['date'].weekday() != hebcalendar.weekday['friday']:
            column2.append((u'ערבית ומוצ"ח', dayTimes['motzei'].strftime("%H:%M")))
    elif dayAfterIs9Av:
        column2.append((u'סוף זמן אכילה ושתיה', dayTimes['sunset'].strftime("%H:%M")))
    elif dayAfterIsPurim:
        column2.append((u'מוצאי שבת', dayTimes['motzei'].strftime("%H:%M")))

    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})
    return


def PrintHoshanaRabah(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    set_header(worddoc, {
        'text': u"%s (%s - %s)" % (', '.join(a['hebrew'] for a in day['fullnames']), day['hebrewWritten'], gregDate)})

    column1.append((u"קריאת משנה תורה בליל הושענא רבה אחרי ערבית",))
    # Moved later because Misheyakir is late. Revisit next year
    column1.append((u"שחרית מנין א' ", '06:00'))

    column2.append((None,))
    column2.append((u"שחרית מנין ב'", '07:30'))
    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})
    return


def PrintRoshChodesh(jd, day, holidays, dstActive, gregDate):
    name = [x['hebrew'] for x in day['names'] if u'ראש' in x['hebrew']][0]
    if name not in holidayDone:
        holidayDone.append(name)
        desc = u''
        twoDay = day['hebrew'][2] == 30
        if twoDay:
            desc += u'ימי ' + hebcalendar.hebrew_day_of_week(
                day['date'].weekday()) + u' - ' + hebcalendar.hebrew_day_of_week(day['date'].weekday() + 1) + u' - '
            desc += name + u" "
            desc += holidays[jd + 1]['date'].strftime("%d.%m.%y")
            desc += u' - ' + day['date'].strftime("%d.%m.%y")
        else:
            desc += u'יום ' + hebcalendar.hebrew_day_of_week(day['date'].weekday()) + u' - '
            desc += name + u" "
            desc += day['date'].strftime("%d.%m.%y")
        # if day['date'].weekday() not in (hebcalendar.weekday['friday'], hebcalendar.weekday['shabbat']):
        if day['date'].weekday() not in (hebcalendar.weekday['shabbat'],):
            earliest = dayTimes['talitTfilin'].replace(hour=5, minute=50)
            shacharitTime = u'05:50'
            if earliest < dayTimes['talitTfilin']:
                shacharitTime = u'06:00'
            desc += u' - שחרית ב%s' % shacharitTime

        set_header(worddoc, {'text': desc})

        column1 = []
        column2 = []

        moladHour = day['molad']['hours'] % 12
        if moladHour == 0:
            moladHour = 12
        text = u'המולד יהיה ביום %s, בשעה %d, ' % (hebcalendar.hebrew_day_of_week(day['molad']['day']), moladHour)
        if day['molad']['minutes']:
            if day['molad']['minutes'] == 1:
                text += u'דקה 1'
            else:
                text += u'%d דקות' % day['molad']['minutes']
            if day['molad']['chalakim']:
                text += u' ו'
        if day['molad']['chalakim'] == 1:
            text += u'חלק 1'
        elif day['molad']['chalakim']:
            text += u'%d חלקים' % day['molad']['chalakim']
        if day['molad']['hours'] < 12:
            text += u' בבוקר'
        elif day['molad']['hours'] == 12 and day['molad']['minutes'] == 0 and day['molad']['chalakim'] == 0:
            text += u' בצהרים'
        else:
            text += u' אחרי הצהרים'
        text += u'\n'
    # For now, not actually printing the molad. Will add this later
    # column1.append((text,))
    # createPopulateTable(worddoc, column1, column2)
    # setHeader(worddoc, {'text': '\n'})
    return


def PrintCholHamoed(jd, day, holidays, dstActive, gregDate):
    # If the first day is Shabbat, it's handled separately. Leave it out.
    if day['date'].weekday() == hebcalendar.weekday['shabbat']:
        return
    name = [x['hebrew'] for x in day['names'] if u'חוה"מ' in x['hebrew']][0]
    if name not in holidayDone:
        holidayDone.append(name)

        dayLast = jd
        while True:
            nextDay = holidays[dayLast + 1]
            if not any([u'חוה"מ' in x['hebrew'] for x in nextDay['names']]):
                break
            dayLast += 1

        lastCH = holidays[dayLast]

        # If the last day is Shabbat, it's handled separately anyway, so go back to Friday
        if lastCH['date'].weekday() == hebcalendar.weekday['shabbat']:
            lastCH = holidays[dayLast - 1]

        desc = name + u' ימי ' + hebcalendar.hebrew_day_of_week(
            day['date'].weekday()) + u' - ' + hebcalendar.hebrew_day_of_week(lastCH['date'].weekday()) + u', '
        desc += hebcalendar.hebrew_number(day['hebrew'][2] - 1) + u' - ' + hebcalendar.hebrew_date(lastCH['hebrew'][1],
                                                                                                   lastCH['hebrew'][2],
                                                                                                   'hebrew')
        desc += " (" + lastCH['date'].strftime("%d.%m.%y") + ' - ' + day['date'].strftime("%d.%m.%y") + ')'

        desc += u'\n'
        set_header(worddoc, {'text': desc})
        text = u'שחרית: 06:00 / 07:30'
        text += u' • '
        text += u'מנחה וערבית: '
        text += (dayTimes['sunset'] - datetime.timedelta(minutes=(15 + dayTimes['sunset'].minute % 5))).strftime(
            "%H:%M")
        text += u' • '
        text += u'ערבית: '
        text += maariv
        text += u'\n'
        set_header(worddoc, {'text': text, 'size': 12, 'bold': False})
        set_header(worddoc, {'text': '\n'})
    return


def PrintRain(js, day, holidays, dstActive, gregData):
    header = u"אור ל-ז' חשון בערבית "
    header += day['date'].strftime("(%d.%m.%y)")
    header += u'\n'
    set_header(worddoc, {'text': header})
    # rain_text = header + u' - '
    rain_text = u'מתחילים לומר "ותן טל ומטר לברכה"'
    rain_text += u'\n'
    set_header(worddoc, {'text': rain_text, 'size': 12, 'bold': False})
    set_header(worddoc, {'text': '\n'})


def PrintFirstbornFast(js, day, holidays, dstActive, gregDate):
    text = u', '.join(a['hebrew'] for a in day['fullnames'])
    text += u' ('
    text += u"יום %s, %s - %s" % (hebcalendar.hebrew_day_of_week(day['date'].weekday()), day['hebrewWritten'], gregDate)
    text += u') '
    text += u'\n'

    set_header(worddoc, {'text': text})
    text = u'סיום לאחר תפילת שחרית ב2 המניינים'
    text += u'\n'
    set_header(worddoc, {'text': text, 'size': 12, 'bold': False})
    set_header(worddoc, {'text': '\n'})


def PrintFastDay(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    text = u', '.join(a['hebrew'] for a in day['fullnames'])
    text += u' ('
    text += u"יום %s, %s - %s" % (hebcalendar.hebrew_day_of_week(day['date'].weekday()), day['hebrewWritten'], gregDate)
    text += u') '
    text += u'\n'

    set_header(worddoc, {'text': text})
    mincha = (dayTimes['sunset'] - datetime.timedelta(minutes=(25 + dayTimes['sunset'].minute % 5))).strftime("%H:%M")
    maariv = (dayTimes['fastEnds'] - datetime.timedelta(minutes=5)).strftime("%H:%M")

    column1.append((u"תחילת הצום", dayTimes['fastBegins'].strftime("%H:%M")))
    column1.append((u"שחרית מניין א'", "05:50"))
    if day['date'].weekday() == hebcalendar.weekday['friday']:
        column2.append((u"שחרית מניין ב'", "08:00"))
    else:
        column1.append((u"שחרית מניין ב'", "08:00"))
        column2.append((u"מנחה", mincha))
        column2.append((u"ערבית", maariv))
        column2.append((u"סוף הצום", dayTimes['fastEnds'].strftime("%H:%M")))

    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})
    return


def PrintIndependance(jd, day, holidays, dstActive, gregDate):
    dayName = []
    omerName = None

    for fullname in day['fullnames']:
        if u'בעומר' in fullname['hebrew'] and not omerName:
            omerName = fullname['hebrew']
        else:
            dayName.append(fullname['hebrew'])
    text = u', '.join(a for a in dayName)
    text += u' ('
    text += u"יום %s, %s - %s" % (hebcalendar.hebrew_day_of_week(day['date'].weekday()), day['hebrewWritten'], gregDate)
    text += u') '
    if omerName:
        text += u' - ' + omerName
    text += u'\n'
    set_header(worddoc, {'text': text})

    column1 = []
    column2 = []

    mincha = (dayTimes['sunset'] - datetime.timedelta(minutes=(25 + dayTimes['sunset'].minute % 5))).strftime(
        "%H:%M")

    column1.append((u"שחרית חגיגית", "07:30"))
    column2.append((u"מנחה וערבית",
                    (dayTimes['sunset'] - datetime.timedelta(minutes=(15 + dayTimes['sunset'].minute % 5))).strftime(
                        "%H:%M")))
    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})
    return


def PrintJerusalem(jd, day, holidays, dstActive, gregDate):
    dayName = []
    omerName = None

    for fullname in day['fullnames']:
        if u'בעומר' in fullname['hebrew'] and not omerName:
            omerName = fullname['hebrew']
        else:
            dayName.append(fullname['hebrew'])
    text = u', '.join(a for a in dayName)
    text += u' ('
    text += u"יום %s, %s - %s" % (hebcalendar.hebrew_day_of_week(day['date'].weekday()), day['hebrewWritten'], gregDate)
    text += u') '
    if omerName:
        text += u' - ' + omerName
    text += u'\n'
    set_header(worddoc, {'text': text})

    maariv = (dayTimes['motzei'] - datetime.timedelta(minutes=(5 + dayTimes['motzei'].minute % 5))).strftime(
        "%H:%M")
    text = u'ערבית חגיגית בערב יום ירושלים: ' + maariv + u'\n'

    set_header(worddoc, {'text': text, 'bold': False})
    set_header(worddoc, {'text': '\n'})


def PrintEsther(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    text = u', '.join(a['hebrew'] for a in day['fullnames'])
    text += u' ('
    text += u"יום %s, %s - %s" % (hebcalendar.hebrew_day_of_week(day['date'].weekday()), day['hebrewWritten'], gregDate)
    text += u') '
    text += u'\n'

    set_header(worddoc, {'text': text})
    mincha = (dayTimes['sunset'] - datetime.timedelta(minutes=(25 + dayTimes['sunset'].minute % 5))).strftime("%H:%M")
    maariv = (dayTimes['fastEnds'] - datetime.timedelta(minutes=5)).strftime("%H:%M")

    column1.append((u"תחילת הצום", dayTimes['fastBegins'].strftime("%H:%M")))
    column1.append((u"שחרית מניין א'", "05:50"))
    column1.append((u"שחרית מניין ב'", "08:00"))

    column2.append((u"מנחה", mincha))
    # Check if Purim is the next day -- this will always be true unless Purim is on Sunday
    if not ((jd + 1) in holidays and 'purim' in holidays[jd + 1]['type']):
        column2.append((u"ערבית", maariv))
    column2.append((u"סוף הצום", dayTimes['fastEnds'].strftime("%H:%M")))
    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})
    return


def PrintGedaliah(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    slichot = u"סליחות עשרת ימי תשובה: 05:25 / 07:30" + u"\n"

    if day['date'].weekday() != hebcalendar.weekday['sunday']:
        set_header(worddoc, {'text': slichot})
        set_header(worddoc, {'text': '\n'})

    text = u', '.join(a['hebrew'] for a in day['fullnames'])
    text += u' ('
    text += u"יום %s, %s - %s" % (hebcalendar.hebrew_day_of_week(day['date'].weekday()), day['hebrewWritten'], gregDate)
    text += u') '
    text += u'\n'

    set_header(worddoc, {'text': text})
    mincha = (dayTimes['sunset'] - datetime.timedelta(minutes=(25 + dayTimes['sunset'].minute % 5))).strftime("%H:%M")
    maariv = (dayTimes['fastEnds'] - datetime.timedelta(minutes=5)).strftime("%H:%M")

    column1.append((u"תחילת הצום", dayTimes['fastBegins'].strftime("%H:%M")))
    column1.append((u"סליחות ושחרית", "05:20"))

    column2.append((u"מנחה", mincha))
    column2.append((u"ערבית", maariv))
    column2.append((u"סוף הצום", dayTimes['fastEnds'].strftime("%H:%M")))
    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})

    if day['date'].weekday() == hebcalendar.weekday['sunday']:
        set_header(worddoc, {'text': slichot})
        set_header(worddoc, {'text': '\n'})
    return


def Print9Av(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    set_header(worddoc, {'text': u"%s (יום %s, %s - %s)" % (
        ', '.join(a['hebrew'] for a in day['fullnames']), hebcalendar.hebrew_day_of_week(day['date'].weekday()),
        day['hebrewWritten'], gregDate)})
    mincha = (dayTimes['sunset'] - datetime.timedelta(minutes=(25 + dayTimes['sunset'].minute % 5)))

    if day['date'].weekday() == hebcalendar.weekday['sunday']:
        column1.append((u'צאת השבת', dayTimes['motzei'].strftime("%H:%M")))
        maariv = dayTimes['motzei'] + datetime.timedelta(minutes=(15 + (5 - dayTimes['motzei'].minute % 5)))
        column1.append((u"ערבית ואיכה", maariv.strftime("%H:%M")))
    else:
        column1.append((u"תחילת הצום", dayTimes['sunset'].strftime("%H:%M")))
        column1.append((u"ערבית ואיכה", "20:10"))
    column1.append((u"שחרית", "07:00"))

    column2.append((u"מנחה", mincha.strftime("%H:%M")))
    column2.append((u"ערבית", (dayTimes['fast9avEnds'] - datetime.timedelta(minutes=5)).strftime("%H:%M")))
    column2.append((u"סוף הצום", dayTimes['fast9avEnds'].strftime("%H:%M")))
    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})
    return


def PrintPurim(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    maariv = dayTimes['fastEnds'] - datetime.timedelta(minutes=(5 + dayTimes['fastEnds'].minute % 5))
    if day['date'].weekday() == hebcalendar.weekday['sunday']:
        # If Purim is Motzei Shabbat, give 30 minutes before Maariv
        maariv = dayTimes['motzei'] + datetime.timedelta(minutes=(40 - dayTimes['motzei'].minute % 5))
    secondReading = maariv + datetime.timedelta(hours=2)
    set_header(worddoc, {'text': u"%s (יום %s, %s - %s)" % (
        ', '.join(a['hebrew'] for a in day['fullnames']), hebcalendar.hebrew_day_of_week(day['date'].weekday()),
        day['hebrewWritten'], gregDate)})

    column1.append((u"ערבית וקריאת מגילה", maariv.strftime("%H:%M")))
    column2.append((u"שחרית וקריאת מגילה", "07:00"))

    column1.append((u"קריאה שניה", secondReading.strftime("%H:%M")))
    column2.append((u"קריאה שניה", "09:30"))

    column2.append((u"מנחה", "13:15"))
    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})
    return


def PrintChanuka(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    if 'chanuka' not in holidayDone:
        holidayDone.append('chanuka')

        chanuka1 = hebrew.to_jd(year, 9, 25)
        chanuka8 = chanuka1 + 7

        # Times according to first day of chanuka.
        dayTimes = times.get_times(day['date'] - datetime.timedelta(days=(jd - chanuka1)))

        day8 = holidays[chanuka8]

        desc = u''
        desc += u"חנוכה, ימים " + hebcalendar.hebrew_day_of_week(
            day8['date'].weekday()) + '-' + hebcalendar.hebrew_day_of_week(day8['date'].weekday()) + ' '
        desc += u'אור לכ"ה כסלו ' + (day8['date'] - datetime.timedelta(days=7)).strftime("%d.%m.%y") + u" עד "
        desc += hebcalendar.hebrew_day_of_month(day8['hebrew'][2] - 1) + u"טבת "
        desc += day8['date'].strftime("%d.%m.%y")

        set_header(worddoc, {'text': desc})

        column1.append((u"שחרית מנין א'", "06:00"))
        column1.append((u"שחרית מנין ב'", "08:00"))

        column2.append((u"מנחה", (
                dayTimes['sunset'] - datetime.timedelta(minutes=(15 + dayTimes['sunset'].minute % 5))).strftime(
            "%H:%M")))
        column2.append((u"ערבית", maariv))

        # for d in range(int(jd-0.5),int(chanuka8+0.5)):
        #	if holidays[d+0.5]['date'].weekday() == hebcalendar.weekday['friday']:
        #		# There's a Friday in Chanuka (well, duh, but specifically for the case of Tevet)
        #		column1.append((u"שחרית מנין א' ביום ו'", "06:00"))
        create_populate_table(worddoc, column1, column2)
        set_header(worddoc, {'text': '\n'})
    return

    # set_header(worddoc, {'text': u"%s (יום %s, %s - %s)" % (
    #     ', '.join(a['hebrew'] for a in day['fullnames']), hebcalendar.hebrew_day_of_week(day['date'].weekday()),
    #     day['hebrewWritten'], gregDate)})


def PrintErevPesach(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    set_header(worddoc, {'text': u"%s (יום %s, %s - %s)" % (
        ', '.join(a['hebrew'] for a in day['fullnames']), hebcalendar.hebrew_day_of_week(day['date'].weekday()),
        day['hebrewWritten'], gregDate)})

    column1.append((u"סוף זמן אכילת חמץ", dayTimes['chametzEating'].strftime("%H:%M")))
    column1.append((u'מנחה גדולה', '13:30'))
    column2.append((u"סוף זמן שריפת חמץ", dayTimes['chametzBurning'].strftime("%H:%M")))
    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})
    return


def PrintErevPesachForShabbatErevPesach(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    text = u"יום %s, %s - %s" % (
        hebcalendar.hebrew_day_of_week(day['date'].weekday()), day['hebrewWritten'], gregDate)
    if 'startDst' in day['type']:
        text += u' - עוברים לשעון קיץ'
    set_header(worddoc, {'text': text})

    column1.append((u"שריפת חמץ", dayTimes['chametzBurning'].strftime("%H:%M")))
    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})
    return


def PrintHoshanaRabah(jd, day, holidays, dstActive, gregDate):
    column1 = []
    column2 = []

    set_header(worddoc, {
        'text': u"%s (%s - %s)" % (', '.join(a['hebrew'] for a in day['fullnames']), day['hebrewWritten'], gregDate)})

    column1.append((u"קריאת משנה תורה בליל הושענא רבה אחרי ערבית",))
    # Moved later because Misheyakir is late. Revisit next year
    column1.append((u"שחרית מנין א' ", '06:00'))

    column2.append((None,))
    column2.append((u"שחרית מנין ב'", '07:30'))
    create_populate_table(worddoc, column1, column2)
    set_header(worddoc, {'text': '\n'})
    return


def PrintSlichot(jd, day, holidays, dstActive, gregDate):
    name = day['names'][0]
    if name not in holidayDone:
        holidayDone.append(name)

        dayLast = jd
        while True:
            try:
                nextDay = holidays[dayLast + 1]
                if 'slichot' not in nextDay['type']:
                    break
            except KeyError:
                break
            dayLast += 1

        first = holidays[jd + 1]
        if utils.jwday(dayLast) == hebcalendar.weekday['shabbat']:
            dayLast -= 1
        last = holidays[dayLast]

        desc = u'סליחות: מוצ"ש '
        desc += u' ('
        desc += u"יום %s, %s - %s" % (
            hebcalendar.hebrew_day_of_week(day['date'].weekday()), day['hebrewWritten'], gregDate)
        desc += u'): '
        desc += u'שעה ' + (
                dayTimes['noon'] - datetime.timedelta(hours=12, minutes=(dayTimes['noon'].minute % 5))).strftime(
            "%H:%M")
        desc += u'\n'
        set_header(worddoc, {'text': desc})
        set_header(worddoc, {'text': '\n'})

        desc = u"סליחות: "

        desc += u' ימי ' + hebcalendar.hebrew_day_of_week(
            first['date'].weekday()) + u' - ' + hebcalendar.hebrew_day_of_week(last['date'].weekday()) + u', '
        desc += hebcalendar.hebrew_number(first['hebrew'][2] - 1) + u' - ' + hebcalendar.hebrew_date(last['hebrew'][1],
                                                                                                     last['hebrew'][2],
                                                                                                     'hebrew')
        desc += " (" + last['date'].strftime("%d.%m.%y") + ' - ' + first['date'].strftime("%d.%m.%y") + '): '
        desc += u'07:40 / 05:35'
        desc += u'\n'
        set_header(worddoc, {'text': desc})
        set_header(worddoc, {'text': '\n'})


### 
# Need to add:
# DST switch -- DST currently works as long as there's nothing else on that day

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
    holidays = hebcalendar.get_month(year, month, location)
else:
    holidays = hebcalendar.get_year(year, location)

times.set_location('Givat Zeev', 'Israel', 31.86, 35.17, 'Asia/Jerusalem')

worddoc = create_doc()

for jd in sorted(holidays):
    day = holidays[jd]
    dayTimes = times.get_times(day['date'])
    if monthName is None:
        monthName = hebcalendar.get_hebrew_month(month, 'english')

    dstActive = dayTimes['dst']

    gregDate = day['date'].strftime("%d.%m.%y")

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
        PrintRoshHashana(jd, day, holidays, dstActive, gregDate)
    elif 'YK' in day['type']:
        PrintYomKippur(jd, day, holidays, dstActive, gregDate)
    # Shabbat or chag, unless it's Shabbat and 2nd day RC for next month
    elif ('shabbat' in day['type'] or 'chag' in day['type']) and month == day['hebrew'][1]:
        PrintShabbat(jd, day, holidays, dstActive, gregDate)
    elif 'RC' in day['type']:
        PrintRoshChodesh(jd, day, holidays, dstActive, gregDate)
    elif 'HR' in day['type']:
        PrintHoshanaRabah(jd, day, holidays, dstActive, gregDate)
    elif 'CH' in day['type']:
        PrintCholHamoed(jd, day, holidays, dstActive, gregDate)
    elif 'fast' in day['type']:
        PrintFastDay(jd, day, holidays, dstActive, gregDate)
    elif 'esther' in day['type']:
        PrintEsther(jd, day, holidays, dstActive, gregDate)
    elif 'gedaliah' in day['type']:
        PrintGedaliah(jd, day, holidays, dstActive, gregDate)
    elif 'jerusalem' in day['type']:
        PrintJerusalem(jd, day, holidays, dstActive, gregDate)
    elif '9av' in day['type']:
        Print9Av(jd, day, holidays, dstActive, gregDate)
    elif 'purim' in day['type']:
        PrintPurim(jd, day, holidays, dstActive, gregDate)
    elif 'chanuka' in day['type']:
        PrintChanuka(jd, day, holidays, dstActive, gregDate)
    elif 'erevPesach' in day['type']:
        PrintErevPesach(jd, day, holidays, dstActive, gregDate)
    elif 'independance' in day['type']:
        PrintIndependance(jd, day, holidays, dstActive, gregDate)
    elif 'preErevPesach' in day['type']:
        PrintErevPesachForShabbatErevPesach(jd, day, holidays, dstActive, gregDate)
    elif 'erevRH' in day['type']:
        desc = u'סליחות: '
        desc += u"%s (%s - %s)" % (', '.join(a['hebrew'] for a in day['fullnames']), day['hebrewWritten'], gregDate)
        desc += u': 07:00 / 05:00\n'
        set_header(worddoc, {'text': desc})
        set_header(worddoc, {'text': '\n'})
    elif 'erevYK' in day['type']:
        PrintErevYK(jd, day, holidays, dstActive, gregDate)
    elif 'slichot' in day['type']:
        PrintSlichot(jd, day, holidays, dstActive, gregDate)
    elif 'firstborn' in day['type']:
        PrintFirstbornFast(jd, day, holidays, dstActive, gregDate)
    elif 'rain' in day['type']:
        PrintRain(jd, day, holidays, dstActive, gregDate)
    elif 'startDst' in day['type'] or 'endDst' in day['type']:
        clock = None
        if 'startDst' in day['type']:
            clock = u'קיץ' + '\n'
        else:
            clock = u'חורף' + '\n'
        text = u"יום %s, %s - %s" % (
            hebcalendar.hebrew_day_of_week(day['date'].weekday()), day['hebrewWritten'], gregDate)
        text += u' - עוברים לשעון %s\n' % clock
        set_header(worddoc, {'text': text})
    elif 'omer' in day['type'] and len(day['type']) == 1:
        pass
    else:
        dayName = []
        omerName = None

        for fullname in day['fullnames']:
            if u'בעומר' in fullname['hebrew'] and not omerName:
                omerName = fullname['hebrew']
            else:
                dayName.append(fullname['hebrew'])
        text = u', '.join(a for a in dayName)
        text += u' ('
        text += u"יום %s, %s - %s" % (
            hebcalendar.hebrew_day_of_week(day['date'].weekday()), day['hebrewWritten'], gregDate)
        text += u') '
        if omerName:
            text += u' - ' + omerName
        text += u'\n'
        set_header(worddoc, {'text': text})
        set_header(worddoc, {'text': '\n'})

save_doc(worddoc, monthName, year)

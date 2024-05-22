#!/usr/bin/env python
# compatible with python 2.x and 3.x
import math
import re
from datetime import datetime, timedelta, date
import pytz


'''
--------------------- Copyright Block ----------------------

praytimes.py: Prayer Times Calculator (ver 2.3)
Copyright (C) 2007-2011 PrayTimes.org

Python Code: Saleem Shafi, Hamid Zarrabi-Zadeh
Original js Code: Hamid Zarrabi-Zadeh

License: GNU LGPL v3.0

TERMS OF USE:
	Permission is granted to use this code, with or
	without modification, in any website or application
	provided that credit is given to the original work
	with a link back to PrayTimes.org.

This program is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY.

PLEASE DO NOT REMOVE THIS COPYRIGHT BLOCK.


--------------------- Help and Manual ----------------------

User's Manual:
http://praytimes.org/manual

Calculation Formulas:
http://praytimes.org/calculation


------------------------ User Interface -------------------------

	getTimes (date, coordinates, timeZone [, dst [, timeFormat]])

	setMethod (method)       // set calculation method
	adjust (parameters)      // adjust calculation parameters
	tune (offsets)           // tune times by given offsets

	getMethod ()             // get calculation method
	getSetting ()            // get current calculation parameters
	getOffsets ()            // get current time offsets


------------------------- Sample Usage --------------------------

	>>> PT = PrayTimes('ISNA')
	>>> times = PT.getTimes((2011, 2, 9), (43, -80), -5)
	>>> times['sunrise']
	07:26

'''


# ----------------------- PrayTimes Class ------------------------

class PrayTimes():
    # ------------------------ Constants --------------------------

    # Time Names
    timeNames = {
        'imsak': 'Imsak',
        'fajr': 'Fajr',
        'sunrise': 'Sunrise',
        'dhuhr': 'Dhuhr',
        'asr': 'Asr',
        'sunset': 'Sunset',
        'maghrib': 'Maghrib',
        'isha': 'Isha',
        'midnight': 'Midnight'
    }

    # Calculation Methods
    methods = {
        'MWL': {
            'name': 'Muslim World League',
            'params': {'fajr': 18, 'isha': 17}},
        'ISNA': {
            'name': 'Islamic Society of North America (ISNA)',
            'params': {'fajr': 15, 'isha': 15}},
        'Egypt': {
            'name': 'Egyptian General Authority of Survey',
            'params': {'fajr': 19.5, 'isha': 17.5}},
        'Makkah': {
            'name': 'Umm Al-Qura University, Makkah',
            'params': {'fajr': 18.5, 'isha': '90 min'}},  # fajr was 19 degrees before 1430 hijri
        'Karachi': {
            'name': 'University of Islamic Sciences, Karachi',
            'params': {'fajr': 18, 'isha': 18}},
        'Tehran': {
            'name': 'Institute of Geophysics, University of Tehran',
            'params': {'fajr': 17.7, 'isha': 14, 'maghrib': 4.5, 'midnight': 'Jafari'}},
        # isha is not explicitly specified in this method
        'Jafari': {
            'name': 'Shia Ithna-Ashari, Leva Institute, Qum',
            'params': {'fajr': 16, 'isha': 14, 'maghrib': 4, 'midnight': 'Jafari'}},
        # BCMA method
        'BCMA': {
            'name': 'British Columbia Muslim Association, BC, Canada',
            'params': {'fajr': 18, 'isha': 15, 'maghrib': '1 min', 'midnight': 'Standard'}}

    }

    # Default Parameters in Calculation Methods
    defaultParams = {
        'maghrib': '0 min', 'midnight': 'Standard'
    }

    # ---------------------- Default Settings --------------------

    calcMethod = 'BCMA'

    # do not change anything here; use adjust method instead
    settings = {
        "imsak": '1 min',
        "dhuhr": '0 min',
        "asr": 'Standard',
        "highLats": 'AngleBased'
    }

    # Settings for Iqamah times
    iqamah_settings = {
        "fajr_step": 15,  # Step size in minutes (e.g., 5:00, 5:15, 5:30, and 5:45 for step of 15 minutes
        "asr_step": 15,  # Step size in minutes (e.g., 5:00, 5:15, 5:30, and 5:45 for step of 15 minutes
        "maghrib_step": 5,  # Step size in minutes (e.g., 5:00, 5:05, 5:10, and 5:15 for step of 5 minutes
        "isha_step": 15,  # Step size in minutes (e.g., 5:00, 5:15, 5:30, and 5:45 for step of 15 minutes

        "fajr_min_time": 31,  # Minimum time between sunset and Fajr iqamah in minutes
        "asr_min_time": 7,  # Minimum time between Asr azan and iqamah in minutes
        "maghrib_min_time": 3,  # Minimum time between Maghrib azan and iqamah in minutes
        "isha_min_time": 7,  # Minimum time between Isha azan and iqamah in minutes

        "fajr_latest_time": 420,    # Latest time of Fajr iqamah in minutes (e.g., 07:00 -> 420)
        "asr_earliest_time": 870,   # Earliest time of Asr iqamah in minutes (e.g., 14:30 -> 870)
        "isha_earliest_time": 1125, # Earliest time of Isha iqamah in minutes (e.g., 18:45 -> 1125)
        "isha_latest_time": 1400,   # Latest time of Isha iqamah in minutes (e.g., 23:20 -> 1400)

        # Dhuhr settings
        "dhuhr_winter_iqamah": 740, # Iqamah time for Dhuhr during winter (no daylight savings) in minutes
        "dhuhr_summer_iqamah": 800, # Iqamah time for Dhuhr during summer (with daylight savings) in minutes
        
        # Jumuah settings
        "jumuah_winter_iqamah": 765,  # Iqamah time for Dhuhr during winter (no daylight savings) in minutes
        "jumuah_summer_iqamah": 840,  # Iqamah time for Dhuhr during summer (with daylight savings) in minutes

        # Ramadan settings
        "Ramadan_start": date(2024, 3, 10), # Replace with actual Ramadan's start date
        "Ramadan_end": date(2024, 4, 9),   # Replace with actual Ramadan's end date

        "fajr_Ramadan_step": 5,  # Step size in minutes (e.g., 5:00, 5:15, 5:30, and 5:45 for step of 15 minutes
        "fajr_Ramadan_min_time": 15,    # Minimum time between Fajr azan and iqamah in minutes
        "maghrib_Ramadan_min_time": 8,  # Minimum time between Maghrib azan and iqamah in minutes
        "isha_Ramadan_step": 10,  # Step size in minutes (e.g., 5:00, 5:15, 5:30, and 5:45 for step of 15 minutes
    }

    timeFormat = '24h'
    timeSuffixes = ['am', 'pm']
    invalidTime = '-----'

    numIterations = 1
    offset = {}

    # ---------------------- Initialization -----------------------

    def __init__(self, method="BCMA"):

        # set methods defaults
        for method, config in self.methods.items():
            for name, value in self.defaultParams.items():
                if not name in config['params'] or config['params'][name] is None:
                    config['params'][name] = value

        # initialize settings
        self.calcMethod = method if method in self.methods else 'MWL'
        params = self.methods[self.calcMethod]['params']
        for name, value in params.items():
            self.settings[name] = value

        # init time offsets
        for name in self.timeNames:
            self.offset[name] = 0

    # -------------------- Interface Functions --------------------

    def setMethod(self, method):
        if method in self.methods:
            self.adjust(self.methods[method].params)
            self.calcMethod = method

    def adjust(self, params):
        self.settings.update(params)

    def tune(self, timeOffsets):
        self.offsets.update(timeOffsets)

    def getMethod(self):
        return self.calcMethod

    def getSettings(self):
        return self.settings

    def getOffsets(self):
        return self.offset

    def getDefaults(self):
        return self.methods

    # return prayer times for a given date
    def getTimes(self, date, coords, timezone, dst=0, format=None):
        self.lat = coords[0]
        self.lng = coords[1]
        self.elv = coords[2] if len(coords) > 2 else 0
        if format != None:
            self.timeFormat = format
        if type(date).__name__ == 'date':
            date = (date.year, date.month, date.day)
        self.timeZone = timezone + (1 if dst else 0)
        self.jDate = self.julian(date[0], date[1], date[2]) - self.lng / (15 * 24.0)
        return self.computeTimes()

    # convert float time to the given format (see timeFormats)
    def getFormattedTime(self, time, format, suffixes=None):
        if math.isnan(time):
            return self.invalidTime
        if format == 'Float':
            return time
        if suffixes == None:
            suffixes = self.timeSuffixes

        time = self.fixhour(time + 0.5 / 60)  # add 0.5 minutes to round
        hours = math.floor(time)

        minutes = math.floor((time - hours) * 60)
        suffix = suffixes[0 if hours < 12 else 1] if format == '12h' else ''
        formattedTime = "%02d:%02d" % (hours, minutes) if format == "24h" else "%d:%02d" % (
            (hours + 11) % 12 + 1, minutes)
        return formattedTime + suffix

    # ---------------------- Calculation Functions -----------------------

    # compute mid-day time
    def midDay(self, time):
        eqt = self.sunPosition(self.jDate + time)[1]
        return self.fixhour(12 - eqt)

    # compute the time at which sun reaches a specific angle below horizon
    def sunAngleTime(self, angle, time, direction=None):
        try:
            decl = self.sunPosition(self.jDate + time)[0]
            noon = self.midDay(time)
            t = 1 / 15.0 * self.arccos((-self.sin(angle) - self.sin(decl) * self.sin(self.lat)) /
                                       (self.cos(decl) * self.cos(self.lat)))
            return noon + (-t if direction == 'ccw' else t)
        except ValueError:
            return float('nan')

    # compute asr time
    def asrTime(self, factor, time):
        decl = self.sunPosition(self.jDate + time)[0]
        angle = -self.arccot(factor + self.tan(abs(self.lat - decl)))
        return self.sunAngleTime(angle, time)

    # compute declination angle of sun and equation of time
    # Ref: http://aa.usno.navy.mil/faq/docs/SunApprox.php
    def sunPosition(self, jd):
        D = jd - 2451545.0
        g = self.fixangle(357.529 + 0.98560028 * D)
        q = self.fixangle(280.459 + 0.98564736 * D)
        L = self.fixangle(q + 1.915 * self.sin(g) + 0.020 * self.sin(2 * g))

        R = 1.00014 - 0.01671 * self.cos(g) - 0.00014 * self.cos(2 * g)
        e = 23.439 - 0.00000036 * D

        RA = self.arctan2(self.cos(e) * self.sin(L), self.cos(L)) / 15.0
        eqt = q / 15.0 - self.fixhour(RA)
        decl = self.arcsin(self.sin(e) * self.sin(L))

        return (decl, eqt)

    # convert Gregorian date to Julian day
    # Ref: Astronomical Algorithms by Jean Meeus
    def julian(self, year, month, day):
        if month <= 2:
            year -= 1
            month += 12
        A = math.floor(year / 100)
        B = 2 - A + math.floor(A / 4)
        return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5

    # ---------------------- Compute Prayer Times -----------------------

    # compute prayer times at given julian date
    def computePrayerTimes(self, times):
        times = self.dayPortion(times)
        params = self.settings

        imsak = self.sunAngleTime(self.eval(params['imsak']), times['imsak'], 'ccw')
        fajr = self.sunAngleTime(self.eval(params['fajr']), times['fajr'], 'ccw')
        sunrise = self.sunAngleTime(self.riseSetAngle(self.elv), times['sunrise'], 'ccw')
        dhuhr = self.midDay(times['dhuhr'])
        asr = self.asrTime(self.asrFactor(params['asr']), times['asr'])
        sunset = self.sunAngleTime(self.riseSetAngle(self.elv), times['sunset'])
        maghrib = self.sunAngleTime(self.eval(params['maghrib']), times['maghrib'])
        isha = self.sunAngleTime(self.eval(params['isha']), times['isha'])
        return {
            'imsak': imsak, 'fajr': fajr, 'sunrise': sunrise, 'dhuhr': dhuhr,
            'asr': asr, 'sunset': sunset, 'maghrib': maghrib, 'isha': isha
        }

    # compute prayer times
    def computeTimes(self):
        times = {
            'imsak': 5, 'fajr': 5, 'sunrise': 6, 'dhuhr': 12,
            'asr': 13, 'sunset': 18, 'maghrib': 18, 'isha': 18
        }
        # main iterations
        for i in range(self.numIterations):
            times = self.computePrayerTimes(times)
        times = self.adjustTimes(times)
        # add midnight time
        if self.settings['midnight'] == 'Jafari':
            times['midnight'] = times['sunset'] + self.timeDiff(times['sunset'], times['fajr']) / 2
        else:
            times['midnight'] = times['sunset'] + self.timeDiff(times['sunset'], times['sunrise']) / 2

        times = self.tuneTimes(times)
        return self.modifyFormats(times)

    # adjust times in a prayer time array
    def adjustTimes(self, times):
        params = self.settings
        tzAdjust = self.timeZone - self.lng / 15.0
        for t, v in times.items():
            times[t] += tzAdjust

        if params['highLats'] != 'None':
            times = self.adjustHighLats(times)

        if self.isMin(params['imsak']):
            times['imsak'] = times['fajr'] - self.eval(params['imsak']) / 60.0
        # need to ask about 'min' settings
        if self.isMin(params['maghrib']):
            times['maghrib'] = times['sunset'] - self.eval(params['maghrib']) / 60.0

        if self.isMin(params['isha']):
            times['isha'] = times['maghrib'] - self.eval(params['isha']) / 60.0
        times['dhuhr'] += self.eval(params['dhuhr']) / 60.0

        return times

    # get asr shadow factor
    def asrFactor(self, asrParam):
        methods = {'Standard': 1, 'Hanafi': 2}
        return methods[asrParam] if asrParam in methods else self.eval(asrParam)

    # return sun angle for sunset/sunrise
    def riseSetAngle(self, elevation=0):
        elevation = 0 if elevation == None else elevation
        return 0.833 + 0.0347 * math.sqrt(elevation)  # an approximation

    # apply offsets to the times
    def tuneTimes(self, times):
        for name, value in times.items():
            times[name] += self.offset[name] / 60.0
        return times

    # convert times to given time format
    def modifyFormats(self, times):
        for name, value in times.items():
            times[name] = self.getFormattedTime(times[name], self.timeFormat)
        return times

    # adjust times for locations in higher latitudes
    def adjustHighLats(self, times):
        params = self.settings
        nightTime = self.timeDiff(times['sunset'], times['sunrise'])  # sunset to sunrise
        times['imsak'] = self.adjustHLTime(times['imsak'], times['sunrise'], self.eval(params['imsak']), nightTime,
                                           'ccw')
        times['fajr'] = self.adjustHLTime(times['fajr'], times['sunrise'], self.eval(params['fajr']), nightTime, 'ccw')
        times['isha'] = self.adjustHLTime(times['isha'], times['sunset'], self.eval(params['isha']), nightTime)
        times['maghrib'] = self.adjustHLTime(times['maghrib'], times['sunset'], self.eval(params['maghrib']), nightTime)
        return times

    # adjust a time for higher latitudes
    def adjustHLTime(self, time, base, angle, night, direction=None):
        portion = self.nightPortion(angle, night)
        diff = self.timeDiff(time, base) if direction == 'ccw' else self.timeDiff(base, time)
        if math.isnan(time) or diff > portion:
            time = base + (-portion if direction == 'ccw' else portion)
        return time

    # the night portion used for adjusting times in higher latitudes
    def nightPortion(self, angle, night):
        method = self.settings['highLats']
        portion = 1 / 2.0  # midnight
        if method == 'AngleBased':
            portion = 1 / 60.0 * angle
        if method == 'OneSeventh':
            portion = 1 / 7.0
        return portion * night

    # convert hours to day portions
    def dayPortion(self, times):
        for i in times:
            times[i] /= 24.0
        return times

    # ---------------------- Misc Functions -----------------------

    # compute the difference between two times
    def timeDiff(self, time1, time2):
        return self.fixhour(time2 - time1)

    # convert given string into a number
    def eval(self, st):
        val = re.split('[^0-9.+-]', str(st), 1)[0]
        return float(val) if val else 0

    # detect if input contains 'min'
    def isMin(self, arg):
        return isinstance(arg, str) and arg.find('min') > -1

    # ----------------- Degree-Based Math Functions -------------------

    def sin(self, d):
        return math.sin(math.radians(d))

    def cos(self, d):
        return math.cos(math.radians(d))

    def tan(self, d):
        return math.tan(math.radians(d))

    def arcsin(self, x):
        return math.degrees(math.asin(x))

    def arccos(self, x):
        return math.degrees(math.acos(x))

    def arctan(self, x):
        return math.degrees(math.atan(x))

    def arccot(self, x):
        return math.degrees(math.atan(1.0 / x))

    def arctan2(self, y, x):
        return math.degrees(math.atan2(y, x))

    def fixangle(self, angle):
        return self.fix(angle, 360.0)

    def fixhour(self, hour):
        return self.fix(hour, 24.0)

    def fix(self, a, mode):
        if math.isnan(a):
            return a
        a = a - mode * (math.floor(a / mode))
        return a + mode if a < 0 else a

    # =====================================================================
    # calculating the iqamah times for the prayer

    def calculate_iqamah_times(self, prayer_times, dst, current_date):
        def excel_time(hours, minutes, seconds=0):
            minutes += seconds // 60
            hours += minutes // 60
            minutes %= 60
            hours %= 24
            return datetime.strptime(f"{hours:02d}:{minutes:02d}", "%H:%M")

        def parse_time(time_str):
            return datetime.strptime(time_str, "%H:%M")

        sunrise = parse_time(prayer_times['sunrise'])
        dhuhr = parse_time(prayer_times['dhuhr'])
        asr = parse_time(prayer_times['asr'])
        maghrib = parse_time(prayer_times['maghrib'])
        isha = parse_time(prayer_times['isha'])

        # Comversion of excel formulas into python based formulas
        fajr_iqamah = excel_time(0,
                                 min(self.iqamah_settings['fajr_latest_time'],
                                     self.iqamah_settings['fajr_step'] * ((60 * sunrise.hour + sunrise.minute -
                                                                           self.iqamah_settings['fajr_min_time']) //
                                                                          self.iqamah_settings['fajr_step'])))

        dhuhr_iqamah = excel_time(0, self.iqamah_settings["dhuhr_winter_iqamah"])
        if dst:
            dhuhr_iqamah = excel_time(0, self.iqamah_settings["dhuhr_summer_iqamah"])
            
        if current_date.weekday()==4:
            dhuhr_iqamah = excel_time(0, self.iqamah_settings["jumuah_winter_iqamah"])
            if dst:
                dhuhr_iqamah = excel_time(0, self.iqamah_settings["jumuah_summer_iqamah"])
        
        
        asr_iqamah = excel_time(0,
                                max(self.iqamah_settings['asr_earliest_time'],
                                    self.iqamah_settings['asr_step'] * (1 + (
                                                60 * asr.hour + asr.minute + self.iqamah_settings[
                                            'asr_min_time'] - 1) // self.iqamah_settings['asr_step'])))
        maghrib_iqamah = excel_time(0,
                                    self.iqamah_settings['maghrib_step'] * (1 + (
                                                60 * maghrib.hour + maghrib.minute + self.iqamah_settings[
                                            'maghrib_min_time'] - 1) // self.iqamah_settings['maghrib_step']))
        isha_iqamah = excel_time(0,
                                 min(self.iqamah_settings['isha_latest_time'],
                                     max(self.iqamah_settings['isha_earliest_time'],
                                         self.iqamah_settings['isha_step'] * (1 + (
                                                     60 * isha.hour + isha.minute + + self.iqamah_settings[
                                                 'isha_min_time'] - 1) // self.iqamah_settings['isha_step']))))
        
        # Adjust iqamah times during Ramadan
        if self.is_Ramadan(current_date):
            fajr = parse_time(prayer_times['fajr'])
            fajr_iqamah = excel_time(0,
                                        self.iqamah_settings['fajr_Ramadan_step'] * (1 + (
                                                60 * fajr.hour + fajr.minute + self.iqamah_settings[
                                            'fajr_Ramadan_min_time'] - 1) // self.iqamah_settings['fajr_Ramadan_step']))
            maghrib_iqamah = excel_time(0,
                                        self.iqamah_settings['maghrib_step'] * (1 + (
                                                60 * maghrib.hour + maghrib.minute + self.iqamah_settings[
                                            'maghrib_Ramadan_min_time'] - 1) // self.iqamah_settings['maghrib_step']))
            isha_iqamah = excel_time(0,
                                     min(self.iqamah_settings['isha_latest_time'],
                                         max(self.iqamah_settings['isha_earliest_time'],
                                             self.iqamah_settings['isha_Ramadan_step'] * (1 + (
                                                     60 * isha.hour + isha.minute + + self.iqamah_settings[
                                                 'isha_min_time'] - 1) // self.iqamah_settings['isha_Ramadan_step']))))


        iqamah_times = {
            'fajr_iqamah': fajr_iqamah.strftime('%H:%M'),
            'dhuhr_iqamah': dhuhr_iqamah.strftime('%H:%M'),
            'asr_iqamah': asr_iqamah.strftime('%H:%M'),
            'maghrib_iqamah': maghrib_iqamah.strftime('%H:%M'),
            'isha_iqamah': isha_iqamah.strftime('%H:%M')
        }

        return {**prayer_times, **iqamah_times}

    def getPrayerAndIqamahTimes(self, date, coords, timezone, dst=0, format=None):
        prayer_times = self.getTimes(date, coords, timezone, dst, format)
        # Make sure to pass 'date' as the last argument
        return self.calculate_iqamah_times(prayer_times, dst, date)


    # Function to check if a date falls within Ramadan
    def is_Ramadan(self, current_date):
        return self.iqamah_settings["Ramadan_start"] <= current_date <= self.iqamah_settings["Ramadan_end"]

def is_dst(dt_date, timezone_name):
	"""
	Determine if a given date (dt_date) for a given timezone (timezone_name) is in DST.
	"""
	timezone = pytz.timezone(timezone_name)
	dt_datetime = datetime.combine(dt_date, datetime.min.time())  # Convert date to datetime
	dt_aware = timezone.localize(dt_datetime + timedelta(1))
	return dt_aware.dst() != timedelta(0)


# Example usage:
if __name__ == "__main__":
    from datetime import date
    import calendar

    # Create a PrayTimes object with specific settings
    PT = PrayTimes()
    # PT.adjust({'fajr': 18, 'isha': 15})
    # PT.adjust({'highLats': 'AngleBased'})

    # Print prayer and iqamah times for December 2023 at a specific location
    # change this to test different years or month
    year = 2024
    month = 5
    num_days = calendar.monthrange(year, month)[1]  # Number of days in December
    location_coords = (50.6833, -120.333, 40)  # Latitude, Longitude
    timezone = -8  # Timezone offset
    timezone_name = 'America/Vancouver'


    print(f'Prayer and Iqamah Times for December {year} in Kamloops, Canada\n' + ('=' * 70))
    print('{:<12} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<10} {:<10} {:<10} {:<10} {:<10}'.format(
        'Date', 'Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha', 'Fajr Iqamah', 'Dhuhr Iqamah', 'Asr Iqamah',
        'Maghrib Iqamah', 'Isha Iqamah'))

    for day in range(1, num_days + 1):
        current_date = date(year, month, day)

        times = PT.getPrayerAndIqamahTimes(current_date, location_coords, timezone, dst=is_dst(current_date, timezone_name))

        print('{:<12}, {:<12}, {:<12}, {:<12}, {:<12}, {:<12}, {:<12}, {:<12}, {:<12}, {:<12}, {:<12}, {:<12}'.format(
            current_date.strftime('%Y-%m-%d'),
            times['fajr'],
            times['fajr_iqamah'],
            times['sunrise'],
            times['dhuhr'],
            times['dhuhr_iqamah'],
            times['asr'],
            times['asr_iqamah'],
            times['maghrib'],
            times['maghrib_iqamah'],
            times['isha'],
            times['isha_iqamah']
        ))

    print('=' * 70)

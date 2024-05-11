from django.shortcuts import render

from datetime import date, timedelta
from KamloopsPrayersTiming import *  # Assuming the PrayTimes class is in KamloopsPrayerTiming.py

from django.http import JsonResponse
import calendar
from .models import Contact , IqamahAdjustment, RamadanDate

from datetime import datetime, time
import calendar
from django.shortcuts import render
 
 
# view to generate the home page

def index(request):
	if request.method == 'POST':
		# Create an instance of your model and save the form data
		email = request.POST.get('email')
		name = request.POST.get('name')
		message = request.POST.get('message')
		
		# Assuming your model is named `Contact` and has `email`, `name`, and `message` fields
		contact = Contact(email=email, name=name, message=message)
		contact.save()
		
		# Redirect or send a success response
		return JsonResponse({'success': 'Message sent successfully!'})
		 
	# Render index page for GET requests
	return render(request, 'index.html')



#views function that calculates the prayer time for kamloops with all adjustments and renders prayer page

 

 
# Assuming you have a function to determine if a date is in Ramadan
def is_ramadan(date):
    try:
        ramadan = RamadanDate.objects.get(year=date.year)
        return ramadan.start_date <= date <= ramadan.end_date
    except RamadanDate.DoesNotExist:
        return False

def get_adjusted_times(date, default_times, is_ramadan_now):
    adjustments = IqamahAdjustment.objects.filter(date=date)
    for adj in adjustments:
        default_times[adj.prayer_name.lower() + '_iqamah'] = adj.iqamah_time.strftime('%H:%M')
    # During Ramadan, replace Fajr time with Imsak time but still label it as Fajr
    if is_ramadan_now:
        default_times['fajr'] = default_times.get('imsak', default_times['fajr'])
    return default_times

def prayer_times_view(request, year=None, month=None):
    today = datetime.today().date()
    year = year or today.year
    month = month or today.month

    PT = PrayTimes("BCMA")
    timezone_name = 'America/Vancouver'
    num_days = calendar.monthrange(year, month)[1]
    month_name = calendar.month_name[month]

    calendar_data = []
    for day in range(1, num_days + 1):
        current_date = datetime(year, month, day).date()
        is_ramadan_now = is_ramadan(current_date)
        dst = is_dst(current_date, timezone_name)
        timezone_offset = -8 
        times = PT.getPrayerAndIqamahTimes(current_date, (50.671016, -120.3637572, 40), timezone_offset, dst=dst)
        times = get_adjusted_times(current_date, times, is_ramadan_now)
        calendar_data.append({'date': current_date, 'times': times, 'is_ramadan': is_ramadan_now})

    # Adjust today's times
    is_ramadan_today = is_ramadan(today)
    dst_today = is_dst(today, timezone_name)
    timezone_offset_today = -8 
    today_times = PT.getPrayerAndIqamahTimes(today, (50.671016, -120.3637572, 40), timezone_offset_today, dst=dst)
    today_times = get_adjusted_times(today, today_times, is_ramadan_today)

    context = {
        'calendar_data': calendar_data,
        'year': year,
        'month': month,
        'today_times': today_times,
        'month_name': month_name,
        'today': today,
        'is_ramadan_today': is_ramadan_today,
    }

    return render(request, 'prayer.html', context)





def test_page(request):
	
 
	context = {
		 
	} 
	return render(request,'test.html', context)
def team(request):
	
 
	context = {
		 
	} 
	return render(request,'team.html', context)


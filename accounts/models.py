from django.db import models
from django.contrib.auth.models import User
 

# Create your models here.


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name


 

class IqamahAdjustment(models.Model):
    PRAYER_CHOICES = [
        ('fajr', 'Fajr'),
        ('dhuhr', 'Dhuhr'),
        ('asr', 'Asr'),
        ('maghrib', 'Maghrib'),
        ('isha', 'Isha'),
        # Add or remove as necessary
    ]

    date = models.DateField()
    prayer_name = models.CharField(max_length=50, choices=PRAYER_CHOICES)
    iqamah_time = models.TimeField()

    class Meta:
        unique_together = ('date', 'prayer_name')

    def __str__(self):
        return f"{self.date} - {self.get_prayer_name_display()}: {self.iqamah_time}"

class RamadanDate(models.Model):
    year = models.IntegerField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField()



# models.py
from django.db import models

class JummahPrayer(models.Model):
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.date} - {self.location} at {self.time}"




class Announcement(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.title
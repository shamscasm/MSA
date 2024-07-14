from django.contrib import admin
from .models import Contact ,IqamahAdjustment, RamadanDate, JummahPrayer, Announcement

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message')  # Customize to display these fields in the admin list view

admin.site.register(Contact, ContactAdmin)


admin.site.register(IqamahAdjustment)
admin.site.register(RamadanDate)



@admin.register(JummahPrayer)
class JummahPrayerAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'location')



 

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title', 'description')
    list_filter = ('date',)

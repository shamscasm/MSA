from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import prayer_times_view ,jummah_prayer_view

urlpatterns = [
    path('',views.index, name="index" ),
     path('prayer',views.prayer_times_view, name="prayer" ),
     path('test',views.test_page, name="test" ),
     path('team',views.team, name="team" ),
     path('jummah-prayer/', jummah_prayer_view, name='jummah_prayer'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
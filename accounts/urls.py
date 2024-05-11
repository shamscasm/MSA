from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import prayer_times_view

urlpatterns = [
    path('',views.index, name="index" ),
     path('prayer',views.prayer_times_view, name="prayer" ),
     path('test',views.test_page, name="test" ),
     path('team',views.team, name="team" ),
  

 
     


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
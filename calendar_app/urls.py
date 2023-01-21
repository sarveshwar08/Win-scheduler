
from django.contrib import admin
from django.urls import path
from .views import home_view, GoogleCalendarInitView,  GoogleCalendarRedirectView, Delete_session_view

urlpatterns = [
    path('', home_view, name = 'home_view'),
    path('rest/v1/calendar/init/',  GoogleCalendarInitView, name = 'user_grant'),
    path('rest/v1/calendar/redirect/',   GoogleCalendarRedirectView, name = 'redirect_view'),
    path('delete_session/', Delete_session_view, name = 'delete_session')
    
]

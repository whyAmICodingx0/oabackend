from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('home/weather', views.homeWeatherView.as_view(), name='homeWeather'),
    path('weather', views.weatherView.as_view(), name='weather'),
]
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'inform'

router = DefaultRouter(trailing_slash=False)
# GET /absent
# POST /absent
router.register('inform', views.InformViewSet, basename='inform')

urlpatterns = [
    path('inform/read', views.ReadInformView.as_view(), name='inform_read'),
] + router.urls
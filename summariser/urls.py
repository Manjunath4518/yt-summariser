# summariser/urls.py
from django.urls import path
from . import views   # import views from the same app

urlpatterns = [
    path('', views.home, name='index'),   # example route
]

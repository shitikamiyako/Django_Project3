from django.urls import path
from . import views

app_name = 'mente'

urlpatterns = [
    path('', views.mente, name='mente'),
]

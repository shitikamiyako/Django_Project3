from django.urls import path
from . import views_form, views_result

app_name = 'question'

urlpatterns = [
    path('form/', views_form.question, name='form'),
    path('result/', views_result.question_result, name='result')
]

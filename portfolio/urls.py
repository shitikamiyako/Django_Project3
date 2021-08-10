from django.urls import path
from . import views_check, views_simulation


app_name = 'portfolio'

urlpatterns = [
    path('check/', views_check.portfolio_check, name='portfolio_check'),
    path('simulation/', views_simulation.simulator, name='simulator'),
]

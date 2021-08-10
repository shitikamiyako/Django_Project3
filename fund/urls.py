from django.urls import path
from . import views_detail, views_search


app_name = 'fund'

urlpatterns = [
    path('search/', views_search.fund_list, name='fund_list'),
    path('detail/<int:fund_id>', views_detail.fund_detail, name='fund_detail'),
    path('register_portfolio/', views_search.register_portfolio,
         name='register_portfolio'),
    path('delete_portfolio/<int:fund_id>', views_search.delete_portfolio,
         name='delete_portfolio'),
]

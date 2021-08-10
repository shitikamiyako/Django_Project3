from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('top/', include('top.urls')),
    path('accounts/', include('allauth.urls')),
    path('question/', include('question.urls')),
    path('mente/', include('mente.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('fund/', include('fund.urls')),
    path('learn/', include('learn.urls')),
    path('explore/', include('explore.urls')),
    path('landing/', include('landing.urls')),
]

# メディアファイル公開用のURL設定
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

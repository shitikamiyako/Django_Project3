from django.contrib import admin

# Register your models here.
from .models import Portfolio

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('id', 'customuser_obj', 'mutual_fund_obj')

admin.site.register(Portfolio,PortfolioAdmin)

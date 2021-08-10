from django.contrib import admin

# Register your models here.
from .models import MutualFund, MutualFundHistory, Category


class MutualFundAdmin(admin.ModelAdmin):
    list_display = ('id', 'fund_name', 'company', 'return_percent', 'risk')


admin.site.register(MutualFund, MutualFundAdmin)
admin.site.register(MutualFundHistory)
admin.site.register(Category)

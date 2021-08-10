from django.shortcuts import render
from django.views import View


class Learn(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'learn/learn.html')


learn = Learn.as_view()

from django.shortcuts import render
from django.views import View


class Explore(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'explore/explore.html')


explore = Explore.as_view()

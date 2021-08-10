from django.shortcuts import render
from django.views import View


class Mente(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'mente/mente.html')


mente = Mente.as_view()

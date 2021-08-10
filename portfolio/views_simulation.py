from django.shortcuts import render
from django.views import View


class Simulator(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'portfolio/simulator.html')


simulator = Simulator.as_view()

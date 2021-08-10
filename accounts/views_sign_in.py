from django.shortcuts import render
from django.contrib.auth.views import LoginView


class LogIn(LoginView):

    def get(self, request, *args, **kwargs):
        return render(request, 'account/login.html')


login = LogIn.as_view()

from django.shortcuts import render
from django.views import View


class Register(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'account/make_account.html')


register = Register.as_view()

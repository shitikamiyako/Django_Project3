from django.shortcuts import redirect, reverse
from django.views import View


# システムにアクセスがあればトップページに飛ばす
class index(View):

    def get(self, request, *args, **kwargs):
        return redirect(reverse('landing:landing'))


index = index.as_view()

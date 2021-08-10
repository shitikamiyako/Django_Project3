from .forms import SearchForm
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from fund.models import MutualFund
from portfolio.models import Portfolio
from accounts.models import CustomUser
from django.shortcuts import redirect, reverse
from django.views import View
from .funcs.fund import build_category_table, search_fund, convert_rate
from django.contrib import messages
from .funcs.portfolio import register_portfolio as reg_portfolio
from .funcs.portfolio import delete_portfolio as del_portfolio

# 1ページの表示件数
PAGINATE_BY = 10


class FundList(LoginRequiredMixin, ListView):
    model = MutualFund
    template_name = 'fund/fund_list.html'
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            category = form_value[0]
            search_query = form_value[1]
            matched_funds = search_fund(search_query, category)
        else:
            # すべてのDB格納されている銘柄を取得する
            matched_funds = search_fund()

        # レートを★に変換
        ret_matched_funds = convert_rate(matched_funds)
        return ret_matched_funds

    def post(self, request, *args, **kwargs):
        # ユーザから検索条件を取得
        form_value = [
            self.request.POST.get('category_list', None),
            self.request.POST.get('query', None),
        ]
        request.session['form_value'] = form_value
        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = ''
        num_matched_funds = ''
        category_list = build_category_table()
        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            category_list = form_value[0]
            search_query = form_value[1]
            num_matched_funds = len(search_fund(search_query, category_list))
        else:
            num_matched_funds = len(search_fund())
        # 合計件数設定
        context['num_matched_funds'] = num_matched_funds

        default_data = {
            'category_list': category_list,
            'query': search_query,
        }
        fund_list_form = SearchForm(initial=default_data)
        fund_list_form.fields['category_list'].choices = build_category_table()
        context['fund_list_form'] = fund_list_form

        return context


fund_list = FundList.as_view()


class Register_portfolio(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        """"受け取ったオブジェクトを比較リストDBに追加"""
        user_id = self.request.user.id
        fund_id = request.POST['fund_id']
        amount = request.POST['amount_form']

        user_obj = CustomUser.objects.get(id=user_id)
        fund_obj = MutualFund.objects.get(id=fund_id)

        if not Portfolio.objects.filter(customuser_obj=user_obj,
                                        mutual_fund_obj=fund_obj):
            reg_portfolio(user_obj, fund_obj, amount)
            messages.info(request, "ポートフォリオに追加しました。",
                          extra_tags='alert-success')
        else:
            messages.info(request, "既に登録されています。",
                          extra_tags='alert-success')

        if request.POST['page'] == "list":
            return redirect(reverse('fund:fund_list'))
        else:
            return redirect(reverse('fund:fund_detail',
                                    kwargs={'fund_id': fund_id}))


register_portfolio = Register_portfolio.as_view()


class Delete_portfolio(LoginRequiredMixin, View):
    def get(self, request, fund_id, *args, **kwargs):
        user_id = self.request.user.id
        user_obj = CustomUser.objects.get(id=user_id)
        fund_obj = MutualFund.objects.get(id=fund_id)
        del_portfolio(user_obj, fund_obj)
        return redirect(reverse('portfolio:portfolio_check'))


delete_portfolio = Delete_portfolio.as_view()

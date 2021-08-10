from django.shortcuts import render
from django.views import View
from top.funcs.top import get_info, get_history_rank, update_question_result
from portfolio.funcs.portfolio import find_fund_popular_portfolio
from portfolio.funcs.portfolio import PortfolioFunc
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime

OFTEN_SEEN_FUND_RANK_NUM = 5
POPULAR_FUND_RANK_NUM = 5


class Top(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # 運営からの連絡を取得
        info_list = get_info()

        # よく見られている銘柄ランキングを取得
        often_seen_fund_list = get_history_rank(OFTEN_SEEN_FUND_RANK_NUM)

        # 人気の銘柄ランキングを取得
        popular_fund_list = find_fund_popular_portfolio(POPULAR_FUND_RANK_NUM)

        # 未ログインユーザーがアンケートに回答した場合、ログイン後に回答結果をそのユーザーに紐つける
        if 'unsaved_answer' in self.request.session and self.request.session['unsaved_answer'] == True:
            user_info = self.request.user.id
            question_result_info = self.request.session["primary_key"]
            update_question_result(user_info, question_result_info)
            self.request.session['unsaved_answer'] = False

        context = {
            'infomations': info_list,
            'often_seen_funds': often_seen_fund_list,
            'popular_funds': popular_fund_list,
        }
        return render(request, 'top/top_page.html', context=context)


top = Top.as_view()

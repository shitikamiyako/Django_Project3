from django.shortcuts import render
import pandas as pd
import numpy as np
from django.views import View
from fund.models import MutualFund

from django.contrib.auth import get_user_model
from portfolio.funcs.portfolio import find_fund_near_risk, find_fund_near_return, find_fund_popular_user
from fund.funcs.fund import add_fund_history, scrape_fund_detail, extract_fund_name, fetch_fund_urls
from django.contrib.auth.mixins import LoginRequiredMixin

class FundDetail(LoginRequiredMixin, View):

    """
    ・似たリスクを持つ銘柄及び似たリターンを持つ銘柄の情報を取得する。
    ・引数の銘柄を持っている人がほかに持っている銘柄を抽出
    """

    def get(self, request, fund_id, *args, **kwargs):

        # 閲覧履歴に追加
        current_user = request.user
        mutual_fund = MutualFund.objects.get(id=fund_id)
        add_fund_history(mutual_fund, current_user.id)

        # スクレイピングでデータを取得
        scraped_fund_details = scrape_fund_detail(mutual_fund.url)

        # 取得件数設定
        num_fund_obj = 5

        # 似たリスク及びリターンを持つ銘柄のリストを変数に代入
        brand_risk_near_list = find_fund_near_risk(fund_id, num_fund_obj)
        brand_return_near_list = find_fund_near_return(fund_id, num_fund_obj)

        # DataFrameのコンテンツの情報
        brand_risk_near_contents = brand_risk_near_list.values.tolist()
        brand_return_near_contents = brand_return_near_list.values.tolist()
        risk_fund_names = extract_fund_name(brand_risk_near_contents)
        return_fund_names = extract_fund_name(brand_return_near_contents)
        risk_urls = fetch_fund_urls(risk_fund_names)
        return_urls = fetch_fund_urls(return_fund_names)
        # 引数の銘柄を持っているユーザーが他に持っている銘柄を登録数上位から取得
        fund_popular_list = find_fund_popular_user(fund_id, num_fund_obj)

        context = {
            'risk_contents': brand_risk_near_contents,
            'risk_urls': risk_urls,
            'return_contents': brand_return_near_contents,
            'return_urls': return_urls,
            'popular_user_funds': fund_popular_list,
            'fund_id': fund_id,
            'fund_obj': mutual_fund,
            **scraped_fund_details,
        }
        return render(request, 'fund/fund_detail.html', context=context)


fund_detail = FundDetail.as_view()

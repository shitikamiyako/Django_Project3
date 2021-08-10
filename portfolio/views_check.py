from django.shortcuts import render
from django.views import View
from portfolio.funcs.portfolio import PortfolioFunc
from django.contrib.auth.mixins import LoginRequiredMixin


class PortfolioCheck(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        analyzed_list, summary = PortfolioFunc.analyze_each_fund(user_id)
        my_fund_list = PortfolioFunc.get(user_id)
        total_risk, total_return = PortfolioFunc.calc_portofolio_risk_return(
            analyzed_list
        )
        context = {
            "analyzed_lists": analyzed_list,
            "summary": summary,
            "my_funds": my_fund_list,
            "total_risk": total_risk,
            "total_return": total_return,
        }
        return render(request, "portfolio/portfolio_check.html", context=context)


portfolio_check = PortfolioCheck.as_view()

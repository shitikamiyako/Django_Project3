from portfolio.models import Portfolio


def register_portfolio(user_obj, fund_obj, amount):
    """奨学金比較リストのデータベースに奨学金を追加する"""
    portfolio = Portfolio(customuser_obj=user_obj,
                          mutual_fund_obj=fund_obj, amount=amount)
    portfolio.save()


def delete_portfolio(user_obj, fund_obj):
    """奨学金比較リストのデータベースから奨学金を削除する"""
    portfolio = Portfolio.objects.get(customuser_obj=user_obj,
                                      mutual_fund_obj=fund_obj)
    portfolio.delete()

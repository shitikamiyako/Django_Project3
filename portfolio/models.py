from django.db import models
import sys
import pathlib
# base.pyのあるディレクトリの絶対パスを取得
# current_dir = pathlib.Path(__file__).resolve().parent
# # モジュールのあるパスを追加
# sys.path.append( str(current_dir) + '/../' )

# print(sys.path)
from accounts.models import CustomUser
from fund.models import MutualFund


class Portfolio(models.Model):
    customuser_obj = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    mutual_fund_obj = models.ForeignKey(MutualFund, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True, blank=True)
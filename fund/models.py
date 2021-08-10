from django.db import models
from datetime import datetime
from accounts.models import CustomUser


class Category(models.Model):
    class Meta:
        db_table = 'Category'
        verbose_name_plural = '投資信託:カテゴリ'

    category = models.CharField('カテゴリ', max_length=255, default='')

    def __str__(self):
        return self.category


class MutualFund(models.Model):
    class Meta:
        db_table = 'MutualFund'
        verbose_name_plural = '投資信託情報'

    DELETE_FLAG = ((0, '未削除'), (1, '削除'))

    # id = AutoField(primary_key=True)  # 自動的に追加されるので定義不要
    url = models.CharField('ファンドURL', max_length=255, null=True, blank=True)
    fund_name = models.CharField(
        'ファンド名', max_length=255, null=True, blank=True)
    company = models.CharField('会社名', max_length=255, null=True, blank=True)
    category_obj = models.ForeignKey(
        Category,
        verbose_name='カテゴリー',
        on_delete=models.CASCADE
    )
    rate = models.IntegerField('総合レーティング', null=True, blank=True)
    return_percent = models.FloatField('リターン率(3年)', null=True, blank=True)
    risk = models.FloatField('リスク値(3年)', null=True, blank=True)
    fee = models.FloatField('信託報酬等（税込）', null=True, blank=True)
    net_assets = models.IntegerField('純資産額（百万円）', null=True, blank=True)
    delete_flag = models.IntegerField('削除フラグ', choices=DELETE_FLAG, default=0)

    def __str__(self):
        return self.fund_name


class MutualFundHistory(models.Model):
    class Meta:
        db_table = 'MutualFundHistory'
        verbose_name_plural = '投資信託閲覧履歴'

    customuser_obj = models.ForeignKey(
        CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    mutual_fund_obj = models.ForeignKey(
        MutualFund, verbose_name='投資信託', on_delete=models.CASCADE)
    datetime = models.DateTimeField('日付時刻', default=datetime.now)

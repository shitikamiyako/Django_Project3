from mente.models import Info
from fund.models import MutualFund, MutualFundHistory
from accounts.models import CustomUser
from question.models import QuestionResult
from django.db.models import Count


def get_info():
    """
    表示フラグ:0の運営からの連絡を取得する

    Returns
    -------
    info_list : QuerySet
        表示フラグが0の連絡リスト (0…表示、1…非表示)
    """
    info_list = Info.objects.filter(show_flag=0)
    return info_list


def get_history_rank(num_items):
    """
    投資信託履歴テーブルから銘柄毎の個数を取得し、idに紐づく投資信託情報を降順で抽出する

    Parameters
    ----------
    num_items : int
        取得件数

    Returns
    -------
    fund_list : list
        銘柄リスト
    """
    # 閲覧履歴からランキングを抽出する
    # 削除フラグが立っている銘柄を除外
    query = MutualFundHistory.objects.filter(mutual_fund_obj__delete_flag=0)
    # 各銘柄の閲覧回数を抽出
    query = query.values('mutual_fund_obj')
    query = query.annotate(history_fund_count=Count(
        expression='mutual_fund_obj'))
    # ランキングを降順でnum_items個取得
    ranking = query.order_by('-history_fund_count')[0:num_items]

    # ランキングに応じたMutalFundオブジェクトのリストを取得
    fund_list = []
    for rank_record in ranking:
        fund = MutualFund.objects.get(pk=rank_record['mutual_fund_obj'])
        fund_list.append(fund)

    return fund_list


def update_question_result(user_info, question_result_info):
    question_result_obj = QuestionResult.objects.get(
        id=question_result_info)
    user_obj = CustomUser.objects.get(id=user_info)
    question_result_obj.customuser_obj = user_obj
    data_to_update = question_result_obj.save()

    return data_to_update

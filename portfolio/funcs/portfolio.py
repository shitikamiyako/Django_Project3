import math
from typing import List

import numpy as np
import pandas as pd
from django.db.models import Count

from fund.models import MutualFund
from portfolio.models import Portfolio


class PortfolioFunc:
    def __init__(self):
        super().__init__()

    def get(user_id: int) -> list:
        """
        user_idに紐づく銘柄オブジェクトを返す。
        """
        portfolios = Portfolio.objects.filter(customuser_obj=user_id)
        funds = []
        for portfolio in portfolios:
            fund = MutualFund.objects.filter(fund_name=portfolio.mutual_fund_obj)
            funds.append(fund)
        return funds

    def analyze_each_fund(user_id: int):
        """user_idに紐づく銘柄のリスク・リターン・レーティング・保有金額・カテゴリ数を返す
        """
        portfolios = Portfolio.objects.filter(customuser_obj=user_id)
        analyzed_list = []
        category_list = []
        summary = {"total": 0, "rate": 0, "category_num": 0}
        for portfolio in portfolios:
            fund = MutualFund.objects.filter(fund_name=portfolio.mutual_fund_obj)[0]
            amount = portfolio.amount / 10000
            return_value = amount * fund.return_percent
            risk_value = amount * fund.risk

            analyzed_list.append(
                {
                    "fund_id": fund.id,
                    "category": fund.category_obj,
                    "fund_name": fund.fund_name,
                    "return_value": return_value,
                    "risk": risk_value,
                    "amount": amount,
                }
            )
            summary["total"] = summary["total"] + return_value - risk_value
            summary["rate"] += fund.rate
            category_list.append(fund.category_obj)

        # ポートフォリオがない場合のバグ対応
        if len(portfolios) != 0:
            summary["rate"] = summary["rate"] / len(portfolios)
        else:
            summary["rate"] = 0

        category_list = set(category_list)
        summary["category_num"] = len(category_list)

        return analyzed_list, summary

    def calc_portofolio_risk_return(analyzed_list: List[dict]) -> float:
        """ポートフォリオのリスク、リターンを計算する

        Args:
            analyzed_list (List[dict]): 個々の銘柄の分析結果

        Returns:
            float: ポートフォリオのリスクとリターン
        """
        total_amount = 0
        # 自分の保有金額の合計を算出
        for value in analyzed_list:
            total_amount += value["amount"]

        # 　銘柄のカテゴリから相関係数を取得する準備
        category_df = pd.read_csv("./portfolio/funcs/category.csv")
        coefficient_df = pd.read_csv("./portfolio/funcs/coefficient.csv", index_col=1)
        coefficient_df = coefficient_df.drop("id", axis=1)
        coefficient_df = coefficient_df.fillna(999)
        sum_risk = 0
        sum_return = 0
        sum_coef = 0

        # 2つの銘柄から相関係数を用いてリスクとリターンを計算
        # 計算式の参考　http://teiiyone.com/blog/2009/05/post_201.html
        for fund_1 in analyzed_list:
            each_fund_risk = (fund_1["amount"] / total_amount) ** 2 * fund_1[
                "risk"
            ] ** 2
            each_fund_return = (fund_1["amount"] / total_amount) * fund_1[
                "return_value"
            ]
            sum_risk += each_fund_risk
            sum_return += each_fund_return
            for fund_2 in analyzed_list:
                fund_1_category = category_df[
                    category_df["category"] == str(fund_1["category"])
                ]
                fund_2_category = category_df[
                    category_df["category"] == str(fund_2["category"])
                ]
                parent_1_category = fund_1_category["親category"]
                parent_2_category = fund_2_category["親category"]
                if parent_1_category.values[0] == parent_2_category.values[0]:
                    coefficient = 1
                else:
                    coefficient = coefficient_df.at[
                        parent_1_category.values[0], parent_2_category.values[0]
                    ]
                # TODO Nan値を指定する。現状はfillnaでNanに999を入れている
                if coefficient == 999:
                    coefficient = coefficient_df.at[
                        parent_2_category.values[0], parent_1_category.values[0]
                    ]

                two_funds_coef = (
                    2
                    * fund_1["amount"]
                    / total_amount
                    * fund_1["risk"]
                    * fund_2["amount"]
                    / total_amount
                    * fund_2["risk"]
                    * float(coefficient)
                )
                sum_coef += two_funds_coef
        # A,Bの銘柄の共分散とB,Aの銘柄の共分散を足しているので、2で割る。
        sum_coef = sum_coef / 2

        total_risk = math.sqrt(sum_risk + sum_coef)
        total_return = sum_return
        return total_risk, total_return


# 福田ここまで


# risk_colとreturn_colの仮定義
risk_col = 0
return_col = 0

# リスク差を求める関数


def risk_differ(x):
    return risk_col - x.loc["risk"]


# リターン差を求める関数


def return_differ(x):
    return return_col - x.loc["return_percent"]


def find_fund_near_risk(fund_id, num_fund_obj):
    """
    取得してきたレコードをDataFrameに変換し、新しくカラムを作ってそこに指定銘柄とのリスク差を絶対値として格納してソートして返す

    Arguments:
        fund_id : str
            銘柄名。
        num_fund_obj : int
            取得件数。

    Returns:
        brand_risk_near : DataFrame
    """
    # レコードを辞書型で取得。
    brand_info = MutualFund.objects.values("id", "company", "fund_name", "risk")

    # DataFrameに変換
    brand_info_df = pd.DataFrame(brand_info)

    # DFから指定銘柄のリスクカラムを抽出
    find_obj = brand_info_df[brand_info_df["id"] == fund_id]
    risk_col = find_obj["risk"]

    # リスク差の計算結果を入れるカラムを作る
    brand_info_df["differ"] = np.nan

    # differカラムにリスク差の値を格納し、値を絶対値化する。
    brand_info_df["differ"] = brand_info_df.apply(risk_differ, axis=1).abs()

    # 引数で指定された銘柄の情報の行を削除
    deleterow = brand_info_df.index[brand_info_df["id"] == fund_id]
    brand_info_df = brand_info_df.drop(deleterow)

    # 少ない順にソートしてdifferカラムとidカラムを削除
    brand_info_df = brand_info_df.sort_values("differ")
    brand_info_df = brand_info_df.drop(columns=["id", "differ"])

    # 件数制限
    brand_risk_near = brand_info_df.head(num_fund_obj)

    return brand_risk_near


def find_fund_near_return(fund_id, num_fund_obj):
    """
    取得してきたレコードをDataFrameに変換し、新しくカラムを作ってそこに指定銘柄とのリターン差を絶対値として格納してソートして返す
    Arguments:
        fund_id : int
            銘柄のid(Mutual_Fundにおけるpk)
        num_fund_obj : int
            取得件数
    Returns:
        brand_return_near : DataFrame
    """
    # レコードを辞書型で取得。
    brand_info = MutualFund.objects.values(
        "id", "company", "fund_name", "return_percent"
    )

    # DataFrameに変換
    brand_info_df = pd.DataFrame(brand_info)

    # DFから指定銘柄のreturn_percentカラムを抽出
    find_obj = brand_info_df[brand_info_df["id"] == fund_id]
    return_col = find_obj["return_percent"]

    # リターン差の計算結果を入れるカラムを作る
    brand_info_df["differ"] = np.nan

    # differカラムにリターン差の値を格納し、値を絶対値化する。
    brand_info_df["differ"] = brand_info_df.apply(return_differ, axis=1).abs()

    # 引数で指定された銘柄の情報の行を削除
    deleterow = brand_info_df.index[brand_info_df["id"] == fund_id]
    brand_info_df = brand_info_df.drop(deleterow)

    # 少ない順にソートしてdifferカラムとidカラムを削除
    brand_info_df = brand_info_df.sort_values("differ")
    brand_info_df = brand_info_df.drop(columns=["id", "differ"])

    # 件数制限
    brand_return_near = brand_info_df.head(num_fund_obj)

    return brand_return_near



# 高橋 ここまで
def find_fund_popular_user(fund_id, num_fund_obj):
    """
    引数の銘柄を持っている人がほかに持っている銘柄を抽出

    Arguments:
        fund_id : int
        num_fund_obj : int

    Returns:
        fund_list : list
    """
    # 引数の銘柄からPortfolioモデルを検索し、引数の銘柄を持っているユーザーを抽出
    query = Portfolio.objects.filter(mutual_fund_obj__id__exact=fund_id)

    # ユーザーID(customuser_obj)だけリストで抽出
    query = query.values_list("customuser_obj", flat=True)

    # 抽出したIDが含まれるレコードをすべて抽出する
    customuser_obj_id_list = Portfolio.objects.filter(customuser_obj__in=query)

    # 引数の銘柄を弾く
    customuser_obj_id_list = Portfolio.objects.exclude(
        mutual_fund_obj__id__exact=fund_id
    )

    # 今度はfund_id(mutual_fund_obj)抽出
    mutual_fund_obj_list = customuser_obj_id_list.values("mutual_fund_obj")

    # 出現回数を集計して引数の取得件数の数だけ上位から取得
    fund_count = mutual_fund_obj_list.annotate(
        portfolio_fund_count=Count(expression="mutual_fund_obj")
    )

    fund_count_list = fund_count.order_by("-portfolio_fund_count")[0:num_fund_obj]

    # forを使い、fund_count_listの数だけ対応するMutualFundオブジェクトを取得し、空のリストに格納して返す
    fund_list = []
    for fund_record in fund_count_list:
        fund = MutualFund.objects.get(pk=fund_record["mutual_fund_obj"])
        fund_list.append(fund)

    return fund_list


# Portfolio クラスを使用


def find_fund_popular_portfolio(num_items):
    """
    Portfolioテーブルに登録されている銘柄毎の個数を取得し、
    idに紐づく投資信託情報を降順で抽出する

    Parameters
    ----------
    num_items : int
        取得件数(最大)

    Returns
    -------
    fund_list : list
        銘柄リスト
    """
    # ポートフォリオテーブルからランキングを抽出する
    # 削除フラグが立っている銘柄を除外
    query = Portfolio.objects.filter(mutual_fund_obj__delete_flag=0)
    # 各銘柄の閲覧回数を抽出
    query = query.values("mutual_fund_obj")
    query = query.annotate(portfolio_fund_count=Count(expression="mutual_fund_obj"))
    # ランキングを降順でnum_items個取得
    ranking = query.order_by("-portfolio_fund_count")[0:num_items]

    # ランキングに応じたMutalFundオブジェクトのリストを取得
    fund_list = []
    for rank_record in ranking:
        fund = MutualFund.objects.get(pk=rank_record["mutual_fund_obj"])
        fund_list.append(fund)

    return fund_list


# 高橋 ここまで

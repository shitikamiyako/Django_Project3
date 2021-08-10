from fund.models import Category, MutualFund, MutualFundHistory
from accounts.models import CustomUser
import pandas
import requests
from bs4 import BeautifulSoup


ALL_CATEGORY = 'すべて'
URL_IFRAME_TEMPLATE = 'http://www.morningstar.co.jp/webaspj/html5/chart.html?fundCode={}'
KEYWORD_QUERY = 'fnc='
COLUMN_RETURN = 'トータルリターン'
COLUMN_RISK = '標準偏差'
COLUMN_YEAR = '年'


def build_category_table():

    categories = Category.objects.all()
    category_list = []
    # プルダウンをChoiceFieldにしたためkey,valueを保持するよう修正
    category_list.append((ALL_CATEGORY, ALL_CATEGORY))
    for category in categories:
        category_list.append((category.category, category.category))

    return category_list


def search_fund(search_word='', fund_category=ALL_CATEGORY):
    """
    検索ワードと銘柄名が部分一致かつ、カテゴリが一致する銘柄を抽出する

    Parameters
    ----------
    search_word : str
        ユーザーが検索したファンド名

    fund_category: str
        ユーザーが検索したファンドのカテゴリー

    Returns
    -------
    matched_funds
        検索条件に合う銘柄のリスト
    """

    # 選ばれたカテゴリーが「すべて」、小カテゴリ、親カテゴリで処理を場合分けする
    # 『すべて』が選ばれた時
    if fund_category == ALL_CATEGORY:
        matched_funds = MutualFund.objects.filter(
            fund_name__contains=search_word)
        return matched_funds

    if Category.objects.filter(category=fund_category).exists():
        category_obj = Category.objects.get(category=fund_category)
        matched_funds = MutualFund.objects.filter(
            fund_name__contains=search_word,
            category_obj=category_obj
        )
        return matched_funds


def add_fund_history(mutual_fund, user_id):
    """
    銘柄を履歴テーブルに登録する
    Parameters
    ----------
    mutual_fund: Queryset
        銘柄のクエリセット
    user_id: int
        ユーザーのid
    -------

    """
    customer_obj = CustomUser.objects.get(id=user_id)
    mutual_fund_history_obj = MutualFundHistory(customuser_obj=customer_obj,
                                                mutual_fund_obj=mutual_fund)
    mutual_fund_history_obj.save()


def parse_fund_unique_code(url_fund_detail):
    """
    銘柄の詳細ページのURLからユニークIDをパースする。
    e.g.){fund_path}?fnc={unique_id}
    Parameters
    ----------
    url_fund_detail: str
        銘柄の詳細ページのURL
    Returns
    ---------
    unique_id: str
        銘柄のURLに使用されているユニークID
    """
    start_index_keyword = url_fund_detail.find(KEYWORD_QUERY)
    if start_index_keyword > 0:
        start_index_unique_id = start_index_keyword + len(KEYWORD_QUERY)
        unique_id = url_fund_detail[start_index_unique_id:]
        return unique_id


def create_iframe_src(url_fund_detail):
    """
    iframeタグのsrcに使われるURLを銘柄のユニークIDから作成する
    Parameters
    ----------
    url_fund_detail: str
        銘柄の詳細ページのURL
    Returns
    ---------
    url_chart_iframe: str
        iframeタグのsrcに使われるURL
    """
    fund_unique_code = parse_fund_unique_code(url_fund_detail)
    url_chart_iframe = URL_IFRAME_TEMPLATE.format(fund_unique_code)
    return url_chart_iframe


def scrape_fund_detail(url_fund_detail):
    """
    銘柄の詳細ページのURLからユニークIDをパースする。
    e.g.){fund_path}?fnc={unique_id}
    Parameters
    ----------
    url_fund_detail: str
        銘柄の詳細ページのURL
    Returns
    ---------
    scraped_fund_details: dict
        テンプレートで使われるデータの集合体
    """
    # # URLからHTMLを取得
    response = requests.get(url_fund_detail)
    response.encoding = response.apparent_encoding
    bs = BeautifulSoup(response.text, 'html.parser')
    # divタグの子要素であるpタグを取得
    elements = bs.select('.inftxt > p')
    # 銘柄の特徴(text)を取得
    fund_feature_text = elements[0].getText()
    # iframeのsrcを取得
    url_chart_iframe = create_iframe_src(url_fund_detail)
    # Dataframeからrisk値とreturn値を抽出しリスト型で纏める
    df_list = pandas.read_html(url_fund_detail)
    df_indicator = df_list[1]
    df_returns = df_indicator.loc[df_indicator[COLUMN_YEAR] == COLUMN_RETURN]
    df_risks = df_indicator.loc[df_indicator[COLUMN_YEAR] == COLUMN_RISK]
    returns_list = list(df_returns.values[0][1:])
    risks_list = list(df_risks.values[0][1:])
    # テンプレートで必要なデータを辞書に代入
    scraped_fund_details = {
        'returns': returns_list,
        'risks': risks_list,
        'fund_feature_text': fund_feature_text,
        'fund_chart_src': url_chart_iframe,
    }

    return scraped_fund_details


def extract_fund_name(fund_2D_list):
    fund_name = []
    for fund_list in fund_2D_list:
        for i, fund_info in enumerate(fund_list):
            if i == 1:
                fund_name.append(fund_info)
    return fund_name


def fetch_fund_urls(fund_names):
    fund_urls = []
    for fund_name in fund_names:
        fund_obj = MutualFund.objects.get(fund_name=fund_name)
        fund_urls.append(fund_obj.id)
    return fund_urls


def convert_rate(matched_funds: list):
    """
    銘柄一覧のレートを★に変換する
    ----------
    mutual_fund: Queryset
        銘柄のクエリセット
    Returns
    ---------
    mutual_fund: Queryset
        レートが★に変換された銘柄のクエリセット
    """
    for fund in matched_funds:
        rate_str = "★" * int(fund.rate)
        fund.rate = rate_str
    return matched_funds

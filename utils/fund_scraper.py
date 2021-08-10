from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import click
import time


TARGET_URL = "http://www.morningstar.co.jp/FundData/DetailSearchResult.do?mode=1"

ID_FUND_URL = 0
ID_FUND_NAME = 1
ID_COMPANY = 2
ID_CATEGORY = 3
ID_RATE = 4
ID_RETURN_PERCENT = 5
ID_RISK = 6
ID_FEE = 7
ID_NET_ASSETS = 8


@click.command()
@click.option("-d", "--driver-path", required=True, type=click.Path(exists=True), help="Set your web driver.")
@click.option("-o", "--output-dir", default="./", type=click.Path(exists=True), help="Output directory for csv files.")
@click.option("-m", "--max-pages", type=int, default=-1, help="Limit of pages scraped.")
@click.option("-h", "--headless-mode", default=False, confirmation_prompt=True, help="Run on headless mode.", is_flag=True)
@click.option("-s", "--sleep", type=float, default=5.0, confirmation_prompt=True, help="Sleep seconds for scraping.")
@click.option("--dry-run", default=False, confirmation_prompt=True, help="make it dry-run mode.", is_flag=True)
def scrape(driver_path, output_dir, max_pages, sleep, headless_mode, dry_run):
    """Scrape mutual fund data from Morning Star"""
    if dry_run:
        print(f'WebDriver: {driver_path}')
        print(f'Output directory: {output_dir}')
        print(f'Pages: {max_pages}')
        print(f'Sleep: {sleep} seconds')
        print(f'Headless mode: {headless_mode}')
        return None

    # driver_path = "/usr/local/bin/chromedriver"
    category_csv_path = os.path.join(output_dir, "Category.csv")
    fund_csv_path = os.path.join(output_dir, "MutualFund.csv")
    if max_pages == -1:
        max_pages = None

    # ファンド情報をスクレイピングする
    scraping_data = scrape_fund_data(driver_path, max_pages, sleep, headless_mode)

    # スクレイピングしたデータを解析する
    valid_data = analyze_scraping_data(scraping_data)

    # カテゴリマスタを生成する
    category_master = create_category_master(valid_data)

    # 銘柄マスタを生成する
    fund_master = create_fund_master(category_master, valid_data)

    # csvファイル出力
    save_csv(category_master, category_csv_path)
    save_csv(fund_master, fund_csv_path)


def save_csv(df, file_path):
    """データフレームをCSVファイルとして出力する

    Parameters
    ----------
    df : pandas.DataFrame
        出力したいDataFrame
    file_path : str
        出力するファイル名
    """
    df.to_csv(file_path, index=False, sep=',', encoding='utf-8')


def scrape_result_table(driver, fund_list):
    """検索結果(1ページぶん)のテーブルをスクレイピングする

    Parameters
    ----------
    driver : WebDriver
        ウェブドライバー

    fund_list : list
        結果を格納するリスト(関数内でappend)

    Returns
    -------
    list
        結果を格納したリスト
    """
    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    table_row = soup.find_all('tr')

    for row in table_row:
        tmp = []
        for td in row.find_all('td'):
            if td.a:
                tmp.append(td.a.get('href'))
                tmp.append(td.text)
            else:
                tmp.append(td.text)

        # スクレイピングした項目が10個でなければ不正としてスキップ
        if len(tmp) != 10:
            pass
        else:
            fund_list.append(tmp)

    return fund_list


def scrape_fund_data(chrome_driver_path, max_pages, sleep_sec, headless_flag):
    """ファンド情報をスクレイピングする

    Parameters
    ----------
    chrome_driver_path : str
        chromedriverのパス

    max_pages : int
        スクレイピングする最大ページ数

    sleep_sec : float
        1ページスクレイピングしたあとの待機間(秒)

    headless_flag : bool
        ヘッドレスモードの可否

    Returns
    -------
    list:
        スクレイピングしたデータのリスト
    """

    # ブラウザのオプションを格納する変数を設定
    options = Options()

    # Headlessモードを有効にする
    options.set_headless(headless_flag)
    # chrome.exeの場所指定(必要？)
    # options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"

    # ブラウザを起動する
    driver = webdriver.Chrome(chrome_options=options,
                              executable_path=chrome_driver_path)

    driver.maximize_window()

    # スタートページ
    driver.get(TARGET_URL)

    # HTMLを文字コードをUTF-8に変換してから取得。
    html = driver.page_source.encode('utf-8')

    # BeautifulSoupでパース
    soup = BeautifulSoup(html, "html.parser")

    # 全件数の取得
    chunk_funds_count = soup.select_one(
        '#sresult1  div.mb15.mt20  h3  span.lltxt.fcred  span')
    print(f'Funds count: {chunk_funds_count.get_text()}')
    funds_count = int(chunk_funds_count.get_text())

    # ページ数を取得　
    # 1ページ当たりの件数:50件で変更がないものとして取得する
    # # #sresult1 > form > div:nth-child(3) > p.move　から、数字を拾ってくる?
    totalpages = funds_count // 50 if funds_count % 50 == 0 else funds_count // 50 + 1
    print(f'Total pages: {totalpages}')

    # 最初のページをスクレイピングする
    fund_list = []
    fund_list = scrape_result_table(driver, fund_list)

    # 残りのページをスクレイピングする
    if max_pages:
        limit = min(totalpages, max_pages)
    else:
        limit = totalpages

    for i in range(limit - 1):
        time.sleep(sleep_sec)
        nextpage = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#sresult1 > form > div:nth-child(11) > p.move > span.rgt > a")))
        nextpage.click()

        fund_list = scrape_result_table(driver, fund_list)

    driver.quit()

    return fund_list


def analyze_scraping_data(fund_list):
    """スクレイピングしたデータを解析する

    Parameters
    ----------
    fund_list : list
        スクレイピングしたデータのリスト

    Returns
    -------
    valid_list : list
        解析、検証を終えた有効なデータリスト
    """
    valid_list = []

    # ファンド個別ページリンク  url ( char )
    # ファンド名                fund_name ( char )
    # 会社名                    company( char )
    # カテゴリー                child_category_obj ( char )
    # 総合レーティング          rate( int )
    # リターン（3年）           return_percent ( int )
    # 標準偏差（3年）           risk ( float )
    # 信託報酬等（税込）        fee ( float )
    # 純資産額（百万円）        net_assets ( int )

    url_base = 'http://www.morningstar.co.jp/FundData/'

    for i in range(len(fund_list)):
        sc_url = url_base + fund_list[i][ID_FUND_URL]
        if not type(sc_url) is str and len(sc_url) <= 255:
            print(f"error at {ID_FUND_URL} (ID_FUND_URL):" + str(i))
            continue

        sc_fund_name = fund_list[i][ID_FUND_NAME]
        if not type(sc_fund_name) is str and len(sc_fund_name) <= 255:
            print(f"error at {ID_FUND_NAME} (ID_FUND_NAME):" + str(i))
            continue

        sc_company = fund_list[i][ID_COMPANY]
        if not type(sc_company) is str and len(sc_company) <= 255:
            print(f"error at {ID_COMPANY} (ID_COMPANY):" + str(i))
            continue

        sc_category = fund_list[i][ID_CATEGORY]
        if not type(sc_category) is str and len(sc_category) <= 255:
            print(f"error at {ID_CATEGORY} (ID_CATEGORY):" + str(i))
            continue

        str_rate = fund_list[i][ID_RATE]
        if str_rate == '--':
            print(f"invalid data at {ID_RATE} (ID_RATE):" + str(i))
            continue

        sc_rate = str_rate.count("★")
        if not type(sc_rate) is int and sc_rate <= 5:
            print(f"error at {ID_RATE} (ID_RATE):" + str(i))
            continue

        str_return_percent = fund_list[i][ID_RETURN_PERCENT]
        if str_return_percent == '--':
            print(f"invalid data at {ID_RETURN_PERCENT} (ID_RETURN_PERCENT):" + str(i))
            continue
            
        sc_return_percent = float(str_return_percent.replace('%', ''))
        if not type(sc_return_percent) is float:
            print(f"error at {ID_RETURN_PERCENT} (ID_RETURN_PERCENT):" + str(i))
            print(type(sc_return_percent))
            continue

        str_risk = fund_list[i][ID_RISK]
        if str_risk == '--':
            print(f"invalid data at {ID_RISK} (ID_RISK):" + str(i))
            continue
        sc_risk = float(str_risk)
        if not type(sc_risk) is float:
            print(f"error at {ID_RISK} (ID_RISK):" + str(i))
            print(type(sc_risk))
            continue

        str_fee = fund_list[i][ID_FEE]
        if str_fee == '--':
            print(f"invalid data at {ID_FEE} (ID_FEE):" + str(i))
            continue
        sc_fee = float(str_fee.replace('%', ''))
        if not type(sc_fee) is float:
            print(f"error at {ID_FEE} (ID_FEE):" + str(i))
            print(type(sc_fee))
            continue

        str_net_assets = fund_list[i][ID_NET_ASSETS]
        if str_net_assets == '--':
            print(f"invalid data at {ID_NET_ASSETS} (ID_NET_ASSETS):" + str(i))
            continue
        sc_net_assets = int(str_net_assets.replace(',', ''))
        if not type(sc_net_assets) is int:
            print(f"error at {ID_NET_ASSETS} (ID_NET_ASSETS):" + str(i))
            print(type(sc_net_assets))
            continue

        valid_list.append([
            sc_url, sc_fund_name, sc_company, sc_category,
            sc_rate, sc_return_percent, sc_risk, sc_fee, sc_net_assets
        ])

    return valid_list


def create_category_list(fund_list):
    """スクレイピングデータをもとにカテゴリリストを作成する

    Parameters
    ----------
    fund_list : list
        スクレイピングしたデータのリスト

    Returns
    -------
    list
        カテゴリーリスト
    """
    category_list = []

    # カテゴリを抽出
    for fund in fund_list:
        category = fund[ID_CATEGORY]

        # 新しいカテゴリを発見したらリストに追加
        if category not in category_list:
            category_list.append(category)

    return category_list


def create_category_master(fund_list):
    """スクレイピングしたデータをもとにカテゴリマスタを作成する
    Parameters
    ----------
    fund_list : list
        スクレイピングしたデータのリスト

    Returns
    -------
    DataFrame
        カテゴリマスタ
    """
    # カテゴリリストを作成
    category_list = create_category_list(fund_list)

    # IDリストを作成
    id_list = []
    for i in range(len(category_list)):
        id_list.append(i + 1)

    # カテゴリマスタを生成
    category_master = pd.DataFrame(
        {'id': id_list,
         'category': category_list})

    return category_master


def create_fund_master(category_master, fund_list):
    """スクレイピングしたデータから投資信託銘柄マスタを生成する

    Parameters
    ----------
    category_master : pandas.DataFrame 
        カテゴリマスタデータ
    fund_list : list 
        スクレイピングしたデータ

    Returns
    -------
    pandas.DataFrame
        投資信託銘柄マスタ
    """
    # カテゴリ文字列からIDを取得しリスト化
    def create_category_id_list():
        id_list = []
        for fund in fund_list:
            category = fund[ID_CATEGORY]
            df = category_master.query(f"category=='{category}'")
            category_id = df.iat[0, 0]
            id_list.append(category_id)

        return id_list

    # データフレーム生成用
    def create_data_list(data_id):
        data_list = []
        for fund in fund_list:
            data_list.append(fund[data_id])
        return data_list

    # 各データの列リスト作成
    id_list = []
    for i in range(len(fund_list)):
        id_list.append(i+1)
    url_list = create_data_list(ID_FUND_URL) 
    fund_name_list = create_data_list(ID_FUND_NAME)
    company_list = create_data_list(ID_COMPANY)
    category_id_list = create_category_id_list()
    rate_list = create_data_list(ID_RATE)
    return_percent_list = create_data_list(ID_RETURN_PERCENT)
    risk_list = create_data_list(ID_RISK)
    fee_list = create_data_list(ID_FEE)
    net_assets_list = create_data_list(ID_NET_ASSETS)

    # DataFrameを生成
    fund_master = pd.DataFrame({
        'id': id_list,
        'url': url_list,
        'fund_name': fund_name_list,
        'company': company_list,
        'category_obj_id': category_id_list,
        'rate': rate_list,
        'return_percent': return_percent_list,
        'risk': risk_list,
        'fee': fee_list,
        'net_assets': net_assets_list,
        'delete_flag': 0
    })

    return fund_master


if __name__ == "__main__":
    scrape()

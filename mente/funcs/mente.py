# coding: UTF-8
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from fund.models import MutualFund



def update_fund():
    """
    ファンド情報をスクレイピングしてDB登録する


    """
    fund_list = []

    def scrape_thispage():

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        table_row = soup.find_all('tr')
        global fund_list
        for row in table_row:
            tmp = []
            for td in row.find_all('td'):
                if td.a:
                    tmp.append(td.a.get('href'))
                    tmp.append(td.text)
                else:
                    tmp.append(td.text)

            if len(tmp) != 10:
                pass
            else:
                fund_list.append(tmp)
        return fund_list

    # ブラウザのオプションを格納する変数を設定
    options = Options()

    # Headlessモードを有効にする
    options.set_headless(True)
    # chrome.exeの場所指定(必要？)
    options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"

    # ブラウザを起動する
    driver = webdriver.Chrome(chrome_options=options, executable_path="C:/Python/chromedriver.exe")
    driver.maximize_window()

    # スタートページ
    driver.get("http://www.morningstar.co.jp/FundData/DetailSearchResult.do?mode=1")

    # HTMLを文字コードをUTF-8に変換してから取得。
    html = driver.page_source.encode('utf-8')

    # BeautifulSoupでパース
    soup = BeautifulSoup(html, "html.parser")

    # 全件数の取得
    chunk_funds_count = soup.select_one(
        '#sresult1  div.mb15.mt20  h3  span.lltxt.fcred  span')
    print(chunk_funds_count.get_text())
    funds_count = int(chunk_funds_count.get_text())

    # ページ数を取得　
    # 1ページ当たりの件数:50件で変更がないものとして取得する
    # # #sresult1 > form > div:nth-child(3) > p.move　から、数字を拾ってくる?

    totalpages = funds_count // 50 if funds_count % 50 == 0 else funds_count // 50 + 1
    print(totalpages)

    # 最初のページをスクレイピングする
    scrape_thispage()

    # 残りのページをスクレイピングする　ひとまず4まで
    for i in range(2, 4):  # totalpages):

        nextpage = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#sresult1 > form > div:nth-child(11) > p.move > span.rgt > a")))
        nextpage.click()
        time.sleep(3)

        scrape_thispage()


    print(fund_list)
    print(len(fund_list))

    driver.quit()


    # ファンド個別ページリンク  url ( char )
    # ファンド名                fund_name ( char )
    # 会社名                    company( char )
    # カテゴリー                child_category_obj ( char )
    # 総合レーティング          rate( int )
    # リターン（3年）           return_percent ( int )
    # 標準偏差（3年）           risk ( float )
    # 信託報酬等（税込）        fee ( float )
    # 純資産額（百万円）        net_assets ( int )

    for i in range(1, len(fund_list)):
        sc_url = fund_list[i][0]
        if not type(sc_url) is str and len(sc_url) <= 255:
            print("error at 0:" + str(i))

        sc_fund_name = fund_list[i][1]
        if not type(sc_fund_name) is str and len(sc_fund_name) <= 255:
            print("error at 1:" + str(i))

        sc_company = fund_list[i][2]
        if not type(sc_company) is str and len(sc_company) <= 255:
            print("error at 2:" + str(i))

        sc_child_category_obj = fund_list[i][3]
        if not type(sc_child_category_obj) is str and len(sc_child_category_obj) <= 255:
            print("error at 3:" + str(i))

        sc_rate = fund_list[i][4].count("★")
        if not type(sc_rate) is int and sc_rate <= 5:
            print("error at 4:" + str(i))

        sc_return_percent = float(fund_list[i][5].replace('%', ''))
        if not type(sc_return_percent) is float:
            print("error at 5:" + str(i))
            print(type(sc_return_percent))

        sc_risk = float(fund_list[i][6])
        if not type(sc_risk) is float:
            print("error at 6:" + str(i))
            print(type(sc_risk))

        sc_fee = float(fund_list[i][7].replace('%', ''))
        if not type(sc_fee) is float:
            print("error at 7:" + str(i))
            print(type(sc_fee))

        sc_net_assets = int(fund_list[i][8].replace(',', ''))
        if not type(sc_net_assets) is int:
            print("error at 8:" + str(i))
            print(type(sc_net_assets))

        # delete_flagのあるものを消す
        # MutualFund.objects.filter(delete_flag=1)

        # 更新
        """
        MutualFund.objects.filter(url=sc_url).update(
                                fund_name = sc_fund_name,
                                company = sc_company,
                                child_category_obj = sc_child_category_obj,
                                rate = sc_rate,
                                return_percent = sc_return_percent,
                                risk = sc_risk,
                                fee = sc_fee,
                                net_assets = sc_net_assets,
                                delete_flag = 0)
        """

        # 作成
        """
        MutualFund.objects.create(url=sc_url,
                                fund_name=sc_fund_name,
                                company=sc_company,
                                child_category_obj=sc_child_category_obj,
                                rate=sc_rate,
                                return_percent=sc_return_percent,
                                risk=sc_risk,
                                fee=sc_fee,
                                net_assets=sc_net_assets,
                                delete_flag=0)
"""

        # 削除
from dart_scraper import HtmlFetcher
from dart_scraper import MetaScraper
from dart_scraper import DataScraper
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
import sqlite3
import json
import re
import os
import time
load_dotenv()
API_KEY = os.getenv('DART_API_KEY')

con = sqlite3.connect('/home/db/finance.db')
cur = con.cursor()
companies = cur.execute('select company_code from company').fetchall()
print(companies)

def is_ignore_name(report_name, ignore_names = ['첨부정정', '첨부추가', '사업보고서제출기한연장신고서']):
    for ignore_name in ignore_names:
        if ignore_name in report_name:
            return True
    return False

def insert_finance(report_code, report_type, corp_code, finance_scraper):
    currency = finance_scraper.retreive_currency()
    year, quarter = finance_scraper.retreive_period_standard().split("-")
    period_length = finance_scraper.retreive_period_length()
    equity = finance_scraper.retreive_equity()
    debt = finance_scraper.retreive_debt()
    sales = finance_scraper.retreive_sales()
    operating_profit = finance_scraper.retreive_operating_profit()
    net_profit = finance_scraper.retreive_net_profit()
    cash_equivalents = finance_scraper.retreive_cash()
    cursor = con.cursor()
    cursor.execute(
        f'insert into finance(report_code, report_type, company_code, currency, year, quarter, cumulative_month, equity, debt, sales, operating_profit, net_profit, cash_equivalents) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [report_code, report_type, corp_code, currency, year, quarter, period_length, equity, debt, sales, operating_profit, net_profit, cash_equivalents]
    )
    cursor.close()

now = datetime.now()
yesterday = (now - timedelta(days=1)).strftime('%Y%m%d')
time_sleep_interval = 3
API_URL = lambda corp_code: f'https://opendart.fss.or.kr/api/list.json?crtfc_key={API_KEY}&corp_code={corp_code}&last_reprt_at=Y&pblntf_ty=A&page_no=1&page_count=50&bgn_de={yesterday}&end_de={yesterday}'
def fetch_report_nums(corp_code):
    for i in range(10):
        try:
            response = requests.get(API_URL(corp_code))
        except requests.exceptions.SSLError:
            print(f"---- HTTP 호출 오류로 {time_sleep_interval}초 동안 잠시 쿨다운 ----")
            time.sleep(time_sleep_interval)
            continue
        break
    response.close()
    data = json.loads(response.text)
    recept_nums = []
    if data['status'] == "000":
        fs_list = data["list"]
        for fs in fs_list:
            if is_ignore_name(fs["report_nm"]):
                continue
            recept_nums.append(fs["rcept_no"])
        recept_nums.sort()
    return recept_nums

report_code = None
fetcher = HtmlFetcher([],3)

for company_code, in companies:
    try:
        report_codes = fetch_report_nums(company_code)
        print(report_codes)
        for report_code in report_codes:
            for target in ['연결재무제표', '재무제표']:
                cover_html = fetcher.fetch_cover(report_code)
                meta_scraper = MetaScraper(cover_html)
                elem_id = meta_scraper.elem_id(target)
                dcm_no = meta_scraper.dcm_no()
                finance_html = fetcher.fetch_content(report_code, elem_id, dcm_no)
                table_count = len(finance_html.findAll(lambda tag: tag.name == "table"))
                if table_count < 2:
                    continue
                finance_scraper = DataScraper(finance_html)
                insert_finance(
                    report_code, 
                    'consolidated K-IFRS' if target == '연결재무제표' else 'seperate K-IFRS',
                    company_code,
                    finance_scraper
                )
        report_code = None
        time.sleep(1) 
    except KeyboardInterrupt as e:
        con.close()
        raise e
    except BaseException as e:
        error_log_path = '/home/db/errors'
        with open(error_log_path + f'/{yesterday}.txt', 'a', encoding='utf-8') as file:
            if report_code:
                file.write(f'{company_code}-{report_code}, 보고서 스크래핑 실패: {e}\n')
            else:
                file.write(f'{company_code}, 기업 스크래핑 실패: {e}\n')
            report_code = None
            file.close()
        
con.commit()
con.close()


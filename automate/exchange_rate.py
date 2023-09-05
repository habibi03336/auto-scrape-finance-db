import requests
import sqlite3
import json
import datetime
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')

month_of_31 = [1,3, 5, 7, 8, 10, 12]
month_of_30 = [4,6, 9, 11]
def get_last_day_of_month(year, month):
    if month in month_of_31:
        return 31
    if month in month_of_30:
        return 30
    if month == 2:
        if year % 400 == 0:
            return 29
        if year % 100 == 0:
            return 28
        if year % 4 == 0:
            return 29
        return 28

def exchange_rate_URL(year, month, day): 
    month_str = f'0{month}' if month < 10 else f'{month}'
    day_str = f'0{day}' if day < 10 else f'{day}'
    return f'http://api.currencylayer.com/historical?access_key={API_KEY}&currencies=KRW,CNY,JPY&source=USD&format=1&date={year}-{month_str}-{day_str}'

try:

    con = sqlite3.connect('/home/db/finance.db')
    cur = con.cursor()

    # exected on the first day of a month
    now = datetime.datetime.now()
    year = now.year if now.month > 1 else now.year - 1
    month = now.month - 1 if now.month > 1 else 12
    url = exchange_rate_URL(year, month, get_last_day_of_month(year, month))
    res = requests.get(url)
    res.close()
    data = json.loads(res.text)
    rates = data['quotes']
    cur.execute(
        f'insert into dollar_exchange_rate(year, month, currency, rate) values(?, ?, ?, ?)', [year, month, "KRW", rates["USDKRW"]]
    )
    cur.execute(
        f'insert into dollar_exchange_rate(year, month, currency, rate) values(?, ?, ?, ?)', [year, month, "CNY", rates["USDCNY"]]
    )
    cur.execute(
        f'insert into dollar_exchange_rate(year, month, currency, rate) values(?, ?, ?, ?)', [year, month, "JPY", rates["USDJPY"]]
    )
    con.commit()

except BaseException as e:
    error_log_path = '/home/db/errors'
    with open(error_log_path + '/exchange_rate_error.txt', 'a', encoding='utf-8') as file:
        file.write(f'{year}-{month}, 환율 스크래핑 실패: {e}\n')
        file.close()

finally:
    con.close()


import requests


details_of_fund_file = 'details-of-fund.json'
fund_list_file = 'fund-list.csv'
checkpoint_file = 'checkpoint.txt'

company_file = 'companies.json'

class FetchingError(Exception):
    pass

def get(url):
    for i in range(3):
        try:
            headers = {
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'http://fundf10.eastmoney.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
            }
            resp = requests.get(url=url, headers=headers)
            if resp.status_code != 200:
                print('Fetch %s error. Reason: %s. Retry...' % (fund_code, resp.reason))
                continue
            else:
                return resp
        except Exception as e:
            print('Request %s error. Caused by %s Retry...' % (url, e))
            pass 
    raise FetchingError('Fetch %s fail in 3 times.' % url)


import requests
import time
import json
import csv
import re
import os

from lxml import etree

class FetchingError(Exception):
    pass

def _get(url):
    for i in range(3):
        headers = {
            'Referer': 'http://fundf10.eastmoney.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }
        resp = requests.get(url=url, headers=headers)
        if resp.status_code != 200:
            print('Fetch %s error. Reason: %s. Retry...' % (fund_code, resp.reason))
            continue
        else:
            return resp
    raise FetchingError('Fetch %s fail in 3 times.' % url)

def fetch_net_worth_history(fund_code, fund_name, start_date, end_date=None, verbose=None):
    end = end_date
    if end_date is None:
        end = time.strftime('%Y-%m-%d') # today
    print('Fetching net worth history of %s from %s to %s.' % (fund_code, start_date, end))
    url = "http://api.fund.eastmoney.com/f10/lsjz?callback=callback' \
        '&fundCode=%s&pageIndex=1&pageSize=20&startDate=%s&endDate=%s_=%s"
    timestamp = time.time() 
    timestamp = int(timestamp * 1000)
    url = url % (fund_code, start_date, end, str(timestamp))
    resp = _get(url)
    text = resp.text
    matches = re.search('\{.*\}', text)
    history_str = matches.group(0)
    history_json = json.loads(history_str)
    if history_json['ErrCode'] == 0:
        file_name = '%s-%s-%s-%s.json' % (fund_code, fund_name, start_date, end)
        file_name = os.path.join('data', file_name)
        with open(file_name, 'w') as f:
            f.write(history_str)
        print('Fetching net worth history of %s from %s to %s. Done.' % (fund_code, start_date, end))
    else:
        print('Fetch net worth history of %s fail.' % fund_name)

    return 

def get_all_funds_code_and_name(file=None):
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    url = 'http://fund.eastmoney.com/js/fundcode_search.js'#'http://fund.eastmoney.com/allfund.html'
    resp = _get(url)
    text = resp.text.lstrip('var r = ').rstrip(';')
    json_obj = json.loads(text)
    print('Saving all funds info to %s.' % file)
    if file is None:
        file = os.path.join('data', 'fundlist.csv')
    with open(file, 'w', newline='') as f:
        csv_file = csv.DictWriter(f, ['CODE', 'NAME', 'TYPE'])
        csv_file.writeheader()
        for item in json_obj:
            csv_file.writerow({
                'CODE': item[0],
                'NAME': item[2],
                'TYPE': item[3],
            })

    print('Saving all funds info to %s. Done.' % file)
    return json_obj

def fetch_fund_basic_info(code): 
    print('Fetching basic info of %s.' % code)
    url = 'http://fundf10.eastmoney.com/jbgk_%s.html' % code

    resp = _get(url)
    html = etree.HTML(resp.text)
    sourcerate = html.xpath('//b[@class="sourcerate"]')[0]
    label = sourcerate.xpath('parent::*')[0]
    discount = label.xpath('//b[@class="red"]')
    discount = discount[0].text if discount else 10 # 10: no discount

    tmp = html.xpath('//div[@class="bs_gl"]')[0]
    tmp = tmp.xpath('p')[0]
    raw_metas = tmp.xpath('child::*')
    establish_date = raw_metas[0].xpath('span')[0]
    manager = raw_metas[1].xpath('a')[0]
    fund_type = raw_metas[2].xpath('span')[0]
    company = raw_metas[3].xpath('a')[0]
    amount = raw_metas[4].xpath('span')[0]
    amount = re.search('\d+\.?\d*', amount.text).group(0)

    # locate to the summary 
    tables = html.xpath('//div[@class="detail"]/div[@class="txt_cont"]//div[@class="box"]')
    last_row = tables[0].xpath('table//tr')[-1]
    last_cell = last_row.xpath('td')[-1]
    index = last_cell.text
    print('Fetching basic info of %s. Done.' % code)

    return [establish_date.text, manager.text, fund_type.text, company.text, amount, index]

def fetch_fees(code):
    result = []
    url = 'http://fundf10.eastmoney.com/jjfl_%s.html'  % code
    resp = _get(url)
    html = etree.HTML(resp.text)
    boxs = html.xpath('//div[@class="box"]')

    # 交易状态
    status = boxs[0].xpath('div//td[@class="w135"]')
    buy_status = status[0]
    sell_status = status[1]
    result.extend([{'申购状态': buy_status.text, '赎回状态': sell_status.text}])

    # 申购与赎回金额
    buy_and_sell = boxs[1].xpath('div//td[@class="w135"]')
    least_buying = buy_and_sell[0] # 申购起点
    least_fixed = buy_and_sell[1] # 最小定投
    day_limit = buy_and_sell[2] # 单日限额
    least_amount_at_first = buy_and_sell[3] # 首次购买
    min_append = buy_and_sell[4] # 追加购买
    max_position = buy_and_sell[5] # 最大持仓
    least_sell = buy_and_sell[6] # 最小赎回份额
    least_holding_after_sell = buy_and_sell[7] # 赎回后最小持有份额
    result.append({'申购起点': least_buying.text, '最小定投': least_fixed.text, '单日限额': day_limit.text,
                    '首次购买': least_amount_at_first.text, '追加购买': min_append.text, 
                    '最大持仓': max_position.text,
                    '最小赎回份额': least_sell.text, '部分赎回后最低保留份额': least_holding_after_sell.text})
    # 交易确认日
    comfirm = boxs[2].xpath('div//td')
    buy_comfirm = comfirm[1]
    sell_comfirm = comfirm[3]
    result.append({'买入确认日': buy_comfirm.text, '卖出确认日': sell_comfirm.text})

    # 运作费率
    operating_fees = boxs[3].xpath('div//td[@class="w135"]')
    managing_fee = operating_fees[0]
    hosting_fee = operating_fees[1]
    selling_fee = operating_fees[2]
    result.append({'管理费': managing_fee.text, '托管费': hosting_fee.text, '销售服务费': selling_fee.text})

    def _get_fees(html):
    
        fees_html = html.xpath('div/table/tbody//tr')
        bucket = len(fees_html)
        items = []
        for i in range(bucket):
            item = {}
            fees = fees_html[i].xpath('td')
            discount = fees[2].xpath('strike')
            item['适用金额'] = fees[0].text
            item['适用期限'] = fees[1].text
            if len(discount) > 0:
                item['原费率'] = discount[0].text
            else:
                item['原费率'] = fees[2].text
    
            items.append(item)
        return items
    
    # 认购费率
    result.append({'认购费率（前端）': _get_fees(boxs[4])})
    # 申购费率
    result.append({'申购费率（前端）': _get_fees(boxs[5])})
    # 赎回费率
    result.append({'赎回费率': _get_fees(boxs[6])})

    return result

def fetch_top10stock(code):
    pass

#fetch_fees('501005')
# fetch_fund_basic_info('501008')
# get_all_funds_code_and_name()
#fetch_net_worth_history('001632', '天弘中证食品饮料指数C', '2011-01-01', None)
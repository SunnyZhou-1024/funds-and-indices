import requests
import time
import json
import csv
import re
import os

from .common import *
from lxml import etree


def fetch_net_worth_history(fund_code, fund_name, start_date, end_date=None, is_update=False, verbose=None):
    end = end_date
    if end_date is None:
        end = time.strftime('%Y-%m-%d') # today
    def _get_page(fund_code, start_date, end_date, index, size):

        print('Fetching net worth history of %s from %s to %s. Page %s.' % (fund_code, start_date, end_date, index))
        url = "http://api.fund.eastmoney.com/f10/lsjz?callback=callback' \
            '&fundCode=%s&pageIndex=%s&pageSize=%s&startDate=%s&endDate=%s_=%s"
        timestamp = time.time() 
        timestamp = int(timestamp * 1000)
        url = url % (fund_code, index, size, start_date, end_date, str(timestamp))
        resp = get(url)
        text = resp.text
        matches = re.search('\{.*\}', text)
        history_str = matches.group(0)
        history_json = json.loads(history_str)
        total_count = history_json['TotalCount']
        data = history_json['Data']
        error_code = history_json['ErrCode']

        return error_code, total_count, data
    
    total_count = 1000 # must larger size
    size = 260 # there are about 260 workday per year

    err_code, total_count, data = _get_page(fund_code, start_date, end, 1, 50)
    file_name = '%s-%s-%s-%s.json' % (fund_code, fund_name, start_date, end)
    file_name = os.path.join('data', file_name)
    with open(file_name, 'a' if is_update else 'w') as f:
        pages = round(total_count / size)
        for i in range(pages):
            index = i + 1
            err_code, total_count, data = _get_page(fund_code, start_date, end, index, size)
            if err_code == 0:
                f.write(json.dumps(data, ensure_ascii=False))
                f.write('\n')
                print('Fetching net worth history of %s from %s to %s. Page %s. Done.' % (fund_code, start_date, end, index))
            else:
                print('Fetch net worth history of %s at page %s fail.' % (fund_name, index))

    return file_name

def get_all_funds_code_and_name(file=None):
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    url = 'http://fund.eastmoney.com/js/fundcode_search.js'#'http://fund.eastmoney.com/allfund.html'
    resp = get(url)
    text = resp.text.lstrip('var r = ').rstrip(';')
    json_obj = json.loads(text)
    print('Saving all funds info to %s.' % file)
    if file is None:
        file = os.path.join('data', fund_list_file)
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

    resp = get(url)
    html = etree.HTML(resp.text)

    sourcerate = html.xpath('//b[@class="sourcerate"]')

    if len(sourcerate) > 0:

        label = sourcerate[0].xpath('parent::*')[0]
        discount = label.xpath('//b[@class="red"]')
        discount = discount[0].text if discount else 10 # 10: no discount
        sourcerate = sourcerate[0].text

    else:
        sourcerate = None
        discount = None # undefined

    # locate to the summary 
    tables = html.xpath('//div[@class="detail"]/div[@class="txt_cont"]//div[@class="box"]')
    rows = tables[0].xpath('table//tr')
    date_row = rows[2]
    date_cell = date_row.xpath('td')
    if len(date_cell) > 0 and date_cell[1].text is not None:
        establish_date = re.search('\d{4}年\d{2}月\d{2}', date_cell[1].text).group(0)
    else:
        establish_date = None
    manager_cell = rows[5].xpath('td')[0]
    manager = manager_cell.xpath('a')[0]
    company_cell = rows[4].xpath('td')[0]
    company = company_cell.xpath('a')[0]
    host_cell = rows[4].xpath('td')[1]
    host = host_cell.xpath('a')[0]
    amount_cell = rows[3].xpath('td')[0]
    amount = re.search('\d+\.?\d*', amount_cell.text)
    if amount:
        amount = amount.group(0)
    else:
        amount = None
    #fund_type = rows[1].xpath('td')[1]

    last_row = rows[-1]
    last_cell = last_row.xpath('td')[-1]
    index = last_cell.text

    establish_date = establish_date.replace('年', '-')
    establish_date = establish_date.replace('月', '-')
    establish_date = establish_date.replace('日', '-')
    print('Fetching basic info of %s. Done.' % code)

    return {'成立日期': establish_date, '基金经理': manager.text, #'基金类型':fund_type.text, 
            '原始费率': sourcerate, '折扣': discount, '基金公司': company.text, 
            '基金规模':amount, '跟踪指数': index}

def manager_history(fund_code):
    url = 'http://fundf10.eastmoney.com/jjjl_%s.html' % fund_code
    resp = get(url)
    html = etree.HTML(resp.text)
    target_table = html.xpath('//tbody')[1]
    rows = target_table.xpath('tr')
    managers = []
    for i, row in enumerate(rows):
        cols = row.xpath('td')
        start = cols[0].text
        end = cols[1].text if cols[1].text != '至今' else time.strftime('%Y-%m-%d')
        who = [i.text for i in cols[2].xpath('a')]
        duration = cols[3].text
        earning_rate = cols[4].text
        managers.append({
            'id': i,
            'start': start,
            'end': end,
            'who': who,
            'duration': duration,
            'earning_rate': earning_rate
        })
    return managers

def fetch_fees(code):
    print('Fetching fees of %s.' % code)
    result = []
    url = 'http://fundf10.eastmoney.com/jjfl_%s.html'  % code
    resp = get(url)
    html = etree.HTML(resp.text)
    boxs = html.xpath('//div[@class="box"]')

    # 交易状态
    status = boxs[0].xpath('div//td[@class="w135"]')
    if len(status) > 0:
        buy_status = status[0]
        sell_status = status[1]
        result.extend([{'申购状态': buy_status.text, '赎回状态': sell_status.text}])

    # 申购与赎回金额
    buy_and_sell = boxs[1].xpath('div//td[@class="w135"]')
    if len(buy_and_sell) > 0:
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
    if len(comfirm) > 0:
        buy_comfirm = comfirm[1]
        sell_comfirm = comfirm[3]
        result.append({'买入确认日': buy_comfirm.text, '卖出确认日': sell_comfirm.text})

    # 运作费率
    operating_fees = boxs[3].xpath('div//td[@class="w135"]')
    if len(operating_fees) > 0:
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
    if len(boxs) > 4:
        result.append({'认购费率（前端）': _get_fees(boxs[4])})
        # 申购费率
    if len(boxs) > 5:
        result.append({'申购费率（前端）': _get_fees(boxs[5])})
        # 赎回费率
    if len(boxs) > 6:
        result.append({'赎回费率': _get_fees(boxs[6])})

    print('Fetching fees of %s. Done.' % code)
    return result

def fetch_top10stock(code):
    pass

#fetch_fees('588090')
# fetch_fund_basic_info('501008')
# get_all_funds_code_and_name()
# fetch_net_worth_history('590001', '天弘中证食品饮料指数C', '2011-01-01', None)
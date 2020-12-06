import csv
import sys
import os
from funds import *

def ensure_enviroments():
    if not os.path.exists('data'):
        os.mkdir('data')

def parse_args():
    pass


def main():
    args = parse_args()
    all_funds = get_all_funds_code_and_name()
    funds_info = open(os.path.join('data', 'fundsdetails.json'), 'w')
    #funds_info_csv = csv.DictWriter(funds_info, ['基金代码'， '基金名字'， '成立日期',
    #                                        '基金经理', '基金规模'， '跟踪指数', '基金类型', ''])
    keys = ['基金代码', '基金名称拼音首字母', '基金名称', '基金类型', '基金名称全拼']
    for item in all_funds:
        try:
            basic_info = fetch_fund_basic_info(item[0])
            fees = fetch_fees(item[0])
            history = fetch_net_worth_history(item[0], item[2], basic_info['成立日期'], None)
            #funds_info_csv.writerow({ '基金代码': ， '基金名字'， '成立日期',
            #                                '基金经理', '基金规模'， '跟踪指数', '基金类型'
            #})

            basic = {**dict(zip(keys, item)), **basic_info}
            fund = {'基本概况': basic, '费率详情': fees, '历史净值地址': history}
            fund_str = json.dumps(fund, ensure_ascii=False)
            funds_info.write(fund_str)
            funds_info.write('\n')
            funds_info.flush()

        except Exception as e:
            print(str(e))
            pass





if __name__ == "__main__":
    ensure_enviroments()
    main()
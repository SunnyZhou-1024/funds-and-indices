import argparse
import csv
import os
import sys
import time

from funds import *

def ensure_enviroments():
    if not os.path.exists('data'):
        os.mkdir('data')

def parse_args():
    parser = argparse.ArgumentParser(description='Parse arguments of this program.')
    parser.add_argument('--reentry', default=True, help='Start from the stop point of most recent time.')
    return parser.parse_args()


def main():
    args = parse_args()
    checkpoint = []
    all_funds = None
    if args.reentry and os.path.exists(os.path.join('data', 'checkpoint.txt')):
        with open(os.path.join('data', 'checkpoint.txt'), 'r') as f:
            fetched = f.read()
            if fetched != '':
            # TO-DO: Should replace with a most rubost reentry method
                checkpoint.extend(json.loads(fetched))
            #checkpoint = int(fetched)
        
        # If enable reentry, we should read the fund list info from file rather than make request 
        # But now, just make request.
        #with open(os.path.join('data', '.txt'), 'r') as f:

    else:
        pass
    all_funds = get_all_funds_code_and_name()


    timestamp = time.time()
    timestamp = str(int(timestamp))
    funds_info = open(os.path.join('data', 'fundsdetails-%s.json' % timestamp), 'w')
    checkpoint_file = open(os.path.join('data', 'checkpoint.txt'), 'w')
    #funds_info_csv = csv.DictWriter(funds_info, ['基金代码'， '基金名字'， '成立日期',
    #                                        '基金经理', '基金规模'， '跟踪指数', '基金类型', ''])
    keys = ['基金代码', '基金名称拼音首字母', '基金名称', '基金类型', '基金名称全拼']

    #all_funds = all_funds[checkpoint: ]
    for item in all_funds:
        if item[0] in checkpoint:
            continue
        try:
            checkpoint.append(item[0])
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

            checkpoint_file.write(json.dumps(checkpoint))
            checkpoint_file.flush()

        except Exception as e:
            print(str(e))
            pass

    funds_info.close()
    checkpoint_file.close()





if __name__ == "__main__":
    ensure_enviroments()
    main()
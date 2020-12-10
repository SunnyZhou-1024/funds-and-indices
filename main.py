import argparse
import csv
import os
import sys
import time
import json

from src.funds.common import details_of_fund_file
from src.funds.funds import *
from src.util import Logger
from src.funds.utils import extract_brief_info

def ensure_enviroments():
    if not os.path.exists('data'):
        os.mkdir('data')

def parse_args():
    parser = argparse.ArgumentParser(description='Parse arguments of this program.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--reentry', action='store_true', help='Start from the stop point of most recent time.')
    group.add_argument('--update', action='store_true', help='Update existing info to newest status.')
    group.add_argument('--scan', action='store_true', help='Download new funds\' info.')
    return parser.parse_args()

def move(src, dest, logger):
    src_file = open(src, 'r')
    dest_file = open(dest, 'a')
    dest_info = extract_brief_info(dest, logger)
    dest_list = [i[0] for i in dest_info]
    line = src_file.readline()
    while line != '':
        jzon = json.loads(line)
        code = jzon['基本概况']['基金代码']
        if code not in dest_list:
            dest_file.write(line)
            dest_file.write('\n')
    src_file.close()
    dest_file.close()

    os.remove(src)
    os.rename(dest, src)


def main():
    logger = Logger()
    args = parse_args()
    checkpoint = []
    all_funds = None

    if args.reentry and os.path.exists(os.path.join('data', 'checkpoint.txt')):
        with open(os.path.join('data', 'checkpoint.txt'), 'r') as f:
            fetched = f.read()
            if fetched != '':
                checkpoint.extend(json.loads(fetched))
        all_funds = get_all_funds_code_and_name()
        
    elif args.update:
        all_funds = extract_brief_info(os.path.join('data', details_of_fund_file), logger)
        checkpoint = []

    elif args.scan:
        exist = extract_brief_info(os.path.join('data', details_of_fund_file), logger)
        checkpoint = [ fund[0] for fund in exist]
        all_funds = get_all_funds_code_and_name()

    else:
        all_funds = get_all_funds_code_and_name()
        checkpoint = []



    keys = ['基金代码', '基金名称拼音首字母', '基金名称', '基金类型', '基金名称全拼']
    funds_info = open(os.path.join('data', details_of_fund_file), 'a')
    if args.update:
        funds_info.close()
        funds_info = open(os.path.join('data', 'tmp-' + details_of_fund_file), 'w')
    for item in all_funds:
        if item[0] in checkpoint:
            continue
        try:
            basic_info = fetch_fund_basic_info(item[0])
            today = time.strftime('%Y-%m-%d')
            if basic_info['成立日期'] is not None:
                fees = fetch_fees(item[0])
                history = fetch_net_worth_history(item[0], item[2], item[5] if args.update else basic_info['成立日期'], today)

            basic = {**dict(zip(keys, item)), **basic_info, **{'最后获取日期': today}}
            fund = {'基本概况': basic, '费率详情': fees, '历史净值地址': history}
            fund_str = json.dumps(fund, ensure_ascii=False)
            funds_info.write(fund_str)
            funds_info.write('\n')
            funds_info.flush()
            checkpoint.append(item[0])

            with open(os.path.join('data', 'checkpoint.txt'), 'w') as checkpoint_file:
                checkpoint_file.write(json.dumps(checkpoint))

        except Exception as e:
            print(str(e))
            pass

    funds_info.close()





if __name__ == "__main__":
    ensure_enviroments()
    main()
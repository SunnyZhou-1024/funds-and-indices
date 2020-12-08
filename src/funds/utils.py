import json
import os
import sys 

from src.funds.common import *

def extract_brief_info(file, logger):
    if not os.path.exists(file):
        logger.error('File %s not found. Can\'t execute update', file)
        sys.exit(1)
    basic_list = []

    with open(file, 'r') as f:
        line = f.readline()
        while line != '':
            jzon = json.loads(line)
            basic = jzon['基本概况']
            basic_list.append([basic['基金代码'], basic['基金名称拼音首字母'], basic['基金名称'], 
                                basic['基金类型'], basic['基金名称全拼'], basic['最后获取日期']])
            line = f.readline()

    return basic_list

if __name__ == "__main__":
    logger = Logger()
    extract_brief_info('/home/sunny/workspace/github/funds-and-indices/data/details-of-fund.json', logger)
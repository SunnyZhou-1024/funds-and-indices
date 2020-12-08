import json
import os

from common import *

def extract_brief_info(file):
    with open(os.path.join('data', file), 'r') as f:
        line = f.readline()
        while line != '':
            jzon = json.loads(line)
            line = f.readline()
            pass

if __name__ == "__main__":
    extract_brief_info('/home/sunny/workspace/github/funds-and-indices/data/000001-华夏成长混合-2001-11-28-2020-12-08.json')
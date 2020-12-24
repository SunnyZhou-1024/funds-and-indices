import json
import os 
import sys

from enum import Enum
from src.funds.common import details_of_fund_file

class InfoType(Enum):
    ALL = 0
    FEE = 1
    BASIC_INFO = 2
    INDEX = 3

class History(object):
    def __init__(self, file, managers):
        self._file = file
        self._managers = managers

    def _calc_max_retracement():

    def _load_history(file):
        hist = []
        with open(file, 'r') as f:
            line = f.readline()
            obj = json.loads(line)
            part = obj['LSJZList']
            for p in part:
                hist.append((p['FSRQ'], p['']))



    def _key(pair):
        return pair[0]

def load(file=details_of_fund_file, info_type=InfoType.ALL)

    pass

if __name__ == '__main__':

    pass
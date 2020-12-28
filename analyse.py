import json
import os 
import sys

from typing import Dict, Set, List, Any, Callable, Iterable, Tuple,


from enum import Enum
from src.funds.common import details_of_fund_file

class InfoType(Enum):
    ALL = 0
    FEE = 1
    BASIC_INFO = 2
    INDEX = 3

class History(object):
    def __init__(self, file, managers):
        self._managers = managers

    
    def _calc_max_retracement(self, hist: List[Tuple[str, str]]):
        candidate = hist[0][1]
        min_jz = candidate
        pre_min = candidate
        pre_max_retreat = (candidate-pre_min) / candidate
        for date, value in hist:
            if value > candidate:
                candidate = value
                min_jz = candidate
            elif value == candidate:
                pre_min = min_jz
                pre_max_retreat = max(pre_max_retreat, (candidate-pre_min)/candidate)
            else:
                min_jz = min(min_jz, value)
        return float(min_jz)

    def _load_history(self, file: str, managers: List[Dict[str, Tuple[str, str]]]) \
            -> Dict[str, float]:
        hist = []
        with open(file, 'r') as f:
            line = f.readline()
            while line:
                obj = json.loads(line)
                part = obj['LSJZList']
                for p in part:
                    hist.append((p['FSRQ'], p['LJJZ']))
                line = f.readline()

        sorted_hist = sorted(hist, key=self._key)
        manager_to_hist = dict()
        for name, duration in enumerate(managers):
            start, end = sorted(duration, key=str.lower)
            manager_hist = sorted_hist[sorted_hist.index(start): sorted_hist.index(end)]
            max_retreat = self._calc_max_retracement(manager_hist)
            manager_to_hist[name] = max_retreat

        return manager_to_hist


                



    def _key(pair):
        return pair[0]

def load(file: str=details_of_fund_file, info_type: Any=InfoType.ALL) -> Dict[str, History]
    with open(file, 'r') as fd:
        line = fd.readline()
        fund_info = dict()
        while line:
            obj = json.loads(line)
            code = obj['基本概况']['基金代码']
            file_path = obj['历史净值地址']
            managers = obj['历任基金经理']



    pass

if __name__ == '__main__':

    pass
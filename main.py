import sys
from funds import *

def ensure_enviroments():
    if not os.path.exists('data'):
        os.mkdir('data')

def parse_args():
    pass


def main():
    args = parse_args()
    all_funds = get_all_funds_code_and_name()
    
    for item in all_funds:
        basic_info = fetch_fund_basic_info(item[0])
        fees = fetch_fees(item[0])
        history = fetch_net_worth_history(item[0], item[2], basic_info[0], None)





if __name__ == "__main__":
    ensure_enviroments()
    main()
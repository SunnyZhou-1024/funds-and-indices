import json
import os
import sys

from lxml import etree

from src.funds.common import get
from src.funds.common import company_file



def get_all_companies():
    url = 'http://fund.eastmoney.com/company/default.html'
    resp = get(url)
    companies = []
    if resp.status_code == 200:
        html = etree.HTML(resp.text, parser=etree.HTMLParser(encoding='ISO-8859-1'))
        companies_div = html.xpath('//div[@id="companyCon"]')[0]
        company_rows = companies_div.xpath('.//tbody/tr')
        for row in company_rows:
            company_cols = row.xpath('td')
            name = company_cols[1].xpath('a')[0].text
            start_from = company_cols[3].text
            scale = company_cols[5].xpath('attribute::data-sortvalue')[0]
            funds = company_cols[6].xpath('a')[0].text
            managers = company_cols[7].xpath('a')[0]
            manager_amount = managers.text
            managers_link = managers.xpath('attribute::href')[0]
            companies.append({
                'name': name,
                'start_from': start_from,
                'scale': scale,
                'fund_amount': funds,
                'manager_amount': manager_amount,
                'managers_link': managers_link
            })
    return companies

def main():
    companies = get_all_companies()
    dumps = json.dumps(companies, ensure_ascii=False)
    with open(os.path.join('data', 'company', company_file), 'w', encoding='ISO-8859-1') as f:
        f.write(dumps)
    pass

if __name__ == "__main__":
    if not os.path.exists(os.path.join('data', 'company')):
        os.makedirs(os.path.join('data', 'company'))
    main()
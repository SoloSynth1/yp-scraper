import requests
from bs4 import BeautifulSoup
import re
import json

site_url = "http://www.yp.com.hk"

def get_industries():
    response = requests.get(site_url)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('div', {'id': 'SITEMAP'}).find('table')
    industries = table.find_all('tr')[1].find('td').find_all('li')
    return {'items' :[{'name':industry.text, 'link':industry.find('a')['href']} for industry in industries]}

def get_subcategories(result_dict):
    industries = result_dict['items']
    for industry in industries:
        subcat_url = site_url + industry['link']
        response = requests.get(subcat_url)
        soup = BeautifulSoup(response.text, 'lxml')
        subcat_table = soup.find('ul', {'class': 'ifr'})
        if subcat_table:
            subcats = subcat_table.find_all('a')
            industry['items'] = [{'name': re.sub(r'\(\d+\)', '', subcat.text).strip(),
                                       'link':subcat['href']} for subcat in subcats]
            get_subcategories(industry)
        else:
            print(industry)


if __name__ == "__main__":
    industries = get_industries()
    get_subcategories(industries)

    with open('output.json', 'w') as f:
        f.write(json.dumps(industries))

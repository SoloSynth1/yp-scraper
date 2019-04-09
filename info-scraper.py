import requests
from bs4 import BeautifulSoup
import json
import re

site_url = "http://www.yp.com.hk"
output_file = open('output.csv', 'w')

def load_subcats(json_file='output.json'):
   with open(json_file, 'r') as f:
       return json.loads(f.read())

def get_child_nodes(industries, subcats, name='', ):
    if 'name' in industries.keys():
        name += '"{}",'.format(industries['name'])

    if 'items' in industries.keys():
        for industry in industries['items']:
            get_child_nodes(industry, subcats, name)
    else:
        subcats.append((name, industries['link']))


def scrape_subcat(name, start_link, items=[]):
    response = requests.get(start_link)
    soup = BeautifulSoup(response.text, 'lxml')
    listings = get_companies(soup)
    write_info(name, listings)
    page_links = soup.find('div', {'class': 'srh_pgnum'}).find_all('a')
    if page_links and page_links[-1].text == "下一頁":
        scrape_subcat(name, site_url + page_links[-1]['href'], items)

def clean_text(input_text):
    return input_text.replace('│', '').replace('\n', '').strip()

def get_companies(soup):
    listings = soup.find_all('div', {'class': 'listing_div'})
    results = []
    for listing in listings:
        td = listing.find('td', {'class': 'left_col'})
        company_name = clean_text(td.find('span', {'class': 'cname'}).text)
        detail_page = td.find('span', {'class': 'cname'}).find_all('a')
        if detail_page:
            response = requests.get(site_url+detail_page[0]['href'])
            soup = BeautifulSoup(response.text, 'lxml')
            items = soup.find('div', {'id':'div_listing'}).find_all('tr')

            tel_no = clean_text(items[0].find_all('td')[1].text)
            addr = clean_text(items[1].find_all('td')[1].text)
            links = items[2].find_all('td')[1].find_all('a')
            if links:
                link = clean_text(links[0].text)
            else:
                link = ''
            mail_addrs = items[3].find_all('td')[1].find_all('a')
            if mail_addrs:
                mail_addr = clean_text(mail_addrs[0].text)
            else:
                mail_addr = ''
            working_hour = clean_text(items[4].find_all('td')[1].text)

            regex_search = re.search(r'staticMapPoint\((.*?)\)', response.text)
            lat, long = [x.replace(' ', '') for x in regex_search.group(1).split(',')]
        else:
            lat, long = '', ''
            tel_no = clean_text(td.find('nobr').text)
            addr = clean_text(td.find('span', {'class': 'addr'}).text)
            link = td.find_all('a', {'rel': 'nofollow'})

            if link:
                link = link[0]['href']
            else:
                link = ''
            mail_addr = ''
            working_hour = ''

        results.append((company_name, tel_no, addr, link, mail_addr, working_hour, lat, long))
    return results

def write_info(name, listings):
    for listing in listings:
        print(listing)
        output_file.write(name + '"{}","{}","{}","{}","{}","{}","{}","{}"\n'.format(listing[0], listing[1], listing[2], listing[3], listing[4], listing[5], listing[6], listing[7]))

if __name__ == "__main__":
    industries = load_subcats()
    subcats = []
    get_child_nodes(industries, subcats)
    for subcat in subcats:
        name = subcat[0]
        start_link = site_url + subcat[1]
        scrape_subcat(name, start_link)




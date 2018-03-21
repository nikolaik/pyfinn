from pprint import pprint

import sys
from requests_html import HTMLSession


session = HTMLSession()


def _clean(text):
    text = text.replace('\xa0', ' ').replace(',-', '').replace(' m²', '')
    try:
        text = int(text.replace(' ', ''))
    except ValueError:
        pass

    return text


def _list_to_vals(r, data, selector):
    values_list = r.html.find(selector, first=True).find('dt, dd')
    values_list = iter(values_list)
    for a in values_list:
        key = a.text
        a = next(values_list)
        data[key] = _clean(a.text)


def scrape_ad(url):
    r = session.get(url)
    ad_data = {
        'Postaddresse': r.html.find('h1 + p', first=True).text,
        'Prisantydning': _clean(r.html.find('h1 + p + dl > dd', first=True).text)
    }
    _list_to_vals(r, ad_data, 'h1 + p + dl + dl')
    _list_to_vals(r, ad_data, 'h1 + p + dl + dl + dl')

    return ad_data


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Invalid number of arguments.\n\nUsage:\n$ python finn.py URL')
        exit(1)

    ad_url = sys.argv[1]
    ad = scrape_ad(ad_url)
    for key, value in ad.items():
        print('{}:\t{}'.format(key, value))

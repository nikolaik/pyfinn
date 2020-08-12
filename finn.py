import json
import re
import sys
from datetime import datetime
from urllib import parse

from fake_useragent import UserAgent
from requests_html import HTMLSession


session = HTMLSession()
ua = UserAgent()


def _clean(text):
    text = text.replace('\xa0', ' ').replace(',-', '').replace(' m²', '')
    try:
        text = int(re.sub(r'kr$', '', text).replace(' ', ''))
    except ValueError:
        pass

    return text


def _parse_data_lists(html):
    data = {}
    days = ['Man.', 'Tir.', 'Ons.', 'Tors.', 'Fre', 'Lør.', 'Søn.']
    skip_keys = ['Mobil', 'Fax', '', ] + days  # Unhandled data list labels

    data_lists = html.find('dl')
    for el in data_lists:
        values_list = iter(el.find('dt, dd'))
        for a in values_list:
            _key = a.text
            a = next(values_list)
            if _key in skip_keys:
                continue
            data[_key] = _clean(a.text)

    return data


def _scrape_viewings(html):
    # Find links to ICAL downloads
    viewings = set()
    calendar_url = [el.attrs["href"] for el in html.find('a[href*=".ics"]')]
    for url in calendar_url:
        query_params = dict(parse.parse_qsl(parse.urlsplit(url).query))
        dt = datetime.strptime(query_params['iCalendarFrom'][:-1], '%Y%m%dT%H%M%S')
        if dt:
            viewings.add(dt.isoformat())
    return list(viewings)


def _calc_price(ad_data):
    debt = ad_data.get('Fellesgjeld', 0)
    cost = ad_data.get('Omkostninger', 0)
    return ad_data['Totalpris'] - debt - cost


def scrape_ad(finnkode):
    url = 'https://www.finn.no/realestate/homes/ad.html?finnkode={code}'.format(code=finnkode)
    r = session.get(url, headers={'user-agent': ua.random})

    r.raise_for_status()

    html = r.html

    postal_address_element = html.find('h1 + p', first=True)
    if not postal_address_element:
        return

    ad_data = {
        'Postadresse': postal_address_element.text,
        'url': url,
    }

    viewings = _scrape_viewings(html)
    if viewings:
        ad_data['Visninger'] = viewings
        ad_data.update({'Visning {}'.format(i): v for i, v in enumerate(viewings, start=1)})

    ad_data.update(_parse_data_lists(html))

    if 'Totalpris' in ad_data:
        ad_data['Prisantydning'] = _calc_price(ad_data)

    return ad_data


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Invalid number of arguments.\n\nUsage:\n$ python finn.py FINNKODE')
        exit(1)

    ad = scrape_ad(sys.argv[1])
    print(json.dumps(ad, indent=2, ensure_ascii=False))

import sys

import dateparser
from fake_useragent import UserAgent
from requests_html import HTMLSession


session = HTMLSession()
ua = UserAgent()


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


def _viewings(r):
    viewings = []
    els = r.html.find('.hide-lt768 time')
    for el in els:
        # Ninja parse dt range string in norwegian locale. Example: "søndag 08. april, kl. 13:00–14:00"
        split_space = el.text.strip().split(' ')
        if len(split_space) < 5:
            continue
        date, time_range = ' '.join(split_space[1:]).replace(' kl. ', '').split(',')
        # start_hour, start_min = time_range.split('–')[0].split(':')
        dt = dateparser.parse(date, languages=['nb'])
        if dt:
            # dt = dt.replace(hour=int(start_hour), minute=int(start_min))
            viewings.append(dt.date().isoformat())
    return viewings


def scrape_ad(finnkode):
    url = 'https://www.finn.no/realestate/homes/ad.html?finnkode={code}'.format(code=finnkode)
    r = session.get(url, headers={'user-agent': ua.random})

    r.raise_for_status()

    postal_address_element = r.html.find('h1 + p', first=True)
    price_element = r.html.find('h1 + p + dl > dd', first=True)
    if not price_element or not postal_address_element:
        return

    viewings = _viewings(r)
    ad_data = {
        'Postadresse': postal_address_element.text,
        'Prisantydning': _clean(price_element.text),
        'Visningsdatoer': viewings,
        'url': url
    }
    ad_data.update({'Visningsdato {}'.format(i): v for i, v in enumerate(viewings, start=1)})
    _list_to_vals(r, ad_data, 'h1 + p + dl + dl')
    _list_to_vals(r, ad_data, 'h1 + p + dl + dl + dl')

    return ad_data


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Invalid number of arguments.\n\nUsage:\n$ python finn.py FINNKODE')
        exit(1)

    ad_url = sys.argv[1]
    ad = scrape_ad(ad_url)
    for key, value in ad.items():
        print('{}:\t{}'.format(key, value))

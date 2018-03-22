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


def scrape_ad(url=None, code=None):
    assert url is not None or code is not None

    if url is None:
        url = 'https://www.finn.no/realestate/homes/ad.html?finnkode={code}'.format(code=code)
    r = session.get(url)

    r.raise_for_status()

    postal_address_element = r.html.find('h1 + p', first=True)
    price_element = r.html.find('h1 + p + dl > dd', first=True)
    if not price_element or not postal_address_element:
        return

    ad_data = {
        'Postaddresse': postal_address_element.text,
        'Prisantydning': _clean(price_element.text)
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

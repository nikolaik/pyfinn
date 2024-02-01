import argparse
import io
import json
import logging
import re
from datetime import datetime
import sys
from urllib import parse

from fake_useragent import UserAgent
from requests_html import HTMLSession, HTML


session = HTMLSession()
ua = UserAgent()

logger = logging.getLogger("pyfinn")
handler = logging.StreamHandler()
formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def _clean(text):
    text = text.replace("\xa0", " ").replace(",-", "").replace(" m²", "")
    try:
        text = int(re.sub(r"kr$", "", text).replace(" ", ""))
    except ValueError:
        pass

    return text


def _parse_data_lists(html: HTML) -> dict:
    data = {}
    days = ["Man.", "Tir.", "Ons.", "Tors.", "Fre", "Lør.", "Søn."]
    skip_keys = ["Mobil", "Fax", ""] + days  # Unhandled data list labels

    data_lists = html.find("dl")
    for el in data_lists:
        values_list = iter(el.find("dt, dd"))
        for a in values_list:
            _key = a.text
            a = next(values_list)
            if _key in skip_keys:
                continue
            data[_key] = _clean(a.text)

    return data


def _scrape_viewings(html: HTML) -> list[str]:
    # Find links to ICAL downloads
    viewings = set()
    calendar_url = [el.attrs["href"] for el in html.find('a[href*=".ics"]')]
    for url in calendar_url:
        query_params = dict(parse.parse_qsl(parse.urlsplit(url).query))
        dt = datetime.strptime(query_params["iCalendarFrom"][:-1], "%Y%m%dT%H%M%S")
        if dt:
            viewings.add(dt.isoformat())
    return sorted(list(viewings))


def _calc_price(ad_data: dict) -> int:
    debt = ad_data.get("Fellesgjeld", 0)
    cost = ad_data.get("Omkostninger", 0)
    return ad_data["Totalpris"] - debt - cost


def fetch_ad(url: str) -> HTML:
    r = session.get(url, headers={"user-agent": ua.random})
    r.raise_for_status()
    return r.html


def scrape_ad(html: HTML) -> dict:
    postal_address_element = html.find('[data-testid="object-address"]', first=True)
    if not postal_address_element:
        return {}

    ad_data = {
        "Postadresse": postal_address_element.text,
    }

    viewings = _scrape_viewings(html)
    if viewings:
        ad_data["Visninger"] = viewings
        ad_data.update({f"Visning {i}": v for i, v in enumerate(viewings, start=1)})

    ad_data.update(_parse_data_lists(html))

    if "Totalpris" in ad_data:
        ad_data["Prisantydning"] = _calc_price(ad_data)

    return ad_data


def main():
    parser = argparse.ArgumentParser(description="Fetch real estate listing from finn.no and make available as JSON")
    parser.add_argument("code")
    parser.add_argument("--html-file", type=argparse.FileType())
    args = parser.parse_args()
    html_file: io.TextIOWrapper | None = args.html_file
    code: str = args.code

    url = f"https://www.finn.no/realestate/homes/ad.html?finnkode={code}"
    if html_file:
        with html_file:
            html_raw = html_file.read()
            html = HTML(url=url, html=html_raw)
    else:
        html = fetch_ad(url)

    ad_data = scrape_ad(html)
    if not ad_data:
        logger.warning("Could not find postal address element in HTML")
    print(json.dumps({"url": url} | ad_data, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())

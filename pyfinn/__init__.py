import argparse
import io
import json
import logging
import re
from datetime import datetime
import sys
from urllib import parse

from fake_useragent import UserAgent

from bs4 import BeautifulSoup
import requests

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


def _parse_data_lists(html: BeautifulSoup) -> dict:
    data = {}
    days = ["Man.", "Tir.", "Ons.", "Tors.", "Fre", "Lør.", "Søn."]
    skip_keys = ["Mobil", "Fax", ""] + days  # Unhandled data list labels

    data_lists = html.find_all("dl")
    for el in data_lists:
        values_list = iter(el.find_all(["dt", "dd"]))
        for a in values_list:
            _key = a.text
            a = next(values_list)
            if _key in skip_keys:
                continue
            data[_key] = _clean(a.text)

    return data


def _scrape_viewings(html: BeautifulSoup) -> list[str]:
    """Find links to iCal downloads and extract the date from the query string"""
    viewings = set()
    anchors = html.find_all("a")
    anchors_ics = [el for el in anchors if ".ics" in el.attrs.get("href", "")]
    calendar_url = [el.attrs["href"] for el in anchors_ics]
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


def fetch_ad(url: str) -> str:
    r = requests.get(url, headers={"user-agent": ua.random})
    r.raise_for_status()
    return r.text


def scrape_ad(html_text: str) -> dict:
    html = BeautifulSoup(html_text, "lxml")
    postal_address_element = html.find(None, {"data-testid": "object-address"})
    if not postal_address_element:
        logger.warning("Could not find postal address element in HTML")
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


class CLIArgs(argparse.Namespace):
    code: str
    html_file: io.TextIOWrapper | None


def init_parser() -> CLIArgs:
    parser = argparse.ArgumentParser(description="Fetch real estate listing from finn.no and make available as JSON")
    parser.add_argument("code")
    parser.add_argument("--html-file", type=argparse.FileType())
    return parser.parse_args()


def main():
    args = init_parser()

    url = f"https://www.finn.no/realestate/homes/ad.html?finnkode={args.code}"
    html = read_or_fetch_html(args.html_file, url)
    ad_data = scrape_ad(html)
    if not ad_data:
        logger.warning("Could not find postal address element in HTML")
    print(json.dumps({"url": url} | ad_data, indent=2, ensure_ascii=False, sort_keys=True))

    return 0


def read_or_fetch_html(html_file: io.TextIOWrapper | None, url: str):
    if not html_file:
        return fetch_ad(url)

    with html_file:
        return html_file.read()


if __name__ == "__main__":
    sys.exit(main())

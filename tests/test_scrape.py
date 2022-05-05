import responses

from pyfinn import scrape_ad


@responses.activate
def test_scrape_ad(ad):
    finnkode = "257069951"
    responses.get(
        f"https://www.finn.no/realestate/homes/ad.html?finnkode={finnkode}",
        status=200,
        body=ad,
    )
    res = scrape_ad(finnkode)
    assert res
    assert res == {
        "Postadresse": "Thereses gate 35B, 0354 Oslo",
        "url": "https://www.finn.no/realestate/homes/ad.html?finnkode=257069951",
        "Visning 1": "2022-05-08T13:00:00",
        "Visning 2": "2022-05-09T14:30:00",
        "Visninger": ["2022-05-08T13:00:00", "2022-05-09T14:30:00"],
        "Omkostninger": 12600,
        "Totalpris": 3802600,
        "Felleskost/mnd.": 3077,
        "Boligtype": "Leilighet",
        "Eieform bolig": "Aksje",
        "Soverom": 1,
        "Primærrom": 30,
        "Bruksareal": 30,
        "Etasje": 4,
        "Byggeår": 1923,
        "Energimerking": "F - mørkegrønn",
        "Rom": 2,
        "Tomteareal": "1391 (eiet)",
        "Boligselgerforsikring": "Ja",
        "Fellesformue": 127032,
        "Formuesverdi": 796595,
        "Prisantydning": 3790000,
    }

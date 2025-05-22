from pyfinn import scrape_ad


def test_scrape_ad(ad_html):
    res = scrape_ad(ad_html)
    assert res
    assert res == {
        "Boligtype": "Leilighet",
        "Bruksareal": 30,
        "Byggeår": 1880,
        "Eieform": "Eier (Selveier)",
        "Eksternt bruksareal": "1 (BRA-e)",
        "Energimerking": "G - Rød",
        "Etasje": 2,
        "Fellesformue": 40375,
        "Fellesgjeld": 157595,
        "Felleskost/mnd.": 3710,
        "Formuesverdi": 809403,
        "Internt bruksareal": "29 (BRA-i)",
        "Omkostninger": 95568,
        "Postadresse": "Kirkegårdsgata 5, 0558 Oslo",
        "Prisantydning": 3245000,
        "Rom": 1,
        "Soverom": 1,
        "Tomteareal": "271 (eiet)",
        "Totalpris": 3498163,
        "Visning 1": "2024-02-01T15:30:00",
        "Visning 2": "2024-02-04T13:00:00",
        "Visninger": ["2024-02-01T15:30:00", "2024-02-04T13:00:00"],
    }

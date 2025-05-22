from pathlib import Path

import pytest

BASE_DIR = Path().parent.resolve()


@pytest.fixture
def ad_html():
    p = BASE_DIR.joinpath("tests/ads/337819107.html")
    yield p.read_text()

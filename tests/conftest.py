from pathlib import Path

import pytest

BASE_DIR = Path().parent.resolve()


@pytest.fixture
def ad():
    p = BASE_DIR.joinpath("tests/ads/257069951.html")
    with p.open() as fp:
        yield fp.read()

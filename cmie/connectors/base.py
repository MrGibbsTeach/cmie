import time
from abc import ABC, abstractmethod
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

from ..config import USER_AGENT, REQUEST_DELAY_SECONDS, REQUEST_TIMEOUT_SECONDS


HEADERS = {"User-Agent": USER_AGENT}


def fetch_html(url: str) -> str:
    time.sleep(REQUEST_DELAY_SECONDS)
    resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
    resp.raise_for_status()
    return resp.text


class BaseConnector(ABC):
    marketplace: str

    @abstractmethod
    def fetch_listings(self, **kwargs) -> List[Dict]:
        """
        Returns list of dicts with at least:
        marketplace, external_id, url, title, author,
        price, currency, grade_levels_raw, subject_raw,
        rating_avg, rating_count
        """
        raise NotImplementedError

    @staticmethod
    def html_parser(html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

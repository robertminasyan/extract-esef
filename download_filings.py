"""Helper function to download a XBRL-package."""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import pathlib
import urllib.request
import random
from enum import Enum


import requests

#from ..const import PATH_ARCHIVES_TE, PATH_ARCHIVES_TR, Country
PATH_BASE = pathlib.Path(__file__).parent.resolve()
PATH_PROJECT_ROOT = os.path.abspath(os.path.join(PATH_BASE, "."))
PATH_ARCHIVES_TE = os.path.abspath(os.path.join(PATH_PROJECT_ROOT, "archives_testing"))
PATH_ARCHIVES_TR = os.path.abspath(os.path.join(PATH_PROJECT_ROOT, "archives_training"))



class Country(str, Enum):
    """Representation of different countries."""

    DENMARK = "DK"
    FINLAND = "FI"
    ICELAND = "IS"
    NORWAY = "NO"
    SWEDEN = "SE"

BASE_URL = "https://filings.xbrl.org/"


@dataclass
class Filing:
    """Represent a filing."""

    country: str
    file_name: str
    path: str
k=0

IdentifierType = dict[str, list[Filing]]


def _parse_file_ending(path: str) -> str:
    global k
    """Parse the file ending."""
    path = path.lower()
    splitted_path = path.split("/")
    country_iso = splitted_path[-2]
    return country_iso


def _cleanup_package_dict(identifier_map: IdentifierType) -> list[Filing]:
    """
    Cleanup package dict and return only one filing.

    Will return the English version if available.
    """
    data_list: list[Filing] = []
    for key, _ in identifier_map.items():
        filing_list = identifier_map[key]

        if len(filing_list) == 1:
            data_list.append(filing_list[0])
            continue

        for filing in filing_list:
            if "en" in filing.file_name:
                data_list.append(filing)
                continue

    return data_list


def download_packages() -> None:
    """
    Download XBRL-packages from XBRL.org.

    Prefer the English version of there are multiple languages available.
    """
    identifier_map: IdentifierType = {}
    idx: int = 0

    with urllib.request.urlopen(f"{BASE_URL}table-index.json") as url:
        data = json.loads(url.read().decode())
        for idx, item in enumerate(data):
            if item["country"] in [
                Country.DENMARK,
                Country.FINLAND,
                Country.ICELAND,
                Country.NORWAY,
                Country.SWEDEN,
            ]:
                lei = item["lei"]
                filing = Filing(
                    country=_parse_file_ending(path=item["path"]),
                    file_name=item["report-package"],
                    path=item["path"],
                )

                if lei not in identifier_map:
                    identifier_map[lei] = [filing]
                else:
                    identifier_map[lei].append(filing)

    data_list = _cleanup_package_dict(identifier_map=identifier_map)
    random.shuffle(data_list)
    print("reports shuffled")

    print(f"{len(data_list)} items found")

    for idx, item in enumerate(data_list):
        if idx < 60:
            _download_package_TR(item)
        else:
            if(idx == 61):
                break
            _download_package_TE(item)


def _download_package_TR(filing: Filing) -> None:
    """Download a package and store it the archive-folder."""
    url = f"{BASE_URL}{filing.path}/{filing.file_name}"

    download_path1 = os.path.join(PATH_ARCHIVES_TR, filing.country)

    # Create download path if it does not exist
    Path(download_path1).mkdir(parents=True, exist_ok=True)

    print(f"Downloading {url}")

    req = requests.get(url, stream=True, timeout=30)
    write_location = os.path.join(download_path1, filing.file_name)
    with open(write_location, "wb") as _file:
        for chunk in req.iter_content(chunk_size=2048):
            _file.write(chunk)

def _download_package_TE(filing: Filing) -> None:
    """Download a package and store it the archive-folder."""
    url = f"{BASE_URL}{filing.path}/{filing.file_name}"

    download_path = os.path.join(PATH_ARCHIVES_TE, filing.country)

    # Create download path if it does not exist
    Path(download_path).mkdir(parents=True, exist_ok=True)

    print(f"Downloading {url}")

    req = requests.get(url, stream=True, timeout=30)
    write_location = os.path.join(download_path, filing.file_name)
    with open(write_location, "wb") as _file:
        for chunk in req.iter_content(chunk_size=2048):
            _file.write(chunk)

download_packages()
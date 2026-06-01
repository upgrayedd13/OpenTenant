from dataclasses import dataclass
from datetime import date
from typing import Any
import requests


@dataclass(frozen=True)
class AvailableApartmentUnit:
    unit_num:       int
    price:          float
    available_now:  bool
    date_available: date|None


def fetch_raw_apartment_data() -> Any:
    '''
    This function will perform the HTTP request below:
        :authority
        sightmap.com
        :method
        GET
        :path
        /app/api/v1/rkwnqrz8wd2/sightmaps/41372
        :scheme
        https
        accept
        application/json, text/javascript, */*; q=0.01
        accept-encoding
        gzip, deflate, br, zstd
        accept-language
        en-US,en;q=0.9
        priority
        u=1, i
        referer
        https://sightmap.com/embed/dqw9k06gpo9
        sec-ch-ua
        "Not-A.Brand";v="24", "Chromium";v="146"
        sec-ch-ua-mobile
        ?0
        sec-ch-ua-platform
        "Windows"
        sec-fetch-dest
        empty
        sec-fetch-mode
        cors
        sec-fetch-site
        same-origin
        sec-fetch-storage-access
        active
        user-agent
        Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36
        x-requested-with
        XMLHttpRequest
    '''

    # request info
    url = "https://sightmap.com/app/api/v1/rkwnqrz8wd2/sightmaps/41372"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://sightmap.com/embed/dqw9k06gpo9",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/146.0.0.0 Safari/537.36"
        ),
        "X-Requested-With": "XMLHttpRequest",
    }

    # make the request
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # return the JSON data
    return response.json()


def parse_unit_data(data: dict[str, Any]) -> AvailableApartmentUnit:
    available_now = data['display_available_on'] == 'Available Now'
    return AvailableApartmentUnit(
        int(data['unit_number']),
        float(data['price']),
        available_now,
        None if available_now else date.strptime(data['available_on'], '%Y-%m-%d')
    )


def get_apartment_data() -> dict:
    # make the request
    raw_data = fetch_raw_apartment_data()

    # we expect (and only support) a dictionary as the return data
    if not isinstance(raw_data, dict):
        raise TypeError(f'Expected a dictionary from the request;, but got a {type(raw_data)}')

    # parse the raw data
    parsed_data = list()
    for unit in raw_data['data']['units']:
        parsed_data.append(parse_unit_data(unit))

    # return data
    return {'raw': raw_data, 'parsed': parsed_data}


def main() -> None:
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate
    from pprint import pprint
    import sqlite3

    conn = sqlite3.connect('lease_info.db')

    # TODO: finish
    db.init_app(app)
    migrate.init_app(app, db)

    data = get_apartment_data()
    pprint(data['parsed'])


if __name__ == "__main__":
    main()
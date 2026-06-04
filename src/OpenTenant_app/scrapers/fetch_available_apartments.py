from datetime import date, datetime
from typing import Any
import requests

from ..models.apartment_inventory_snapshot import ApartmentInventorySnapshot
from ..models.apartment_unit_snapshot import ApartmentUnitSnapshot


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


def parse_unit_data(data: dict[str, Any]) -> ApartmentUnitSnapshot:
    return ApartmentUnitSnapshot(
        unit_id=data['id'],
        unit_num=data['unit_number'] if 'unit_number' in data else None,
        price=int(data['price']) if 'price' in data else None,
        sq_footage=int(data['area']) if 'area' in data else None,
        date_available=date.strptime(data['available_on'], '%Y-%m-%d') if 'available_on' in data else None,
    )


def get_apartment_snapshot() -> ApartmentInventorySnapshot:
    # make the request
    raw_data = fetch_raw_apartment_data()

    # we expect (and only support) a dictionary as the return data
    if not isinstance(raw_data, dict):
        raise TypeError(f'Expected a dictionary from the request;, but got a {type(raw_data)}')

    snapshot = ApartmentInventorySnapshot(
        snapshot_time=datetime.now(),
        raw_data=raw_data,
    )

    # parse the raw data
    for unit in raw_data['data']['units']:
        snapshot.units.append(parse_unit_data(unit))

    # return data
    return snapshot


def main() -> None:
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine

    from ..models.model_base import ModelBase

    # expected to be called from the OpenTenant root directory with "uv run -m src.OpenTenant_app.scrapers.fetch_available_apartments"
    db_file = 'sqlite:///instance/app.db'
    engine = create_engine(db_file, future=True)
    ModelBase.metadata.create_all(engine)

    data = get_apartment_snapshot()

    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    with SessionLocal() as session:
        session.add(data)
        session.commit()


if __name__ == "__main__":
    main()
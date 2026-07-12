from datetime import datetime, timezone
from typing import Any
import requests

from ..models.apartments.apartment_inventory_snapshot import ApartmentInventorySnapshot
from ..models.apartments.apartment_unit_snapshot import ApartmentUnitSnapshot
from ..schemas.apartment_snapshot import ApartmentSnapshotSchema


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


def get_apartment_snapshot() -> ApartmentInventorySnapshot:
    # make the request
    raw_data = fetch_raw_apartment_data()

    # Use the schema to validate and parse the raw data
    snapshot_params, parsed_units = ApartmentSnapshotSchema.parse_snapshot(raw_data)

    snapshot = ApartmentInventorySnapshot(
        snapshot_time=datetime.now(timezone.utc),
        **snapshot_params,
    )

    # create model instances from the parsed unit data
    for unit_data in parsed_units:
        snapshot.units.append(ApartmentUnitSnapshot(**unit_data))

    # return data
    return snapshot

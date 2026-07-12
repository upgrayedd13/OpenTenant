from inspect import isfunction

from ..scrapers.fetch_available_apartments import get_apartment_snapshot
from .db import SessionLocal


def run_periodic_scrape() -> None:
    data = get_apartment_snapshot()

    with SessionLocal() as session:
        session.add(data)
        session.commit()


# dictionary to map all function names to functions
function_map = {name: obj for name, obj in globals().items() if isfunction(obj)}

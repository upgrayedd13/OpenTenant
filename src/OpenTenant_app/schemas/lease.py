from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any


class LeaseSchema:
    @staticmethod
    def _parse_decimal(value: Any) -> Decimal | None:
        if value is None or value == 'UNKNOWN' or value == float('nan'):
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None


    @staticmethod
    def _parse_date(value: Any) -> date | None:
        if value is None or value == 'UNKNOWN' or value == '1970-01-01':
            return None
        try:
            return date.fromisoformat(str(value))
        except (ValueError, TypeError):
            return None


    @staticmethod
    def _parse_int(value: Any) -> int | None:
        if value is None or value == 'UNKNOWN':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


    @classmethod
    def serialize(cls, lease: Any) -> dict:
        """Convert a Lease model instance into a dictionary for API responses."""
        return {
            'id': lease.id,
            'unit_number': lease.unit_number,
            'base_monthly_rent': str(lease.base_monthly_rent),
            'monthly_rent_total': str(lease.monthly_rent_total),
            'start_date': lease.start_date.isoformat() if lease.start_date else None,
            'end_date': lease.end_date.isoformat() if lease.end_date else None,
            'path': lease.path,
            'num_occupants': lease.num_occupants,
        }


    @classmethod
    def parse_and_validate(cls, data: dict) -> dict:
        """
        Clean and validate data from the lease parser.
        Returns a dictionary compatible with the Lease model.
        """
        if not isinstance(data, dict):
            raise ValueError('Lease data must be a dictionary')

        # Map parser keys to model keys and apply conversions
        # Parser keys: unit_number, base_rent, monthly_rent_total, 
        # lease_start_date, lease_end_date, residents, etc.
        
        # Required fields for a valid lease
        required = ['unit_number', 'base_rent', 'lease_start_date']
        for field in required:
            if field not in data or data[field] == 'UNKNOWN':
                raise ValueError(f'Missing required lease field: {field}')

        return {
            'unit_number': cls._parse_int(data.get('unit_number')),
            'base_monthly_rent': cls._parse_decimal(data.get('base_monthly_rent')),
            'monthly_rent_total': cls._parse_decimal(data.get('monthly_rent_total')),
            'start_date': cls._parse_date(data.get('lease_start_date')),
            'end_date': cls._parse_date(data.get('lease_end_date')),
            'num_occupants': (cls._parse_int(data.get('num_authorized_adults')) or 0) + (cls._parse_int(data.get('num_authorized_minors')) or 0),
        }

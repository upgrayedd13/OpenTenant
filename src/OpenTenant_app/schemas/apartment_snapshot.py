from datetime import date


class ApartmentSnapshotSchema:
    @staticmethod
    def parse_unit(data: dict) -> dict:
        """
        Clean and validate a single unit's data from the API.
        Returns a dictionary compatible with ApartmentUnitSnapshot.
        """
        if not isinstance(data, dict):
            raise ValueError('Unit data must be a dictionary')

        # Required field: id
        if 'id' not in data:
            raise ValueError('Unit data missing required field: id')

        # Optional fields with type conversion
        # price: int
        price = data.get('price')
        if price is not None:
            try:
                price = int(price)
            except (ValueError, TypeError):
                raise ValueError(f'Invalid price value: {price}')

        # area (sq_footage): int
        area = data.get('area')
        if area is not None:
            try:
                area = int(area)
            except (ValueError, TypeError):
                raise ValueError(f'Invalid area value: {area}')

        # available_on (date_available): date
        available_on = data.get('available_on')
        if available_on is not None:
            try:
                available_on = date.strptime(available_on, '%Y-%m-%d')
            except (ValueError, TypeError):
                raise ValueError(f'Invalid date format for available_on: {available_on}. Expected YYYY-MM-DD')

        # unit_number: int
        unit_num = data.get('unit_number')
        if unit_num is not None:
            try:
                unit_num = int(unit_num)
            except (ValueError, TypeError):
                raise ValueError(f'Invalid unit_number value: {unit_num}')

        return {
            'unit_id': data['id'],
            'unit_num': unit_num,
            'price': price,
            'sq_footage': area,
            'date_available': available_on,
        }


    @classmethod
    def parse_snapshot(cls, raw_data: dict) -> tuple[dict, list[dict]]:
        """
        Validate the top-level API response and parse all units.
        Returns a tuple of (snapshot_data, list_of_parsed_units).
        """
        if not isinstance(raw_data, dict):
            raise ValueError(f'Expected API response to be a dictionary, got {type(raw_data)}')

        if 'data' not in raw_data or 'units' not in raw_data['data']:
            raise ValueError('API response missing expected "data.units" structure')

        units_raw = raw_data['data']['units']
        if not isinstance(units_raw, list):
            raise ValueError(f'Expected "data.units" to be a list, got {type(units_raw)}')

        parsed_units = [cls.parse_unit(unit) for unit in units_raw]

        # Return the raw data for the snapshot model and the cleaned units
        return {'raw_data': raw_data}, parsed_units

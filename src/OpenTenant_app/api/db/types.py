from dataclasses import dataclass
from flask import Response
from typing import Any
import logging

logger = logging.getLogger(__name__)


class WorkerException(Exception):
    def __init__(self, response: tuple[Response, int]) -> None:
        self.response = response



@dataclass(frozen=True)
class CellUpdate:
    id: int
    column: str
    new_value: Any


    @staticmethod
    def json_to_cell_updates(id: int, js_data: dict) -> list['CellUpdate']|None:
        # initial sanity check that we were given a dictionary
        if not isinstance(js_data, dict):
            logger.error(f"Didn't get a dictionary ({js_data})!")
            return None

        return [CellUpdate(id, k, v) for k, v in js_data.items()]



@dataclass(frozen=True)
class TableUpdate:
    table_name: str
    cell_updates: list[CellUpdate]


    @staticmethod
    def json_to_table_update(table_name: str, js_data: dict) -> list['TableUpdate']|None:
        # initial sanity check that we were given a dictionary
        if not isinstance(js_data, dict):
            logger.error(f"Didn't get a dictionary ({js_data})!")
            return None

        updates: list[CellUpdate] = []
        for id, changes in js_data.items():
            # ensure we were given a string or int
            if not isinstance(id, str) and not isinstance(id, int):
                logger.error(f"id isn't a string or int ({id} is a {type(id)})")
                return None

            # get id as an int
            try:
                id = int(id)
            except ValueError:
                logger.error(f'Failed to convert id "{id}" to an int')
                return None

            # convert the JSON to a CellUpdate object
            cells = CellUpdate.json_to_cell_updates(id, changes)
            if cells is None:
                return None

            # add the CellUpdate to our list of cells
            for cell in cells:
                updates.append(cell)

        return TableUpdate(table_name, updates)


    @property
    def ids(self) -> set[int]:
        return {cell.id for cell in self.cell_updates}



@dataclass(frozen=True)
class UpdateRequest:
    tables: list[TableUpdate]


    @staticmethod
    def json_to_update_request(js_data: dict) -> 'UpdateRequest|None':
        # initial sanity check that we were given a dictionary
        if not isinstance(js_data, dict):
            logger.error(f"Didn't get a dictionary ({js_data})!")
            return None

        # we'll eventually return this
        updates: list[TableUpdate] = []

        # iterate through the data and generate our object
        for table_name, changes in js_data.items():
            # ensure we were given a string
            if not isinstance(table_name, str):
                logger.error(f"table_name isn't a string ({table_name} is a {type(table_name)})")
                return None

            # convert the JSON to a TableUpdate object
            table = TableUpdate.json_to_table_update(table_name, changes)
            if table is None:
                return None

            # add the TableUpdate to our list of tables
            updates.append(table)

        return UpdateRequest(updates)

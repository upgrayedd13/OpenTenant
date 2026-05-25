from sqlalchemy import Table, Connection, select
from sqlalchemy.sql.schema import Column
import logging

from ...utils.log_and_abort import log_and_abort
from ...extensions import db, md

from .types import TableUpdate

logger = logging.getLogger(__name__)


def load_table(table_name: str) -> Table:
    try:
        return Table(table_name, md, autoload_with=db.engine)
    except Exception:
        log_and_abort(400, f'Unknown table: {table_name}')


def get_id_col(table: Table) -> Column:
    primary_keys = list(table.primary_key.columns)

    if len(primary_keys) != 1:
        log_and_abort(400, 'Only single-column primary keys supported')

    return primary_keys[0]


def check_keys_exist(conn: Connection, pk_col: Column, keys: set[int]) -> None:
    # if there aren't any keys, there's nothing to do
    if len(keys) == 0:
        return

    # get the primary keys (as a set)
    command = select(pk_col).where(pk_col.in_(keys))
    result = conn.execute(command).fetchall()
    existing_keys = {row[0] for row in result}

    # if there are any keys that aren't in the column, complain
    missing = keys - existing_keys
    if missing:
        log_and_abort(400, f'Invalid IDs: {sorted(missing)}')


def update_table_worker(conn: Connection, update: TableUpdate) -> None:
    # load our table
    table = load_table(update.table_name)
    id_col = get_id_col(table)

    check_keys_exist(conn, id_col, update.ids)

    for cell in update.cell_updates:
        if cell.column not in table.c:
            log_and_abort(400, f'Bad column {cell.col}')

        # make the change
        command = table.update().where(id_col == cell.id).values({cell.column: cell.new_value})
        conn.execute(command)
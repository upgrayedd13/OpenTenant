from sqlalchemy import Table, Connection, select
from sqlalchemy.sql.schema import Column
import logging

from ...utils.log_and_exit import log_and_jsonify
from ...extensions import db, md

from .types import TableUpdate, WorkerException

logger = logging.getLogger(__name__)


def load_table(table_name: str) -> Table:
    try:
        return Table(table_name, md, autoload_with=db.engine)
    except Exception:
        raise WorkerException(log_and_jsonify(f'Unknown table: {table_name}', 400))


def get_id_col(table: Table) -> Column:
    primary_keys = list(table.primary_key.columns)

    if len(primary_keys) != 1:
        raise WorkerException(log_and_jsonify('Only single-column primary keys supported', 400))

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
        raise WorkerException(log_and_jsonify(f'Invalid IDs: {sorted(missing)}', 400))


def update_table_worker(conn: Connection, update: TableUpdate) -> None:
    # load our table and ID column
    table = load_table(update.table_name)
    id_col = get_id_col(table)

    # ensure our keys all exist
    check_keys_exist(conn, id_col, update.ids)

    for cell in update.cell_updates:
        if cell.column not in table.c:
            raise WorkerException(log_and_jsonify(f'Bad column {cell.column}', 400))

        # make the change
        command = table.update().where(id_col == cell.id).values({cell.column: cell.new_value})
        conn.execute(command)
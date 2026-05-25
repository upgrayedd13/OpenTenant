from flask import Blueprint, jsonify, Response, request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
import logging

from ...models.user_role import minimum_user_role, UserRole
from ...utils.log_and_abort import log_and_abort
from ...extensions import db

from .db_management import update_table_worker, load_table
from .types import UpdateRequest

db_api_bp = Blueprint('db_api', __name__, url_prefix='/api/db')
logger = logging.getLogger(__name__)


@db_api_bp.route('/tables', methods=['GET'])
@minimum_user_role(UserRole.SUPER_ADMIN)
def get_tables() -> Response:
    tables = inspect(db.engine).get_table_names()
    logger.debug(f'tables: {tables}')
    return jsonify({'tables': tables})


@db_api_bp.route('/table/<string:table_name>', methods=['GET'])
@minimum_user_role(UserRole.SUPER_ADMIN)
def get_table_content(table_name: str) -> Response | tuple[Response, int]:
    # load this table
    table = load_table(table_name)

    # get the rows
    with db.engine.connect() as conn:
        rows = conn.execute(table.select()).fetchall()
    rowData = [dict(row._mapping) for row in rows]
    
    # get the types of the columns
    typeData = {col.name: str(col.type.__class__.__name__) for col in table.columns}

    # return everything
    logger.info(f'rows: {rows}')
    return jsonify({'rows': rowData, 'types': typeData})


@db_api_bp.route('/tables', methods=['POST'])
@minimum_user_role(UserRole.SUPER_ADMIN)
def update_tables() -> Response | tuple[Response, int]:
    # get the changes in the request JSON
    payload: dict = request.get_json(force=True)
    changes: dict|None = payload.get('changes')
    if changes is None:
        log_and_abort(400, 'Bad payload')
    logger.info(f'Requested changes: {changes}')

    # convert the raw JSON to an UpdateRequest object
    update_req = UpdateRequest.json_to_update_request(changes)
    if update_req is None:
        log_and_abort(400, "Failed to parse raw JSON")

    try:
        # update each table in the DB
        with db.engine.begin() as conn:
            for table_update in update_req.tables:
                update_table_worker(conn, table_update)

    except SQLAlchemyError as e:
        log_and_abort(500, str(e))

    return jsonify({'status': 'ok'})
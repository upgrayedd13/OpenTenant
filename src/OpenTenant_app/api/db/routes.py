from flask import Blueprint, jsonify, Response, request, send_file
from sqlalchemy.exc import SQLAlchemyError, ResourceClosedError
from sqlalchemy import inspect, text, Table, CheckConstraint
from io import BytesIO
import pandas as pd
import logging

from ...schemas.db_management import UpdateRequest, WorkerException
from ...models.user_role import minimum_user_role, UserRole
from ...utils.log_and_exit import log_and_jsonify
from ...extensions import db

from .db_management import update_table_worker, load_table

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
    try:
        table = load_table(table_name)
    except WorkerException as e:
        return e.response

    # get the types of the columns
    info = get_column_info(table)

    # get the rows
    with db.engine.connect() as conn:
        rows = conn.execute(table.select()).fetchall()
    info['rows'] = [dict(row._mapping) for row in rows]

    info['types'] = {col.name: str(col.type.__class__.__name__) for col in table.columns}

    # return everything
    logger.debug(info)
    return jsonify(info)


def get_column_info(table: Table) -> dict:
    cols = dict()
    for col in table.columns:
        if col.default is None:
            default = None
        elif callable(col.default.arg):
            default = '<dynamic>'
        else:
            try:
                default = str(col.default.arg)
            except Exception:
                default = '<unknown>'
        
        cols[col.name] = {
            'type': col.type.__class__.__name__,
            'nullable': col.nullable,
            'primary_key': col.primary_key,
            'default': default,
            'foreign_keys': [str(fk.target_fullname) for fk in col.foreign_keys],
        }

    constraints = []
    for constraint in table.constraints:
        if isinstance(constraint, CheckConstraint):
            constraints.append({'name': constraint.name, 'sqltext': str(constraint.sqltext)})

    return {'columns': cols, 'constraints': constraints}


@db_api_bp.route('/tables', methods=['POST'])
@minimum_user_role(UserRole.SUPER_ADMIN)
def update_tables() -> Response | tuple[Response, int]:
    # get the changes in the request JSON
    payload: dict = request.get_json(force=True)
    changes: dict|None = payload.get('changes')
    if changes is None:
        return log_and_jsonify('Bad payload', 400)
    logger.info(f'Requested changes: {changes}')

    # convert the raw JSON to an UpdateRequest object
    update_req = UpdateRequest.json_to_update_request(changes)
    if update_req is None:
        return log_and_jsonify('Failed to parse raw JSON', 400)

    try:
        # update each table in the DB
        with db.engine.begin() as conn:
            for table_update in update_req.tables:
                update_table_worker(conn, table_update)

    except WorkerException as e:
        return e.response

    except SQLAlchemyError as e:
        return log_and_jsonify(str(e), 500)

    return jsonify({'status': 'ok'})


@db_api_bp.route('/query', methods=['POST'])
@minimum_user_role(UserRole.SUPER_ADMIN)
def run_query() -> Response | tuple[Response, int]:
    query = request.json.get('query')
    if not query:
        return log_and_jsonify('No query provided', 400)
    logger.info(f'Query: {query}')

    try:
        with db.engine.connect() as conn:
            result = conn.execute(text(query))
            conn.commit()
            
            try:
                rows = result.fetchall()
                types = {desc[0]: desc[1].__name__ if desc[1] else 'unknown' for desc in result.cursor.description} if result.cursor.description else {}
                return jsonify({'rows': [dict(row._mapping) for row in rows], 'types': types})
            
            except ResourceClosedError:
                return jsonify({'rows': [], 'types': {}})

    except Exception as e:
        return log_and_jsonify(str(e), 500)


@db_api_bp.route('/export/<string:table_name>', methods=['GET'])
@minimum_user_role(UserRole.SUPER_ADMIN)
def export(table_name: str) -> Response | tuple[Response, int]:
    df = pd.read_sql_table(table_name, db.engine)

    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name=f'{table_name}.csv', mimetype='text/csv')
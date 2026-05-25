from flask import Blueprint, jsonify, Response, request
from sqlalchemy import inspect, Table, MetaData
import logging

from ...extensions import db
from ...models.user_role import minimum_user_role, UserRole


db_api_bp = Blueprint('db_api', __name__, url_prefix='/api/db')
logger = logging.getLogger(__name__)



@db_api_bp.route('/tables', methods=['GET'])
@minimum_user_role(UserRole.SUPER_ADMIN)
def get_tables() -> Response:
    inspector = inspect(db.engine)
    tables = dict()

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        tables[table_name] = [{'name': col['name'], 'type': str(col['type'])} for col in columns]

    logger.debug(f'tables: {tables}')
    return jsonify({'tables': tables})


@db_api_bp.route('/table/<string:table_name>', methods=['GET'])
@minimum_user_role(UserRole.SUPER_ADMIN)
def get_table_content(table_name: str) -> Response | tuple[Response, int]:
    inspector = inspect(db.engine)
    if table_name not in inspector.get_table_names():
        return jsonify({'error': f'{table_name} is not in database'}), 400

    table = Table(table_name, MetaData(), autoload_with=db.engine)
    with db.engine.connect() as conn:
        rows = conn.execute(table.select()).fetchall()

    logger.debug(f'rows: {rows}')
    return jsonify({'rows': [dict(row._mapping) for row in rows]})
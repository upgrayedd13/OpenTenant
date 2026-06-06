from flask import Blueprint, render_template, jsonify, request, abort, Response
from datetime import datetime, timezone, timedelta
import logging

from ...models.user_role import minimum_user_role, UserRole
from ...models.calendar_event import CalendarEvent
from ...utils.log_and_exit import log_and_jsonify


calendar_api_bp = Blueprint('calendar_api', __name__, url_prefix='/api/calendar')
logger = logging.getLogger(__name__)


@calendar_api_bp.route('/events', methods=['GET'])
def get_calendar_events() -> Response | tuple[Response, int]:
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    tz = request.args.get("tz", type=int)

    # sanity check inputs
    if not (0 < month < 12):
        return log_and_jsonify(f'Got bad month ({month})', 400)
    elif not (-24 < tz / 60 < 24):
        return jsonify(f'Got bad timezone offset ({tz})', 400)

    tz_info = timezone(timedelta(minutes=tz))
    start = datetime(year, month, 1, tzinfo=tz_info)
    end = datetime(year, month + 1, 1, 23, 59, 59, tzinfo=tz_info)

    events = CalendarEvent.get_events(start, end)
    return jsonify(events)


@calendar_api_bp.route('/events', methods=['POST'])
@minimum_user_role(UserRole.ADMIN)
def add_calendar_event() -> Response | tuple[Response, int]:
    data = request.get_json(silent=True)
    if not data:
        log_and_jsonify('Invalid JSON', 400)

    try:
        CalendarEvent.from_dict(data)
    except ValueError as e:
        log_and_jsonify(str(e), 400)

    return jsonify()

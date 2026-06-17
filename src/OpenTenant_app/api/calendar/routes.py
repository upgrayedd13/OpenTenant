from flask import Blueprint, jsonify, request, Response
from datetime import datetime, timezone, timedelta
import logging

from ...models.user_role import minimum_user_role, UserRole
from ...models.calendar_event import CalendarEvent
from ...utils.log_and_exit import log_and_jsonify
from ...extensions import db


calendar_api_bp = Blueprint('calendar_api', __name__, url_prefix='/api/calendar')
logger = logging.getLogger(__name__)


@calendar_api_bp.route('/events', methods=['GET'])
def get_calendar_events() -> Response | tuple[Response, int]:
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    # sanity check inputs
    if not month or not year or not (0 < month <= 12):
        return log_and_jsonify(f'Got bad year/month ({year}, {month})', 400)

    start = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    end -= timedelta(microseconds=1)

    events = CalendarEvent.get_events(start, end)
    return jsonify(events)


@calendar_api_bp.route('/events', methods=['POST'])
@minimum_user_role(UserRole.ADMIN)
def add_calendar_event() -> Response | tuple[Response, int]:
    data = request.get_json(silent=True)
    if not data:
        return log_and_jsonify('Invalid JSON', 400)

    try:
        ce = CalendarEvent.from_dict(data)
        db.session.add(ce)
        db.session.commit()
    except Exception as e:
        return log_and_jsonify(str(e), 400)

    return jsonify()

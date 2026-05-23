from flask import Blueprint, render_template, jsonify, request, abort
from datetime import datetime, timezone, timedelta
import logging

from ...models.calendar_event import CalendarEvent
from ...models.calendar_event_exception import CalendarEventException
from ...extensions import db


calendar_api_bp = Blueprint('calendar_api', __name__, url_prefix='/api/calendar')
logger = logging.getLogger(__name__)



@calendar_api_bp.route('/events', methods=['GET'])
def get_calendar_events() -> tuple[dict, int]:
    year = int(request.args["year"])
    month = int(request.args["month"])
    tz = int(request.args["tz"])

    # sanity check inputs
    if not (0 < month < 12):
        return jsonify({'error': f'Got bad month ({month})'}), 400
    elif not (-24 < tz / 60 < 24):
        return jsonify({'error': f'Got bad timezone offset ({tz})'}), 400

    print(tz)
    print(request.args['tz'])
    tz_info = timezone(timedelta(minutes=tz))
    start = datetime(year, month, 1, tzinfo=tz_info)
    end = datetime(year, month + 1, 1, 23, 59, 59, tzinfo=tz_info)

    events = CalendarEvent.get_events(start, end)
    return jsonify(events), 200


@calendar_api_bp.route('/events', methods=['POST'])
def add_calendar_event() -> None:
    pass
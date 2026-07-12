from flask import Blueprint, jsonify, request, Response
from datetime import datetime, timezone, timedelta
import logging

from ...models.calendar.calendar_event_exception import CalendarEventException
from ...models.user.user_role import minimum_user_role, UserRole
from ...models.calendar.calendar_event import CalendarEvent
from ...utils.log_and_exit import log_and_jsonify
from ...extensions import db


calendar_api_bp = Blueprint('calendar_api', __name__, url_prefix='/api/calendar')
logger = logging.getLogger(__name__)


@calendar_api_bp.route('/events', methods=['GET'])
def get_calendar_events() -> Response | tuple[Response, int]:
    start_str = request.args.get("start")
    end_str = request.args.get("end")

    if not start_str or not end_str:
        return log_and_jsonify('Missing start or end date parameters', 400)

    try:
        # Parse ISO strings and ensure they are treated as UTC
        start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
    except Exception as e:
        return log_and_jsonify(f'Invalid date format: {str(e)}', 400)

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


@calendar_api_bp.route('/events/<int:event_id>', methods=['DELETE'])
@minimum_user_role(UserRole.ADMIN)
def delete_calendar_event(event_id: int) -> Response | tuple[Response, int]:
    data = request.get_json(silent=True) or {}
    scope = data.get('scope')
    if scope not in ('single', 'series'):
        return log_and_jsonify(f'Invalid or missing scope "{scope}" (expected "single" or "series")', 400)

    event = db.session.get(CalendarEvent, event_id)
    if event is None:
        return log_and_jsonify(f'No event with id {event_id}', 404)

    # A non-repeating event only has one occurrence, so "single" and
    # "series" both just mean deleting the event outright.
    if scope == 'series' or event.rrule is None:
        db.session.delete(event)
    else:
        occurrence_start = data.get('occurrence_start')
        if not occurrence_start:
            return log_and_jsonify('Missing occurrence_start for single-occurrence delete', 400)

        try:
            occ_dt = datetime.fromisoformat(str(occurrence_start).replace('Z', '+00:00'))
            if occ_dt.tzinfo is None:
                raise ValueError('occurrence_start must include timezone info')
        except Exception:
            return log_and_jsonify('Invalid occurrence_start format', 400)
        event.exceptions.append(CalendarEventException(exception_date=occ_dt.astimezone(timezone.utc)))

    db.session.commit()
    return jsonify()


@calendar_api_bp.route('/events/<int:event_id>', methods=['PUT'])
@minimum_user_role(UserRole.ADMIN)
def update_calendar_event(event_id: int) -> Response | tuple[Response, int]:
    data = request.get_json(silent=True)
    if not data:
        return log_and_jsonify('Invalid JSON', 400)

    event = db.session.get(CalendarEvent, event_id)
    if event is None:
        return log_and_jsonify(f'No event with id {event_id}', 404)

    try:
        # Handle date parsing for start_time and end_time
        tz_name = data.get('timezone')
        if not tz_name:
            # If we are updating times, we MUST have a timezone to parse them correctly
            if 'start_time' in data or 'end_time' in data:
                return log_and_jsonify('Timezone is required when updating start_time or end_time', 400)
        else:
            from zoneinfo import ZoneInfo
            tz = ZoneInfo(tz_name)
            
            if 'start_time' in data:
                st_str = data['start_time']
                # Parse as naive, then attach timezone, then normalize to UTC
                st_naive = datetime.fromisoformat(st_str)
                data['start_time'] = st_naive.replace(tzinfo=tz).astimezone(timezone.utc)
            
            if 'end_time' in data:
                et_str = data['end_time']
                et_naive = datetime.fromisoformat(et_str)
                data['end_time'] = et_naive.replace(tzinfo=tz).astimezone(timezone.utc)

        # Update event attributes from the provided data
        for key, value in data.items():
            if hasattr(event, key) and key != 'timezone':
                # Prevent assigning None to collection relationships (like 'exceptions')
                if key == 'exceptions' and value is None:
                    value = []
                setattr(event, key, value)
        
        db.session.commit()
    except Exception as e:
        return log_and_jsonify(str(e), 400)

    return jsonify()

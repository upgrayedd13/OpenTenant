from flask import Blueprint, jsonify, Response
import logging

from ...models.elevator import Elevator
from ...extensions import db
from sqlalchemy import select

elevator_api_bp = Blueprint('elevator_api', __name__, url_prefix='/api/elevator')
logger = logging.getLogger(__name__)


@elevator_api_bp.route('/status', methods=['GET'])
def get_elevator_status() -> Response:
    result = db.session.execute(select(Elevator).order_by(Elevator.car_number))
    elevators = result.scalars().all()
    
    if not elevators:
        logger.warning('No elevators found in database')
        return jsonify({'error': 'No elevators configured'}), 404
    
    elevator_list = []
    for elevator in elevators:
        status_value = elevator.status.value if hasattr(elevator.status, 'value') else elevator.status
        elevator_list.append({
            'car_number': elevator.car_number,
            'status': status_value,
            'comment': elevator.comment,
            'last_updated': elevator.updated_at.isoformat() if elevator.updated_at else None
        })
    
    return jsonify(elevator_list)

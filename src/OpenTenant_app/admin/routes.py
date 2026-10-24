from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
import logging

from ..models.user_role import *
from ..models.elevator import Elevator, ElevatorStatus
from ..models.elevator_history import ElevatorStatusHistory
from ..extensions import db
from .subforms.bot_account_form import BotAccountForm
from .forms import ElevatorStatusForm
from sqlalchemy import select


admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates', static_folder='static', static_url_path='/admin/static')
logger = logging.getLogger(__name__)


@admin_bp.route('/admin')
@minimum_user_role(UserRole.ADMIN)
def admin():
    return render_template('admin/admin.html')


@admin_bp.route('/admin/modify-calendar')
@minimum_user_role(UserRole.ADMIN)
def modify_calendar():
    return render_template('admin/modify_calendar.html')


@admin_bp.route('/db-edit-tool')
@minimum_user_role(UserRole.SUPER_ADMIN)
def db_edit_tool():
    return render_template('admin/db_edit_tool.html')


@admin_bp.route('/create-bot-account', methods=['GET', 'POST'])
@minimum_user_role(UserRole.SUPER_ADMIN)
def create_bot_account():
    form = BotAccountForm()
    
    if form.validate_on_submit():
        user = form.create_user()
        db.session.add(user)
        db.session.commit()
        
        flash('Bot account created successfully!', 'success')
        return redirect(url_for('account.login'))
    
    return render_template('admin/create_bot_account.html', form=form)


@admin_bp.route('/elevator-status', methods=['GET', 'POST'])
@minimum_user_role(UserRole.ADMIN)
def elevator_status():
    form = ElevatorStatusForm()
    
    if request.method == 'GET':
        elevators = db.session.execute(select(Elevator).order_by(Elevator.car_number)).scalars().all()
        if elevators:
            for i, elevator in enumerate(elevators, 1):
                form_vars = {
                    f'car_{i}_status': elevator.status.value if hasattr(elevator.status, 'value') else elevator.status,
                    f'car_{i}_comment': elevator.comment or ''
                }
                for key, value in form_vars.items():
                    setattr(form, key, value)
    
    if form.validate_on_submit():
        update_all = request.form.get('update_all')
        
        if update_all:
            car_fields = ['1', '2', '3']
        else:
            update_car = request.form.get('update_car')
            car_fields = [update_car] if update_car else []
        
        if not car_fields:
            flash('Please select a car to update.', 'error')
            return redirect(url_for('admin.elevator_status'))
        
        for car_num in car_fields:
            status_value = form[f'car_{car_num}_status'].data
            comment = form[f'car_{car_num}_comment'].data.strip() if form[f'car_{car_num}_comment'].data else None
            
            if not status_value:
                continue
            
            elevator = db.session.execute(select(Elevator).filter_by(car_number=int(car_num))).scalar_one_or_none()
            
            if elevator:
                old_status = elevator.status.value if hasattr(elevator.status, 'value') else elevator.status
                old_comment = elevator.comment
                
                if old_status != status_value or old_comment != comment:
                    history = ElevatorStatusHistory(
                        elevator_id=elevator.id,
                        car_number=int(car_num),
                        old_status=old_status,
                        new_status=status_value,
                        changed_by_user_id=current_user.id,
                        comment=comment if comment else None
                    )
                    db.session.add(history)
                
                elevator.status = ElevatorStatus(status_value)
                elevator.comment = comment if comment else None
            else:
                elevator = Elevator(
                    car_number=int(car_num),
                    status=ElevatorStatus(status_value),
                    comment=comment if comment else None
                )
                db.session.add(elevator)
                
                history = ElevatorStatusHistory(
                    elevator_id=elevator.id,
                    car_number=int(car_num),
                    old_status=None,
                    new_status=status_value,
                    changed_by_user_id=current_user.id,
                    comment=comment if comment else None
                )
                db.session.add(history)
        
        db.session.commit()
        flash('Elevator statuses updated successfully!', 'success')
        return redirect(url_for('admin.elevator_status'))
    
    return render_template('admin/elevator_status.html', form=form)

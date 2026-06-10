from flask import Blueprint, render_template
import logging

from ..models.user_role import *


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

from flask import Blueprint, render_template

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates', static_folder='static', static_url_path='/admin/static')


@admin_bp.route("/admin")
def admin():
    return render_template("admin/admin.html")

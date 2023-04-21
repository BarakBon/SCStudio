from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user

views = Blueprint('views', __name__)


@views.route('/equipment')
@login_required
def equipment():
    
    return render_template("equipment.html", user=current_user)



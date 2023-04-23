from flask import Blueprint, render_template, request, flash, jsonify
from app.models import Equipment

views = Blueprint('views', __name__)


@views.route('/equipment', methods=['GET', 'POST'])
@login_required
def equipment():
    equipment_list = Equipment.query.all()
    return render_template("equipment.html", user=current_user, equipment_list=equipment_list)
    

@views.route('/Borrowing_Equipment', methods=['GET', 'POST'])
def Borrowing_Equipment():
    
    return render_template("Borrowing_Equipment.html")

@views.route('/equipment_failure', methods=['GET', 'POST'])
def equipment_failure():
    
    return render_template("equipment_failure.html")


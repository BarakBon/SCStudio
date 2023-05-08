import dbm
from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from flask import render_template
from app.models import Equipment

views = Blueprint('views', __name__)


@views.route('/equipment')
@login_required
def equipment():
    # Filter equipment by Type, model and Available
    type_filter = request.args.get('type')
    model_filter = request.args.get('model')
    available_filter = request.args.get('available')
    query = Equipment.query
    if type_filter:
        query = query.filter_by(Type=type_filter)
    if model_filter:
        query = query.filter_by(model=model_filter)
    if available_filter:
        query = query.filter_by(available=available_filter)
    equipment_list = query.all()

    return render_template("equipment.html", user=current_user, equipment_list=equipment_list)




@views.route('/Borrowing_Equipment', methods=['GET', 'POST'])
@login_required
def Borrowing_Equipment():
   
    return render_template("Borrowing_Equipment.html", equipment=equipment, user=current_user)



@views.route('/equipment_failure', methods=['GET', 'POST'])
def equipment_failure():
    
    return render_template("equipment_failure.html")


@views.route('/Fixing_equipment', methods=['GET', 'POST'])
def Fixing_equipment():
    
    return render_template("Fixing_equipment.html")


@views.route('/borrowed_equipment', methods=['GET', 'POST'])
def borrowed_equipment():
    
    return render_template("borrowed_equipment.html")


@views.route('/borrowing_history', methods=['GET', 'POST'])
def borrowing_history():
    
    return render_template("borrowing_history.html")


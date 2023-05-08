import dbm
from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from flask import render_template
from app.models import *

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
        query = query.filter_by(status=available_filter)
    equipment_list = query.all()
    print(current_user.userType)

    return render_template("equipment.html", user=current_user, equipment_list=equipment_list)




@views.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
   
    return render_template("borrow.html", equipment=equipment, user=current_user)


@views.route('/fault_report', methods=['GET', 'POST'])
def fault_report():
    
    return render_template("fault_report.html", user=current_user)


@views.route('/Fixing_equipment', methods=['GET', 'POST'])
def Fixing_equipment():
    
    return render_template("Fixing_equipment.html" , user=current_user)


@views.route('/borrowed_equipment', methods=['GET', 'POST'])
def borrowed_equipment():
    
    return render_template("borrowed_equipment.html" , user=current_user)


@views.route('/user_borrowing', methods=['GET', 'POST'])
def user_borrowing():
    query = Borrow.query
    query = query.filter_by(borrower=current_user.id)
    borrows = query.all()
    return render_template("user_borrowing.html", borrows=borrows , user=current_user)


@views.route('/rooms', methods=['GET', 'POST'])
def rooms():
    
    return render_template("rooms.html", user=current_user)
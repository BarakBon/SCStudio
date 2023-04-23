import dbm
from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from flask import render_template
from mysqlx import DbDoc
from app.models import Equipment,Borrowed_Equipment

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
        query = query.filter_by(Available=available_filter)
    equipment_list = query.all()

    return render_template("equipment.html", user=current_user, equipment_list=equipment_list)




@views.route('/Borrowing_Equipment', methods=['GET', 'POST'])
@login_required
def Borrowing_Equipment():
    if request.method == 'POST':
        equipment = request.form['equipment']
        pickup_date = request.form['pickup-date']
        return_date = request.form['return-date']
        user_id = current_user.id

        borrowed_equipment = Borrowed_Equipment(equipment=equipment,
                                                pickup_date=pickup_date, return_date=return_date, user_id=user_id)
        DbDoc.session.add(borrowed_equipment)
        dbm.session.commit()

        flash('Equipment borrowed successfully!', 'success')
        return redirect(url_for('borrow_equipment', user=current_user))

    equipment = Equipment.query.with_entities(Equipment.Type, Equipment.model).all()
    return render_template("Borrowing_Equipment.html", equipment=equipment, user=current_user)



@views.route('/equipment_failure', methods=['GET', 'POST'])
def equipment_failure():
    
    return render_template("equipment_failure.html")

@views.route('/Fixing_equipment', methods=['GET', 'POST'])
def Fixing_equipment():
    
    return render_template("Fixing_equipment.html")



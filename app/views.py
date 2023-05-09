import dbm
from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from flask import render_template
from app.models import *
from dateutil import parser

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
    if request.method == 'POST':
        type = request.form.get('type')
        model = request.form.get('model')
        from_date = request.form.get('pickup-date')
        to_date = request.form.get('return-date')
        if type != "" and model:
            equ = Equipment.query.filter_by(Type=type).filter_by(model=model).first()
            try:
                from_d = parser.parse(from_date)
                to_d = parser.parse(to_date)
                diff = to_d - from_d
                if diff.days <= equ.max_time :
                    equ = Equipment.query.filter_by(Type=type).filter_by(model=model).filter_by(status="available").first()
                    if equ:
                        new_order = Borrow(borrower=current_user.id, aq_serial=equ.serial_number, borrow_date=from_d.strftime('%d/%m/%Y'), return_date=from_d.strftime('%d/%m/%Y'), return_status="no")
                        db.session.add(new_order)
                        equ.status = "borrowed"
                        db.session.commit()
                        type= ""
                        flash('!הזמנתך נקלטה בהצלחה', category='success')
                        return redirect(url_for('views.borrowing_history'))
                    else:
                       type= ""
                       flash('!אין מוצר זמין להשאלה', category='error') 
                else:
                    type= ""
                    flash('!כמות ימים גבוהה מידי למוצר זה', category='error')
            except:
                type= ""
                pass 
    type= ""                       
    return render_template("borrow.html",  user=current_user)

@views.route('/fault_report', methods=['GET', 'POST'])
def fault_report():
    
    return render_template("fault_report.html", user=current_user)


@views.route('/Fixing_equipment', methods=['GET', 'POST'])
def Fixing_equipment():
    
    return render_template("Fixing_equipment.html" , user=current_user)


@views.route('/borrowed_equipment', methods=['GET', 'POST'])
def borrowed_equipment():
    query = Borrow.query
    borrows = query.all()
    return render_template("borrowed_equipment.html" ,  borrows=borrows ,user=current_user)


@views.route('/user_borrowing', methods=['GET', 'POST'])
def user_borrowing():
    query = Borrow.query
    query = query.filter_by(borrower=current_user.id)
    borrows = query.all()
    return render_template("user_borrowing.html", borrows=borrows , user=current_user)


@views.route('/rooms', methods=['GET', 'POST'])
def rooms():
    
    return render_template("rooms.html", user=current_user)



@views.route('/adding_equipment', methods=['GET', 'POST'])
def adding_equipment():
    # Check if the user is logged in and exists
    if current_user.is_authenticated:
        user = current_user
    else:
        user = None

    if request.method == 'POST':
        # Get the form data from the request object
        equipment_type = request.form.get('equipment')
        model = request.form.get('model')
        serial_number = request.form.get('serialNumber')
        max_time = request.form.get('maxTime')
        
        # Create a new Equipment object
        new_equipment = Equipment(Type=equipment_type, model=model, serial_number=serial_number, status='available', max_time=max_time)
        
        # Add the new equipment to the database
        db.session.add(new_equipment)
        db.session.commit()
        flash('הציוד נוסף בהצלחה!', category='success')
        # Redirect the user to the equipment list page
        return redirect(url_for('views.equipment'))
    
    # Render the add equipment template
    return render_template('adding_equipment.html', user=user)





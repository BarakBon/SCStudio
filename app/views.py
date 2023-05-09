import dbm
from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from flask import render_template
from app.models import *
from dateutil import parser
from datetime import datetime
from collections import namedtuple

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

    return render_template("equipment.html", user=current_user, equipment_list=equipment_list)




@views.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
    if request.method == 'POST':
        type = request.form.get('type')
        model = request.form.get('model')
        from_date = request.form.get('pickup-date')
        to_date = request.form.get('return-date')
        if type != "" and model != "":
            equipment_list = Equipment.query.filter_by(Type=type).filter_by(model=model).filter(Equipment.status !="faulty").all()
            try:
                from_d = parser.parse(from_date)
                to_d = parser.parse(to_date)
                diff = to_d - from_d
                Range = namedtuple('Range', ['start', 'end'])
                #chosen_range = Range(start=from_d, end=to_d)
                for aquip in equipment_list:
                    borrows_list = Borrow.query.filter_by(aq_serial=aquip.serial_number).filter_by(return_status="no").all()
                    overlaped = False
                    for borrow in borrows_list:
                        bor_from_d = datetime.strptime(borrow.borrow_date, '%d/%m/%Y')
                        bor_to_d = datetime.strptime(borrow.return_date, '%d/%m/%Y')
                        if (from_d <= bor_to_d) and (to_d >= bor_from_d):
                            overlaped = True
                            break                        
                    if diff.days <= aquip.max_time:
                        if overlaped == False:
                            new_order = Borrow(borrower=current_user.id, aq_serial=aquip.serial_number, borrow_date=from_d.strftime('%d/%m/%Y'), return_date=to_d.strftime('%d/%m/%Y'), return_status="no")
                            db.session.add(new_order)
                            #equ.status = "borrowed" 
                            db.session.commit()
                            type= ""
                            flash('!הזמנתך נקלטה בהצלחה', category='success')
                            return redirect(url_for('views.user_borrowing'))                        
                    else:
                        type= ""
                        flash('!כמות ימים גבוהה מידי למוצר זה', category='error')
                        break
                type= ""
                flash('!אין מוצר זמין להשאלה', category='error') 
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
    
    return render_template("borrowed_equipment.html" , user=current_user)


@views.route('/user_borrowing', methods=['GET', 'POST'])
def user_borrowing():
    query = Borrow.query
    query = query.filter_by(borrower=current_user.id)
    borrows = query.all()
    return render_template("user_borrowing.html", borrows=borrows , user=current_user)


@views.route('/rooms', methods=['GET', 'POST'])
@login_required
def rooms():
    if request.method == 'POST':
        pass
    return render_template("rooms.html", user=current_user)
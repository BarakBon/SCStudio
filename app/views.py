import dbm
from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from flask import render_template
from app.models import *
from dateutil import parser
from datetime import datetime
from collections import namedtuple

views = Blueprint('views', __name__, template_folder='templates')


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
                            #TODO: add borrow notification
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
    aq_serial = request.args.get('aq_serial')
    item_model = request.args.get('item_model')
    item_type = request.args.get('item_type')
    #TODO: add notification of report on post request
    return render_template("fault_report.html", user=current_user,aq_serial=aq_serial, item_model=item_model, item_type=item_type)


@views.route('/Fixing_equipment', methods=['GET', 'POST'])
def Fixing_equipment():
    
    return render_template("Fixing_equipment.html" , user=current_user)


@views.route('/borrowed_equipment', methods=['GET', 'POST'])
@login_required
def borrowed_equipment():
    borrows = Borrow.query.filter_by(return_status='no').all()
    all_borrowed = []
    for borrow in borrows:
        if borrow.item.status == 'borrowed':
            all_borrowed.append(borrow)
    
    if request.method == 'POST':
        borrow_id = request.form.get('borrow_id')
        borrow = Borrow.query.get(borrow_id)
        equipment = Equipment.query.filter_by(serial_number=borrow.aq_serial).first()
        if equipment and borrows:
            equipment.status = 'available'
            borrow.return_status='yes'
            db.session.commit()
            flash('Equipment returned successfully', 'success')
            return redirect(url_for('views.equipment'))
        else:
            flash('Equipment not found', 'error')
    return render_template("borrowed_equipment.html", borrows=all_borrowed, user=current_user)


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
        room_type = request.form.get('type')
        date = request.form.get('date')
        time = request.form.get('time')        
        if date != "" and time != "":
            try:
                d = parser.parse(date)  
                book = Room_Book.query.filter_by(date=d.strftime('%d/%m/%Y')).filter_by(start_hour=time).first()
                if not book:
                    new_room_book = Room_Book(type=room_type, inviter=current_user.id, date=d.strftime('%d/%m/%Y'), start_hour=time)
                    db.session.add(new_room_book)
                    db.session.commit()
                    date = ""
                    flash('!הזמנתך נקלטה בהצלחה', category='success')
                    return redirect(url_for('views.user_borrowing'))
                else:
                    date = ""
                    flash('החדר תפוס בזמן זה', category='error')       
            except:
                date = ""
                pass
    date = ""                    
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


@views.route('/eq_transfer', methods=['GET', 'POST'])
@login_required
def eq_transfer():
    borrows = Borrow.query.all()
    borrows = Borrow.query.filter_by(return_status='no').all()
    today = datetime.now().date()  # get today's date
    borrows_today = []  # list to store borrows with borrow_date = today's date
    for borrow in borrows:
        borrow_date = datetime.strptime(borrow.borrow_date, '%d/%m/%Y').date()  # convert borrow date string to datetime object
       
        if borrow_date == today and borrow.return_status=='no' and borrow.item.status=='available':
            borrows_today.append(borrow)

    if request.method == 'POST':
        borrow_id = request.form.get('borrow_id')
        borrow = Borrow.query.get(borrow_id)
        equipment = Equipment.query.filter_by(serial_number=borrow.aq_serial).first()
        if equipment:
            equipment.status = 'borrowed'
            #TODO: add new notification for the return date (maybe day before)
            db.session.commit()
            flash('Equipment returned successfully', 'success')
            return redirect(url_for('views.equipment'))

    return render_template("eq_transfer.html", user=current_user, borrows=borrows_today)



@views.route('/notifications/count', methods=['GET'])
@login_required
def notifications_count():
    today = datetime.now().date().strftime("%d/%m/%Y")
    count = 0
    if current_user.userType == "Manager":
        count = Notification.query.filter_by(date=today).filter_by(is_read="no").count()
    else:
        count = Notification.query.filter_by(date=today).filter_by(user=current_user.id).filter_by(is_read="no").count()
    return jsonify({'count': count})

@views.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    return render_template("notifications.html", user=current_user)

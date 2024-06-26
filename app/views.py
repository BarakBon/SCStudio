import dbm
from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from flask import render_template
from app.models import *
from dateutil import parser
from datetime import datetime
from collections import namedtuple
from sqlalchemy import or_
from sqlalchemy import func
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, flash



views = Blueprint('views', __name__, template_folder='templates')

eq_dict = {'Camera':'מצלמה', 'Rec':'מיקרופון', 'Apple':'מוצר אפל', 'Tripod':'חצובה', 
           'Projectors':'פרוזקטור', 'Cables':'כבל', 'Lights':'תאורה', 'Convertors':'מתאם'}


@views.route('/equipment')
@login_required
def equipment():
    
    # Filter equipment by Type, model, and Available
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
    
    return render_template("equipment.html", user=current_user, equipment_list=equipment_list, eq_dict=eq_dict)


@views.route('/report_failure', methods=['POST'])
@login_required
def report_failure():
    eq_serial = request.form['eq_serial']
    equipment = Equipment.query.filter_by(serial_number=eq_serial).first()
    if equipment:
        equipment.status = 'faulty'
        db.session.commit()
        flash('סטטוס הציוד עודכן בהצלחה.')
    else:
        flash('ציוד לא נמצא במערכת.')

    return redirect(url_for('views.equipment'))


@views.route('/report_available', methods=['POST'])
@login_required
def report_available():
    eq_serial = request.form['eq_serial']
    equipment = Equipment.query.filter_by(serial_number=eq_serial).first()
    if equipment:
        equipment.status = 'available'
        db.session.commit()
        flash('סטטוס הציוד עודכן בהצלחה.')
    else:
        flash('ציוד לא נמצא במערכת.')

    return redirect(url_for('views.equipment'))



@views.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
    if request.method == 'POST':
        type = request.form.get('type')
        model = request.form.get('model')
        from_date = request.form.get('pickup_date')
        to_date = request.form.get('return_date')

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
                    if borrows_list:
                        for borrow in borrows_list:
                            bor_from_d = datetime.strptime(borrow.borrow_date, '%d/%m/%Y')
                            bor_to_d = datetime.strptime(borrow.return_date, '%d/%m/%Y')
                            if (from_d <= bor_to_d) and (to_d >= bor_from_d):
                                overlaped = True
                                break                        
                    if diff.days <= aquip.max_time:
                        print(overlaped)
                        if overlaped == False:
                            if current_user.userType == "Student":
                                new_order = Borrow(borrower=current_user.id, aq_serial=aquip.serial_number, borrow_date=from_d.strftime('%d/%m/%Y'), return_date=to_d.strftime('%d/%m/%Y'), return_status="no")
                            else:
                                new_order = Borrow(borrower=current_user.id, aq_serial=aquip.serial_number, borrow_date=from_d.strftime('%d/%m/%Y'), return_date=from_d.strftime('%d/%m/%Y'), return_status="no")    
                            new_noti = Notification(type="order", date=from_d.strftime('%d/%m/%Y'), user=current_user.id, item=aquip.serial_number, is_read="no")
                            db.session.add(new_order)
                            db.session.add(new_noti)
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


@views.route('/transfer_form', methods=['POST', 'GET'])
@login_required
def transfer_form():
    serial = request.args.get('eq_serial')
    borrowed_items = Borrow.query.filter_by(return_status='no').filter_by(aq_serial=serial).first()
        
    return render_template("transfer_form.html", user=current_user, borrowed_items=borrowed_items)


@views.route('/check_trans', methods=['POST', 'GET'])
@login_required
def check_trans():
    today = datetime.now().date().strftime("%d/%m/%Y")
    mail = request.form.get('email')
    user = User.query.filter_by(email=mail).first()
    serial = request.form.get('aq_serial')
    borrowed_items = Borrow.query.filter_by(return_status='no').filter_by(aq_serial=serial).first()
    
    borrows = Borrow.query.filter_by(return_status='no').all()
    all_borrowed = []
    for borrow in borrows:
        if borrow.item.status == 'borrowed':
            all_borrowed.append(borrow)

    if user :
        if current_user.userType == 'Manager':
            if user.id != borrowed_items.user.id and user.userType == borrowed_items.user.userType and user.userType != 'Manager':
                new_order = Borrow(borrower=user.id, aq_serial=borrowed_items.aq_serial, borrow_date=today, return_date=borrowed_items.return_date, return_status="no")
                new_noti = Notification(type="swap", date=today, user=user.id, item=borrowed_items.aq_serial, is_read="no")
                borrowed_items.return_date = today
                borrowed_items.return_status = "yes"
                borrowed_items.item.status = 'borrowed'
                db.session.add(new_order)
                db.session.add(new_noti) 
                db.session.commit()
                flash(' הועבר בהצלחה ', category='success')
                return redirect(url_for('views.borrowed_equipment'))      
            else:
                flash('לא ניתן להעביר ציוד למשתמש זה', category='error')
                return redirect(url_for('views.transfer_form', eq_serial=borrowed_items.aq_serial))
                
        else:
            if user.id != current_user.id and  user.userType == current_user.userType:
                new_order = Borrow(borrower=user.id, aq_serial=borrowed_items.aq_serial, borrow_date=today, return_date=borrowed_items.return_date, return_status="no")
                new_noti = Notification(type="swap", date=today, user=user.id, item=borrowed_items.aq_serial, is_read="no")
                borrowed_items.return_date = today
                borrowed_items.return_status = "yes"
                borrowed_items.item.status = 'borrowed'
                db.session.add(new_order)
                db.session.add(new_noti) 
                db.session.commit()
                flash(' הועבר בהצלחה ', category='success')
                return redirect(url_for('views.user_borrowing', borrows=borrows))
            else:
                flash('לא ניתן להעביר ציוד למשתמש זה', category='error')
                return redirect(url_for('views.transfer_form', eq_serial=borrowed_items.aq_serial))

    else:
        flash('משתמש לא נמצא', category='error')
        return redirect(url_for('views.transfer_form', eq_serial=borrowed_items.aq_serial))


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
        return render_template("borrowed_equipment.html" , borrows=all_borrowed , user=current_user, eq_dict=eq_dict)


#Equipment return reporting process
@views.route('/report_return', methods=['POST'])
@login_required
def report_return():
    today = datetime.now().date()

    borrows = Borrow.query.filter_by(return_status='no').all()
    all_borrowed = []
    for borrow in borrows:
        if borrow.item.status == 'borrowed':
            all_borrowed.append(borrow)
    
    if request.method == 'POST':
        borrow_id = request.form.get('borrow_id')
        borrow = Borrow.query.filter_by(id=borrow_id).first()
        equipment = Equipment.query.filter_by(serial_number=borrow.aq_serial).first()
        if equipment and borrows:
            equipment.status = 'available'
            return_date = datetime.strptime(borrow.return_date, '%d/%m/%Y').date()
            if (return_date > today):
                borrow.return_status='yes'
            else:
                borrow.return_status='late'
            borrow.return_date = today.strftime("%d/%m/%Y")
            db.session.commit()
            flash(' ציוד הוחזר בהצלחה ', 'success')
            return redirect(url_for('views.borrowed_equipment'))
        else:
            flash('!ציוד לא נמצא', 'error')
    return render_template("borrowed_equipment.html", borrows=all_borrowed, user=current_user)



#Equipment malfunction reporting process
@views.route('/report_fault', methods=['POST'])
@login_required
def report_fault():
    today = datetime.now().date()

    borrows = Borrow.query.filter_by(return_status='no').all()
    all_borrowed = []
    for borrow in borrows:
        if borrow.item.status == 'borrowed':
            all_borrowed.append(borrow)

    borrow_id = request.form.get('borrow_id')
    borrow = Borrow.query.filter_by(id=borrow_id).first()
    equipment = Equipment.query.filter_by(serial_number=borrow.aq_serial).first()
    if equipment and borrows:
        equipment.status = 'faulty'
        return_date = datetime.strptime(borrow.return_date, '%d/%m/%Y').date()
        if (return_date > today):
                borrow.return_status='yes'
        else:
            borrow.return_status='late'
        borrow.return_date = today.strftime("%d/%m/%Y")
        db.session.commit()
        return redirect(url_for('views.borrowed_equipment'))
    return render_template("borrowed_equipment.html", borrows=all_borrowed, user=current_user)
    


@views.route('/user_borrowing', methods=['GET', 'POST'])
def user_borrowing():
    query = Borrow.query
    query = query.filter_by(borrower=current_user.id)
    borrows = query.all()
    return render_template("user_borrowing.html", borrows=borrows , user=current_user, eq_dict=eq_dict)


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
        type = request.form.get('type')
        model = request.form.get('model')
        serial_number = request.form.get('serialNumber')
        max_time = request.form.get('maxTime')
        
        # Create a new Equipment object
        new_equipment = Equipment(Type=type, model=model, serial_number=serial_number, status='available', max_time=max_time)
        
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
        borrow = Borrow.query.filter_by(id=borrow_id).first()
        equipment = Equipment.query.filter_by(serial_number=borrow.aq_serial).first()
        if equipment:
            equipment.status = 'borrowed'
            new_noti = Notification(type="return", date=borrow.return_date, user=current_user.id, item=borrow.aq_serial, is_read="no")
            db.session.add(new_noti)
            db.session.commit()
            flash('!ציוד הוחזר בהצחלה', 'success')
            return redirect(url_for('views.eq_transfer'))

    return render_template("eq_transfer.html", user=current_user, borrows=borrows_today, eq_dict=eq_dict)



@views.route('/notifications/count', methods=['GET'])
@login_required
def notifications_count():
    today = datetime.now().date().strftime("%d/%m/%Y")
    count = 0
    if current_user.userType == "Manager":
        count = Notification.query.filter_by(date=today).filter(or_(Notification.is_read == "no", Notification.is_read == "u")).count()

    else:
        count = Notification.query.filter_by(date=today).filter_by(user=current_user.id).filter(or_(Notification.is_read == "no", Notification.is_read == "m")).count()
    return jsonify({'count': count})



@views.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    today = datetime.now().date().strftime("%d/%m/%Y")
    
    if current_user.userType == "Manager":
        noti_today = Notification.query.filter_by(date=today).filter(or_(Notification.is_read == "no", Notification.is_read == "u")).all()
        desc_dict = {'order': 'השאלה שהוזמנה להיום', 'return': 'השאלה שאמורה להיות מוחזרת היום', 'fault': 'דווחה תקלה במוצר שבהשאלה', 'swap': 'בוצעה החלפה בין משתמשים'}
    else:
        noti_today = Notification.query.filter_by(date=today).filter_by(user=current_user.id).filter(or_(Notification.is_read == "no", Notification.is_read == "m")).all()
        desc_dict = {'order': 'ההשאלה שבוקשה על ידך מתקיימת היום', 'return': 'ההשאלה שברשותך אמורה להיות מוחזרת היום', 'fault': 'דווחה תקלה שביצעת התקבלה במערכת','swap': 'בוצעה החלפה בין משתמשים'}
    return render_template("notifications.html", user=current_user, notifs=noti_today, desc_dict=desc_dict, eq_dict=eq_dict )


@views.route('/seen_notification', methods=['GET', 'POST'])
@login_required
def seen_notification():
    noti_id = request.args.get('notif_id')
    print(noti_id)
    notification = Notification.query.filter_by(id=noti_id).first()
    if current_user.userType == "Manager":
        if notification.is_read == "no": 
            notification.is_read = "m" 
        else: 
            notification.is_read = "both" 
        db.session.commit()
    else:
        if notification.is_read == "no": 
            notification.is_read = "u" 
        else: 
            notification.is_read = "both"
        db.session.commit()
    
    return redirect(url_for('views.notifications'))



@views.route('/who_borrowed', methods=['GET', 'POST'])
@login_required
def who_borrowed():
    serial = request.form.get('eq_serial')

    # Get the list of borrowed items
    borrowed_items = Borrow.query.filter_by(return_status='no').filter_by(aq_serial=serial).first()
    return render_template('who_borrowed.html', borrowed_items=borrowed_items, user=current_user, eq_dict=eq_dict)



@views.route('/return_policy', methods=['GET', 'POST'])
@login_required
def return_policy():
    # Filter equipment by Type, model
    type_filter = request.form.get('type')
    model_filter = request.form.get('model')
  
    query = Equipment.query

    if type_filter:
        query = query.filter_by(Type=type_filter)
    if model_filter:
        query = query.filter_by(model=model_filter)
    
    equipment_list = query.all()

    max_time = None
    new_max_time = None

    if type_filter and model_filter:
        equipment = Equipment.query.filter_by(Type=type_filter, model=model_filter).first()
        if equipment:
            max_time = equipment.max_time

    if request.method == 'POST':
        new_max_time = request.form.get('newMaxTime')
        if type_filter and model_filter and new_max_time:
            # Update max borrowing time for all products with the same type and model
            Equipment.query.filter_by(Type=type_filter, model=model_filter).update({Equipment.max_time: new_max_time})
            db.session.commit()
            flash('Max borrowing time updated successfully!', 'success')
            return redirect(url_for('views.equipment'))

    return render_template("return_policy.html", user=current_user, equipment_list=equipment_list, max_time=max_time, new_max_time=new_max_time)

 
@views.route('/get_old_loan_time', methods=['POST'])
def get_old_loan_time():
    product_type = request.form.get('type')
    product_model = request.form.get('model')

    equipment = Equipment.query.filter_by(Type=product_type, model=product_model).first()

    if equipment:
        old_loan_time = equipment.max_time
    else:
        old_loan_time = ''

    return jsonify({'old_loan_time': old_loan_time})




@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        old_password = request.form.get('old_pass')
        new_password = request.form.get('pass1')
        confirm_password = request.form.get('pass2')

        # Check if the old password matches the stored password
        if check_password_hash(current_user.password, old_password):
            if len(new_password) < 7:
                flash('הסיסמא חייבת להיות לפחות 7 תווים.', category='error')
            elif new_password != confirm_password:
                flash('הסיסמאות לא תואמות', category='error')

            elif check_password_hash(current_user.password, new_password):
                flash('לא ניתן לשנות לסיסמה הקודמת.', category='error')

                # Checks that the password is structured correctly
            elif not any(char.isupper() for char in new_password):
                flash('הסיסמה חייבת להכיל לפחות אות אחת גדולה.', category='error')
            elif not any(char.islower() for char in new_password):
                flash('הסיסמה חייבת להכיל לפחות אות קטנה אחת.', category='error')
            elif not any(char.isdigit() for char in new_password):
                flash('הסיסמה חייבת להכיל לפחות ספרה אחת.', category='error')   

            else:
                # Check if the new password and confirm password match
                    if new_password == confirm_password:
                        # Hash the new password
                        hashed_password = generate_password_hash(new_password, method='sha256')

                        # Update the user's password in the database
                        current_user.password = hashed_password
                        db.session.commit()

                        flash('סיסמה עודכנה בהצלחה', category='success')
                    else:
                        flash('הסיסמאות לא תואמות', category='error')
        else:
            flash('סיסמה ישנה שגויה', category='error')

    return render_template("profile.html", user=current_user)












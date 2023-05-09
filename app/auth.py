from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Equipment, User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

import app

auth = Blueprint("auth", __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.equipment'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('name')
        phone = request.form.get('phone')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        userType = request.form.get('userType')

        # inputs required
        if not email:
            flash('יש להכניס אימייל', category='error')
        elif not first_name:
            flash('יש להכניס שם מלא.', category='error')
        elif not phone:
            flash('יש להכניס מספר טלפון', category='error')
        elif not password1 or not password2:
            flash('יש להכניס סיסמא ', category='error')

        # checks that email is an SCE address
        elif not email.endswith('@sce.ac.il') and not email.endswith('@ac.sce.ac.il'):
            flash('חייב להיות אימייל תקין של המכללה', category='error')

        # Field size check
        elif len(first_name) < 5:
            flash('השם הפרטי חייב להיות גדול מ-5 תווים.', category='error')
        elif len(phone) != 10:
            flash('מספר טלפון חייב להכיל 10 תווים', category='error')
        elif len(password1) < 7:
            flash('הסיסמא חייבת להיות לפחות 7 תווים.', category='error')

        # password1 and password2 matching
        elif password1 != password2:
            flash('הסיסמאות לא תואמות', category='error')

        # Checks that the password is structured correctly
        elif not any(char.isupper() for char in password1):
            flash('הסיסמה חייבת להכיל לפחות אות אחת גדולה.', category='error')
        elif not any(char.islower() for char in password1):
            flash('הסיסמה חייבת להכיל לפחות אות קטנה אחת.', category='error')
        elif not any(char.isdigit() for char in password1):
            flash('הסיסמה חייבת להכיל לפחות ספרה אחת.', category='error')

        # If everything was inserted correctly
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                flash('האימייל כבר קיים במערכת', category='error')
            else:
                new_user = User(userType=userType, email=email, name=first_name, password=generate_password_hash(password1, method='sha256'),phone=phone)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('חשבון נוצר!', category='success')
                return redirect(url_for('views.equipment'))

    return render_template("register.html", user=current_user)

@auth.route('/adding_equipment', methods=['GET', 'POST'])
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


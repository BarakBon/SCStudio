from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Equipment, User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, request
from flask_mail import Mail, Message
import secrets , string

import sendgrid
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from flask import current_app


import app

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = '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'
app.config['SENDGRID_API_KEY'] = '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'
app.config['MAIL_DEFAULT_SENDER'] = 'vcew2023@gmail.com'

mail = Mail(app)


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash(' התחבר בהצלחה ', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.equipment'))
            else:
                flash('!סיסמא שגויה, נסה שוב', category='error')
        else:
            flash('מייל לא קיים ', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/reset_password', methods=['POST'])
def reset_password():
    reset_email = request.form.get('resetEmail')
    print(reset_email)
    user = User.query.filter_by(email=reset_email).first()
    if user:
        # Generate a temporary password
        alphabet = string.ascii_letters + string.digits + string.punctuation
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(8))
            if any(c.islower() for c in password) and any(c.isupper() for c in password) and any(c in string.punctuation for c in password):
                break

        # Create the email message
        message = Mail(
            from_email='vcew2023@gmail.com',
            to_emails=[reset_email],
            subject='Password Reset',
            plain_text_content=f'{password} :הסיסמא הזמנית שלך היא \n אנא החלף סיסמא לאחר ההתחברות'
        )
        
        user.password=generate_password_hash(password, method='sha256')
        db.session.commit()
        
       
       
            # Create a SendGrid client
        sg = SendGridAPIClient(api_key=app.config['SENDGRID_API_KEY'])
            
            # Send the email
        response = sg.send(message)
            
        if response.status_code == 202:
                flash('סיסמא זמנית נשלחה', category='success')
        else:
                flash('שליחת מייל נכשלה, נסה שוב .', category='error')

        ''' except Exception as e:
            flash('אירעה שגיאה בעת שליחת האימייל. בבקשה נסה שוב מאוחר יותר.', category='error')
'''
    else:
        flash('כתובת האימייל לא קיימת', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout', methods=['GET', 'POST'])
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


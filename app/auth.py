from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Equipment, User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, request
from flask_mail import Mail, Message
import secrets , string


import app


app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'vcew2023@gmail.com'
app.config['MAIL_PASSWORD'] = 'Aa123456!'
mail = Mail(app)



auth = Blueprint("auth", __name__, template_folder='templates')


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
        msg = Message('Password Reset', sender='vcew2023@gmail.com', recipients=[reset_email])
        msg.body = f'Your temporary password is: {password}'

        # Send the email
        mail.send(msg)


        flash(' נשלחה סיסמא זמנית', category='success')
        return render_template("login.html", user=current_user)
    else:
        flash(' מייל לא קיים ', category='error')
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


from flask import Blueprint, render_template, request, flash, jsonify

views = Blueprint('views', __name__)


@views.route('/equipment', methods=['GET', 'POST'])
def equipment():
    
    return render_template("equipment.html")

@views.route('/Borrowing_Equipment', methods=['GET', 'POST'])
def Borrowing_Equipment():
    
    return render_template("Borrowing_Equipment.html")

@views.route('/equipment_failure', methods=['GET', 'POST'])
def equipment_failure():
    
    return render_template("equipment_failure.html")


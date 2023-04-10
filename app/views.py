from flask import Blueprint, render_template, request, flash, jsonify

views = Blueprint('views', __name__)


@views.route('/equipment', methods=['GET', 'POST'])
def equipment():
    
    return render_template("equipment.html")



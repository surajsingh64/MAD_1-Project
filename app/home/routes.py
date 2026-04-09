from flask import render_template
from app.home import home

@home.route('/') 
def landing_page():
     return render_template('home/landing.html')
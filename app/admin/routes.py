from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from . import admin_bp
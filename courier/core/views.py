from flask import redirect, render_template,request, Blueprint, url_for, flash, session


core = Blueprint('core', __name__, template_folder='templates')


@core.route('/')
def index():

    return render_template('index.html')
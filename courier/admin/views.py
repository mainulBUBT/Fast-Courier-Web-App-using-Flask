from asyncio.windows_events import NULL
from turtle import update
from flask import Blueprint, redirect, request, render_template, url_for, session, flash
from flask_login import login_user, current_user
from functools import wraps

from sqlalchemy import null

from courier import db
from courier.admin.forms import LoginForm
from courier.models import Merchant, DeliveryInfo, Parcel, User



admin = Blueprint('admin', __name__, template_folder='templates')

def login_required_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in_admin' in session:
            return f(*args, **kwargs)
        else:
            flash("You are not Admin")
            return redirect(url_for('core.index'))

    return wrap




@admin.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user.check_password(form.password.data) and user is not None:
            login_user(user)
            session['role'] = user.roles
            if session['role'] == 'admin':
                session['logged_in_admin'] = True
                flash('Logged in successfully', "success" )

                next = request.args.get('next')
                if next == None or not next[0] == '/':
                    next = url_for('admin.admin_dashboard')
                return redirect(next)
            else:
                flash('Username and Password not found!', 'danger')
                return redirect(url_for('admin.admin_login'))
        else:
            flash('information Wrong!', "danger" )  
    return render_template('admin_login.html', form=form)




@admin.route('/admin_dashboard')
def admin_dashboard():

    return render_template('admin_dashboard.html')


@admin.route('/pending_parcels', methods=['GET', 'POST'])
def pending_parcels():

    pending_search = ''
    pending_list = ''

    page = request.args.get('page',1,type=int)

    if request.method == 'POST':
        if 'search' in request.form:
            track_number = int(request.form['track_number'])
            pending_search = db.session.query(DeliveryInfo.receiver_name,DeliveryInfo.receiver_number, DeliveryInfo.receiver_address, DeliveryInfo.delivery_area, Parcel.delivery_man, Parcel.id, Parcel.parcel_status, DeliveryInfo.receiver_number).join(Parcel).filter(Parcel.id == track_number , Parcel.parcel_status == 'Not pickup yet')
        elif 'update' in request.form:
            parcel_id = request.form['parcel_id']
            delivery_man = request.form['delivery_man']
            parcel_status = request.form['parcel_status']

            update_sql = Parcel.query.filter_by(id=parcel_id).first()

            if delivery_man and parcel_status is not None:
                print(update_sql)
                update_sql.delivery_man = delivery_man
                update_sql.parcel_status = parcel_status
                db.session.commit()
                flash('Parcel Sent to the '+ parcel_status +' section', 'warning')
                return redirect(url_for('admin.pending_parcels')) 
    else:
        pending_list= db.session.query(DeliveryInfo.receiver_name,DeliveryInfo.receiver_number, DeliveryInfo.receiver_address, DeliveryInfo.delivery_area, Parcel.delivery_man, Parcel.id, Parcel.parcel_status,DeliveryInfo.receiver_number).join(Parcel).filter(Parcel.parcel_status == 'Not pickup yet').order_by(DeliveryInfo.book_date.asc()).paginate(page=page,per_page=8)
   
    return render_template('pending_parcels.html', pending_list = pending_list, pending_search=pending_search)

@admin.route('/delivered_parcels', methods=['GET', 'POST'])
def delivered_parcels():

    delivered_search = ''
    delivered_list = ''

    page = request.args.get('page',1,type=int)

    if request.method == 'POST':
        if 'search' in request.form:
            track_number = int(request.form['track_number'])
            delivered_search = db.session.query(DeliveryInfo.receiver_name,DeliveryInfo.receiver_number, DeliveryInfo.receiver_address, DeliveryInfo.delivery_area, Parcel.delivery_man, Parcel.id, Parcel.parcel_status, DeliveryInfo.receiver_number).join(Parcel).filter(Parcel.id == track_number , Parcel.parcel_status == 'delivered')
        elif 'update' in request.form:
            parcel_id = request.form['parcel_id']
            delivery_man = request.form['delivery_man']
            parcel_status = request.form['parcel_status']

            update_sql = Parcel.query.filter_by(id=parcel_id).first()

            if delivery_man and parcel_status is not None:
                print(update_sql)
                update_sql.delivery_man = delivery_man
                update_sql.parcel_status = parcel_status
                db.session.commit()
                flash('Parcel Sent to the '+ parcel_status +' section', 'warning')
                return redirect(url_for('admin.delivered_parcels')) 
    else:
        delivered_list= db.session.query(DeliveryInfo.receiver_name,DeliveryInfo.receiver_number, DeliveryInfo.receiver_address, DeliveryInfo.delivery_area, Parcel.delivery_man, Parcel.id, Parcel.parcel_status,DeliveryInfo.receiver_number).join(Parcel).filter(Parcel.parcel_status == 'delivered').order_by(DeliveryInfo.book_date.asc()).paginate(page=page,per_page=8)
   
    return render_template('delivered_parcels.html', delivered_list = delivered_list, delivered_search=delivered_search)

@admin.route('/pickedup_parcels', methods=['GET', 'POST'])
def pickedup_parcels():

    pickedup_search = ''
    pickedup_list = ''

    page = request.args.get('page',1,type=int)

    if request.method == 'POST':
        if 'search' in request.form:
            track_number = int(request.form['track_number'])
            pickedup_search = db.session.query(DeliveryInfo.receiver_name,DeliveryInfo.receiver_number, DeliveryInfo.receiver_address, DeliveryInfo.delivery_area, Parcel.delivery_man, Parcel.id, Parcel.parcel_status, DeliveryInfo.receiver_number).join(Parcel).filter(Parcel.id == track_number , Parcel.parcel_status == 'picked up')
        elif 'update' in request.form:
            parcel_id = request.form['parcel_id']
            delivery_man = request.form['delivery_man']
            parcel_status = request.form['parcel_status']

            update_sql = Parcel.query.filter_by(id=parcel_id).first()

            if delivery_man and parcel_status is not None:
                print(update_sql)
                update_sql.delivery_man = delivery_man
                update_sql.parcel_status = parcel_status
                db.session.commit()
                flash('Parcel Sent to the '+ parcel_status +' section', 'warning')
                return redirect(url_for('admin.pickedup_parcels')) 
    else:
        pickedup_list= db.session.query(DeliveryInfo.receiver_name,DeliveryInfo.receiver_number, DeliveryInfo.receiver_address, DeliveryInfo.delivery_area, Parcel.delivery_man, Parcel.id, Parcel.parcel_status,DeliveryInfo.receiver_number).join(Parcel).filter(Parcel.parcel_status == 'picked up').order_by(DeliveryInfo.book_date.asc()).paginate(page=page,per_page=8)
   
    return render_template('pickedup_parcels.html', pickedup_list = pickedup_list, pickedup_search=pickedup_search)

@admin.route('/transit_parcels', methods=['GET', 'POST'])
def transit_parcels():

    transit_search = ''
    transit_list = ''

    page = request.args.get('page',1,type=int)

    if request.method == 'POST':
        if 'search' in request.form:
            track_number = int(request.form['track_number'])
            transit_search = db.session.query(DeliveryInfo.receiver_name,DeliveryInfo.receiver_number, DeliveryInfo.receiver_address, DeliveryInfo.delivery_area, Parcel.delivery_man, Parcel.id, Parcel.parcel_status, DeliveryInfo.receiver_number).join(Parcel).filter(Parcel.id == track_number , Parcel.parcel_status == 'in transit')
        elif 'update' in request.form:
            parcel_id = request.form['parcel_id']
            delivery_man = request.form['delivery_man']
            parcel_status = request.form['parcel_status']

            update_sql = Parcel.query.filter_by(id=parcel_id).first()

            if delivery_man and parcel_status is not None:
                print(update_sql)
                update_sql.delivery_man = delivery_man
                update_sql.parcel_status = parcel_status
                db.session.commit()
                flash('Parcel Sent to the '+ parcel_status +' section', 'warning')
                return redirect(url_for('admin.transit_parcels')) 
    else:
        transit_list= db.session.query(DeliveryInfo.receiver_name,DeliveryInfo.receiver_number, DeliveryInfo.receiver_address, DeliveryInfo.delivery_area, Parcel.delivery_man, Parcel.id, Parcel.parcel_status,DeliveryInfo.receiver_number).join(Parcel).filter(Parcel.parcel_status == 'in transit').order_by(DeliveryInfo.book_date.asc()).paginate(page=page,per_page=8)
   
    return render_template('transit_parcels.html', transit_list = transit_list, transit_search=transit_search)

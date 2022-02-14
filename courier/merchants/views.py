import os
from flask import redirect, render_template,request, Blueprint, url_for, flash, session, current_app
from flask_login import login_user, logout_user, current_user
from sqlalchemy.sql import func
from os import abort
from werkzeug.utils import secure_filename


from courier import db
from courier.merchants.forms import PickupRequest, RegisterFrom, LoginForm
from courier.models import Merchant, DeliveryInfo, Parcel, User
from functools import wraps

merchant = Blueprint('merchant', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = set(['png', 'jpg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required_user(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in_user' in session:
            return f(*args, **kwargs)
        else:
            flash("You are not Merchant")
            return redirect(url_for('core.index'))

    return wrap


@merchant.route('/merchant_login', methods=['GET', 'POST'])
def merchant_login():

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user.check_password(form.password.data) and user is not None:
            login_user(user)
            session['role'] = user.roles
            if session['role'] == 'merchant':
                session['logged_in_user'] = True
                flash('Logged in successfully', "success" )

                next = request.args.get('next')
                if next == None or not next[0] == '/':
                    next = url_for('merchant.merchant_dashboard')
                return redirect(next)
            else:
                flash('Username and Password not found!', 'danger')
                return redirect(url_for('merchant.merchant_login'))
        else:
            flash('information Wrong!', "danger" )
    
    return render_template('merchant_login.html', form=form)
    
@merchant.route('/logout')
def logout():
    if 'logged_in_user' in session:
        logout_user()
        session.pop('logged_in_user', None)
        flash('Logged out Successfully!', 'success')
        return redirect(url_for('merchant.merchant_login'))

    elif 'logged_in_admin' in session:
        session.pop('logged_in_admin', None)
        flash('Logged out Successfully!', 'success')
        return redirect(url_for('admin.admin_login'))


@merchant.route('/merchant_register', methods=['POST', 'GET'])
def merchant_register():

    form = RegisterFrom()

    if form.validate_on_submit():
        
        user = User(email=form.email.data, username=form.username.data, mobile_number=form.mobile_number.data, password=form.password.data)
        db.session.add(user)
        db.session.flush()
        db.session.commit()

        if user.id is not None:
            merchant= Merchant(merchant_id = user.id, pickup_address = form.address.data)
            db.session.add(merchant)
            db.session.commit()
            flash("Registraion Successful. Login Now!",'success')
            return redirect(url_for('merchant.merchant_login'))

    return render_template('merchant_register.html', form=form)

@merchant.route('/merchant_dashboard')
@login_required_user
def merchant_dashboard():

    user_paid =  ''
    charge_due = ''
    user_due = ''
    
    total_count = db.session.query(Parcel.id).filter(Parcel.merchant_id == current_user.id).count()
    delivered_count = db.session.query(Parcel.id).filter(Parcel.merchant_id == current_user.id, Parcel.parcel_status == 'delivered').count()
    
    user_paid = db.session.query(func.sum(Parcel.user_balance).label('sum')).filter(Parcel.pay_status == '1', Parcel.merchant_id == current_user.id)
    user_due = db.session.query(func.sum(Parcel.user_balance).label('sum')).filter(Parcel.pay_status == '0', Parcel.merchant_id == current_user.id)
    charge_due = db.session.query(func.sum(Parcel.due_charge).label('sum')).filter(Parcel.pay_status == '0', Parcel.merchant_id == current_user.id)

   
    for due in user_due:
      user_due = due.sum
    print(user_due)

    for paid in user_paid:
        user_paid = paid.sum
    print(user_paid)

    for due_charge in charge_due:
        charge_due = due_charge.sum
    print(charge_due)

    return render_template('merchant_dashboard.html', sidebar_name='merchant_dashboard', total_count = total_count,delivered_count=delivered_count, user_paid = user_paid, user_due = user_due, charge_due=charge_due)

@merchant.route('/all_parcels', methods=['GET', 'POST'])
def all_parcels():

    parcel_search = ''
    parcel_list = ''

    page = request.args.get('page',1,type=int)

    if request.method == 'POST':
        if 'search' in request.form:
            track_number = int(request.form['track_number'])
            parcel_search = db.session.query(DeliveryInfo.receiver_name,DeliveryInfo.receiver_number, DeliveryInfo.receiver_address, DeliveryInfo.delivery_area, DeliveryInfo.collectable_amount, Parcel.id).join(Parcel).filter(Parcel.id == track_number , Parcel.merchant_id == current_user.id)
   
    else:
        parcel_list= db.session.query(DeliveryInfo.receiver_name,DeliveryInfo.receiver_number, DeliveryInfo.receiver_address, DeliveryInfo.delivery_area, DeliveryInfo.collectable_amount, Parcel.id).join(Parcel).filter(Parcel.merchant_id == current_user.id , DeliveryInfo.merchant_id == current_user.id).order_by(DeliveryInfo.book_date.desc()).paginate(page=page,per_page=8)
    
    return render_template('all_parcels.html', parcel_list=parcel_list, parcel_search=parcel_search, sidebar_name='all_parcels')

@merchant.route('/<int:id>/delete_parcel', methods=['GET', 'POST'])
def delete_parcel(id):
    parcel_sql = Parcel.query.get_or_404(id)

    delivery_id = parcel_sql.delivery_id
    parcel_status = parcel_sql.parcel_status

    if parcel_sql.merchant_id != current_user.id:
        abort(403)

    if parcel_status == 'Not pickup yet':
        db.session.delete(parcel_sql)

        delivery_info_sql = DeliveryInfo.query.get_or_404(delivery_id)
        db.session.delete(delivery_info_sql)
        
        db.session.commit()
        flash('Deleted your parcel pickup request from queue', 'success')
        return redirect(url_for('merchant.all_parcels'))
    else:
        flash('Sorry, you cannot cancel pickup or parcel order right now! Already picked up. For more info contact our office', 'danger')
        return redirect(url_for('merchant.all_parcels'))

    

@merchant.route('/parcel_track', methods=['GET', 'POST'])
def parcel_track():
    parcel_search = ''

    if request.method == 'POST':
        if 'search' in request.form:
            track_id = request.form['track_id']
            parcel_search = db.session.query(DeliveryInfo.delivery_area, DeliveryInfo.receiver_name,DeliveryInfo.receiver_address, Parcel.id, Parcel.delivery_man, Parcel.parcel_status, Parcel.parcel_date, Parcel.updated_at).join(Parcel).filter(Parcel.id == track_id)
            print(track_id)
 
        
    return render_template('parcel_track.html', parcel_search=parcel_search, sidebar_name='parcel_track')

@merchant.route('/merchant_payments', methods = ['GET', 'POST'])
def merchant_payments():
    payment_search = ''
    payment_sql = ''
    page = request.args.get('page',1,type=int)

    if request.method == 'POST':
        if 'search' in request.form:
            track_id = request.form['track_id']
            print(track_id)
            payment_search = db.session.query(Parcel.id, Parcel.due_charge, Parcel.user_balance, Parcel.parcel_status, Parcel.pay_method, Parcel.pay_status).filter(Parcel.merchant_id == current_user.id, Parcel.id == track_id)
            print(payment_search)
    else:
        payment_sql = db.session.query(Parcel.id, Parcel.due_charge, Parcel.user_balance, Parcel.parcel_status, Parcel.pay_method, Parcel.pay_status).filter(Parcel.merchant_id == current_user.id).order_by(Parcel.id.desc()).paginate(page=page,per_page=8)

    return render_template('merchant_payments.html', sidebar_name='merchant_payments', payment_sql=payment_sql, payment_search = payment_search)


@merchant.route('/merchant_settings', methods=['GET', 'POST'])
def merchant_settings():
    get_info = ''
    if request.method == 'POST':
        if 'update' in request.form: 
            old_password = request.form['old_pass']
            new_password = request.form['new_pass']
            email = request.form['email']
            update_sql = User.query.filter_by(email=email).first()
            
            if update_sql.id == current_user.id and update_sql.check_password(old_password):

                update_sql.change_password(new_password)
                db.session.commit()
                flash('your Password Updated!', 'success')
                return redirect(url_for('merchant.merchant_settings')) 
            else:
                flash('Enter current password correctly!', 'danger')
                return redirect(url_for('merchant.merchant_settings'))

        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('merchant.merchant_settings'))

        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading', 'danger')
            return redirect(url_for('merchant.merchant_settings'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ext_type = filename.split('.')[-1]
            storage_filename = str(current_user.username)+'.'+ext_type
            user_id = current_user.id
            image_sql = User.query.filter_by(id = user_id).first()
            if image_sql:
                file.save(os.path.join(current_app.root_path, 'static\profile_pics', storage_filename))
                image_sql. profile_image = storage_filename
                db.session.commit()
                # print('upload_image filename: ' + filename)
                flash('Image successfully updated', 'success')
                return redirect(url_for('merchant.merchant_settings'))

        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif', 'danger')
            return redirect(url_for('merchant.merchant_settings'))
    else:       
        get_info = db.session.query(Merchant.merchant_id, Merchant.bank_number, Merchant.bkash_number, Merchant.pickup_address, User.id, User.mobile_number, User.username, User.email).join(Merchant).filter(Merchant.merchant_id == current_user.id, User.id == current_user.id)


    return render_template('merchant_settings.html', sidebar_name='merchant_settings', get_info = get_info)




@merchant.route('/parcel_request', methods=['POST', 'GET'])
def parcel_request():

    form = PickupRequest()

    result = []

    form.select_zone.choices = choiceList(result)
    
    SELECT_WEIGHTS = {
    'Dhaka Metro': [('1', 'Upto 1 KG'), ('2', 'Upto 3 KG')],
    'Outside Dhaka': [('1', 'Upto 3 KG'), ('2', 'Upto 5 KG')],
    'Next Day': [('1', 'Upto 3 KG')],
    }

    form.select_weight.choices = SELECT_WEIGHTS.get(form.select_zone.data) or []


    if form.validate_on_submit():

        zone = form.select_zone.data
        weight = form.select_weight.data
        amount = form.collectable_amount.data
        print('weight '+ weight + 'zone '+ zone)
        if zone == 'Dhaka Metro':
            
            if amount == '0':

                delivery = DeliveryInfo(receiver_name=form.receipient_name.data,delivery_area=form.select_zone.data, collectable_amount=form.collectable_amount.data, receiver_number=form.receipient_number.data, receiver_address=form.receipient_address.data, merchant_id=current_user.id)
                db.session.add(delivery)
                db.session.flush()
                db.session.commit()

                if weight == '1':

                    parcel = Parcel(merchant_id=current_user.id, delivery_id=delivery.id, parcel_status='Not pickup yet', charge='0', due_charge='70', user_balance='0')
                    db.session.add(parcel)
                    db.session.commit()
                    flash('You have been created Pick-Up request, Thank you!', 'success')
                    return redirect(url_for('merchant.all_parcels'))

                else:
                    parcel = Parcel(merchant_id=current_user.id, delivery_id=delivery.id, parcel_status='Not pickup yet', charge='0', due_charge='100', user_balance='0')
                    db.session.add(parcel)
                    db.session.commit()
                    flash('You have been created Pick-Up request, Thank you!', 'success')
                    return redirect(url_for('merchant.all_parcels'))

            elif (int(amount)>=70 and weight == '1') or (int(amount)>=100 and weight == '2'):

                balance_left = int(amount)-70
                balance_left_2 = int(amount)-100

                delivery = DeliveryInfo(receiver_name=form.receipient_name.data,delivery_area=form.select_zone.data, collectable_amount=form.collectable_amount.data, receiver_number=form.receipient_number.data, receiver_address=form.receipient_address.data, merchant_id=current_user.id)
                db.session.add(delivery)
                db.session.flush()
                db.session.commit()

                if weight == '1':
                    
                    parcel = Parcel(merchant_id=current_user.id, delivery_id=delivery.id, parcel_status='Not pickup yet', charge='70', due_charge='0', user_balance= balance_left)
                    db.session.add(parcel)
                    db.session.commit()
                    flash('You have been created Pick-Up request, Thank you!', 'success')
                    return redirect(url_for('merchant.all_parcels'))
                else:

                    parcel = Parcel(merchant_id=current_user.id, delivery_id=delivery.id, parcel_status='Not pickup yet', charge='100', due_charge='0', user_balance= balance_left_2)
                    db.session.add(parcel)
                    db.session.commit()
                    flash('You have been created Pick-Up request, Thank you!', 'success')
                    return redirect(url_for('merchant.all_parcels'))
            else:
                flash('Input collectable amount for 1KG 70 Taka or more, if 3KG then 100 Taka or more', 'warning')
        
        elif zone == 'Outside Dhaka':
            
            if amount == '0':

                delivery = DeliveryInfo(receiver_name=form.receipient_name.data,delivery_area=form.select_zone.data, collectable_amount=form.collectable_amount.data, receiver_number=form.receipient_number.data, receiver_address=form.receipient_address.data, merchant_id=current_user.id)
                db.session.add(delivery)
                db.session.flush()
                db.session.commit()

                if weight == '1':

                    parcel = Parcel(merchant_id=current_user.id, delivery_id=delivery.id, parcel_status='Not pickup yet', charge='0', due_charge='120', user_balance='0')
                    db.session.add(parcel)
                    db.session.commit()
                    flash('You have been created Pick-Up request, Thank you!', 'success')
                    return redirect(url_for('merchant.all_parcels'))
                else:
                    parcel = Parcel(merchant_id=current_user.id, delivery_id=delivery.id, parcel_status='Not pickup yet', charge='0', due_charge='150', user_balance='0')
                    db.session.add(parcel)
                    db.session.commit()
                    flash('You have been created Pick-Up request, Thank you!', 'success')
                    return redirect(url_for('merchant.all_parcels'))

            elif (int(amount)>=120 and weight == '1') or (int(amount)>=150 and weight == '2'):

                balance_left = int(amount)-120
                balance_left_2 = int(amount)-150

                delivery = DeliveryInfo(receiver_name=form.receipient_name.data,delivery_area=form.select_zone.data, collectable_amount=form.collectable_amount.data, receiver_number=form.receipient_number.data, receiver_address=form.receipient_address.data, merchant_id=current_user.id)
                db.session.add(delivery)
                db.session.flush()
                db.session.commit()

                if weight == '1':
                    
                    parcel = Parcel(merchant_id=current_user.id, delivery_id=delivery.id, parcel_status='Not pickup yet', charge='120', due_charge='0', user_balance= balance_left)
                    db.session.add(parcel)
                    db.session.commit()
                    flash('You have been created Pick-Up request, Thank you!', 'success')
                    return redirect(url_for('merchant.all_parcels'))
                else:

                    parcel = Parcel(merchant_id=current_user.id, delivery_id=delivery.id, parcel_status='Not pickup yet', charge='150', due_charge='0', user_balance= balance_left_2)
                    db.session.add(parcel)
                    db.session.commit()
                    flash('You have been created Pick-Up request, Thank you!', 'success')
                    return redirect(url_for('merchant.all_parcels'))
            else:
                flash('Input collectable amount for 3KG 120 Taka or more, if 5KG then 150 Taka or more', 'warning')
        
        elif zone == 'Next Day':

            if (int(amount)>=120):

                balance_left = int(amount)-120
                
                delivery = DeliveryInfo(receiver_name=form.receipient_name.data,delivery_area=form.select_zone.data, collectable_amount=form.collectable_amount.data, receiver_number=form.receipient_number.data, receiver_address=form.receipient_address.data, merchant_id=current_user.id)
                db.session.add(delivery)
                db.session.flush()
                db.session.commit()

                if delivery.id is not None:

                    parcel = Parcel(merchant_id=current_user.id, delivery_id=delivery.id, parcel_status='Not pickup yet', charge='120', due_charge='0', user_balance=balance_left)
                    db.session.add(parcel)
                    db.session.commit()
                    flash('You have been created Pick-Up request, Thank you!', 'success')
                    return redirect(url_for('merchant.all_parcels'))
            else:
                flash("Next Day Delivery in Dhaka Metro collectable amount should be input {$next_dhk}120 or more Taka", 'warning')  
       
    return render_template('parcel_request.html', form = form, sidebar_name='parcel_request', )


def choiceList(result):
    area = {
    "Dhaka Metro": "Dhaka Metro",
    "Outside Dhaka": "Outside Dhaka",
    "Next Day": "Next Day in Dhaka Metro"
    }
    for k,v in area.items():
        result.append((k,v))
    
    return result
    
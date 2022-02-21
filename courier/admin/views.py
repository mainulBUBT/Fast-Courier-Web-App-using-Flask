from flask import Blueprint, redirect, request, render_template, url_for, session, flash
from flask_login import login_user, current_user
from functools import wraps
from sqlalchemy.sql import func

from courier import db
from courier.admin.forms import LoginForm
from courier.models import Merchant, DeliveryInfo, Parcel, User, ReturnParcel



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


@admin.route('/return_parcels', methods=['GET', 'POST'])
def return_parcels():

    return_search = ''
    return_list = ''
    reason_sql = ''

    page = request.args.get('page',1,type=int)

    if request.method == 'POST':
        if 'search' in request.form:
            track_number = int(request.form['track_number'])
            return_search = db.session.query(DeliveryInfo.receiver_name,DeliveryInfo.receiver_number, DeliveryInfo.receiver_address, DeliveryInfo.delivery_area, Parcel.delivery_man, Parcel.id, Parcel.parcel_status, DeliveryInfo.receiver_number).join(Parcel).filter(Parcel.id == track_number , Parcel.parcel_status == 'Return to Hub')
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
                return redirect(url_for('admin.return_parcels'))

        elif 'report_2' in request.form:
            parcel_id = request.form['parcel_id']
            reason = request.form['message']
            
            add_reason = ReturnParcel(parcel_id=parcel_id, reason=reason)
            db.session.add(add_reason)
            db.session.commit()
            flash('Reported reason for return the parcel', 'danger')
            return redirect(url_for('admin.return_parcels')) 

        elif 'report_1' in request.form:
            reason_id = request.form['reason_id']
            print(reason_id)
            parcel_id = request.form['parcel_id']
            reason = request.form['message']
            
            update_reason = ReturnParcel.query.filter_by(id=reason_id).first()
            print(update_reason)
            if update_reason:
                update_reason.parcel_id = parcel_id
                update_reason.reason = reason
                db.session.commit()
                flash('Reported reason for return the parcel', 'danger')
                return redirect(url_for('admin.return_parcels')) 
    else:
        return_list= db.session.query(DeliveryInfo.receiver_name,DeliveryInfo.receiver_number, DeliveryInfo.receiver_address, DeliveryInfo.delivery_area, Parcel.delivery_man, Parcel.id, Parcel.parcel_status,DeliveryInfo.receiver_number).join(Parcel).filter(Parcel.parcel_status == 'Return to Hub').order_by(DeliveryInfo.book_date.asc()).paginate(page=page,per_page=8)
        
        reason_sql = db.session.query(ReturnParcel.id , ReturnParcel.parcel_id, ReturnParcel.reason ,ReturnParcel.updated_date).join(Parcel).filter(Parcel.id == ReturnParcel.parcel_id)
        # for row in reason_sql:
        #     # return_parcel_id = row.parcel_id
        #     # reason_message = row.reason
        #     print(row.parcel_id)

    return render_template('return_parcels.html', return_list = return_list, return_search=return_search, reason_sql = reason_sql)

@admin.route('/merchant_details', methods=['GET', 'POST'])
def merchant_details():

    earn_sql = ''
    due_charge = ''
    user_sqls = ''
    

    user_search = ''
    due_charge_s=''
    earn_sql_s = ''

    page = request.args.get('page',1,type=int)
    
    if request.method == 'POST':
        if 'search' in request.form:
            name = request.form['name']
            earn_sql_s = db.session.query(Parcel.merchant_id, func.sum(Parcel.charge+Parcel.due_charge).label('earn')).filter(Parcel.pay_status == '1', Parcel.parcel_status=='delivered', Parcel.merchant_id==User.id).group_by(Parcel.merchant_id)
            due_charge_s = db.session.query(Parcel.merchant_id, func.sum(Parcel.user_balance).label('balance_clearence'), func.sum(Parcel.due_charge).label('due_charge')).filter(Parcel.pay_status == '0', Parcel.merchant_id==User.id)
            # user_sql = db.session.query(User.id, User.username, User.email, User.mobile_number, func.sum(Parcel.charge+Parcel.due_charge).label('earn'),func.sum(Parcel.due_charge).label('charge'), Merchant.balance, Merchant.bank_number, Merchant.bkash_number).filter(User.id == Parcel.merchant_id, User.id == Merchant.merchant_id).filter(Parcel.merchant_id==Merchant.merchant_id, Parcel.pay_status=='1', Parcel.parcel_status=='delivered').order_by(Merchant.merchant_id.asc()).paginate(page=page,per_page=8)
            user_search = db.session.query(User.id, User.username, User.email, User.mobile_number, Merchant.balance, Merchant.bank_number, Merchant.bkash_number).filter(User.id == Merchant.merchant_id, User.roles=='merchant', User.username==name)
            

        elif 'update' in request.form:
            user_id = request.form['update']
            update_sql = Merchant.query.filter_by(merchant_id = user_id).first()
            if update_sql and user_id is not None:
                balance_sql = db.session.query(func.sum(Parcel.user_balance).label('user_balance')).filter(Parcel.pay_status == '1', Parcel.merchant_id == user_id).first()
                update_sql.balance = balance_sql.user_balance
                
                if update_sql.balance is not None:
                    db.session.commit()
                    flash(f'Updated user balance {update_sql.balance} Taka added!', 'danger')
                    return redirect(url_for('admin.merchant_details'))
                else:
                    flash(f'User balance is {update_sql.balance}! no changes applied.', 'danger')
                    return redirect(url_for('admin.merchant_details'))
        elif 'edit_user':
            flash('got it')
            return redirect(url_for('admin.merchant_details'))
    else:
        earn_sql = db.session.query(Parcel.merchant_id, func.sum(Parcel.charge+Parcel.due_charge).label('earn')).filter(Parcel.pay_status == '1', Parcel.parcel_status=='delivered', Parcel.merchant_id==User.id).group_by(Parcel.merchant_id)
        due_charge = db.session.query(Parcel.merchant_id, func.sum(Parcel.user_balance).label('balance_clearence'), func.sum(Parcel.due_charge).label('due_charge')).filter(Parcel.pay_status == '0', Parcel.merchant_id==User.id).group_by(Parcel.merchant_id)
        # user_sql = db.session.query(User.id, User.username, User.email, User.mobile_number, func.sum(Parcel.charge+Parcel.due_charge).label('earn'),func.sum(Parcel.due_charge).label('charge'), Merchant.balance, Merchant.bank_number, Merchant.bkash_number).filter(User.id == Parcel.merchant_id, User.id == Merchant.merchant_id).filter(Parcel.merchant_id==Merchant.merchant_id, Parcel.pay_status=='1', Parcel.parcel_status=='delivered').order_by(Merchant.merchant_id.asc()).paginate(page=page,per_page=8)
        user_sqls = db.session.query(User.id, User.username, User.email, User.mobile_number, Merchant.balance, Merchant.bank_number, Merchant.bkash_number).filter(User.id == Merchant.merchant_id, User.roles=='merchant').order_by(Merchant.merchant_id.asc()).paginate(page=page,per_page=6)
        

    return render_template('merchant_details.html', user_sql=user_sqls, earn_sql=earn_sql, due_charge=due_charge, user_search = user_search, due_charge_s = due_charge_s, earn_sql_s = earn_sql_s)
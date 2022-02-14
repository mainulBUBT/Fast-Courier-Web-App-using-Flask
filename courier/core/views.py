from flask import redirect, render_template,request, Blueprint, url_for, flash, session, make_response
import pdfkit

from courier.models import DeliveryInfo, Merchant, Parcel, User
from courier import db


core = Blueprint('core', __name__, template_folder='templates')


@core.route('/')
def index():

    return render_template('index.html')

@core.route('/invoice/<int:id>', methods=['GET', 'POST'])
def invoice(id):
    merchant_id =''
    dates = ''
    delivery_id = ''

    if request.method == 'POST':
        track_id = id
        parcel_pdf = db.session.query(DeliveryInfo.delivery_area, DeliveryInfo.receiver_name,DeliveryInfo.receiver_address,  DeliveryInfo.collectable_amount,DeliveryInfo.book_date, Parcel.id, Parcel.delivery_man, Parcel.parcel_status, Parcel.parcel_date, Parcel.merchant_id, Parcel.charge, Parcel.delivery_id).join(Parcel).filter(Parcel.id == track_id)
        
        for id in parcel_pdf:
            merchant_id = id.merchant_id
            dates = id.book_date
            delivery_id = id.delivery_id
            print(id)
        user_info = db.session.query(User.username, User.mobile_number, Merchant.pickup_address).join(Merchant).filter(Merchant.id == merchant_id, User.id == merchant_id)
    
        rendered = render_template('invoice.html', parcel_pdf = parcel_pdf, user_info = user_info,dates = dates, merchant_id=merchant_id, delivery_id=delivery_id)
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdf = pdfkit.from_string(rendered,False, configuration=config)

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
    
        return response
        
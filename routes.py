from flask import render_template, flash, redirect, url_for, request, jsonify, send_file, send_from_directory
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse
from app import app, db
from app.models import *
from app.utils import NullableDateField, login_required
from datetime import date, datetime
from dateutil.parser import parse, isoparse
from flask_wtf import FlaskForm
from flask_table import Table, Col, BoolCol, LinkCol, DatetimeCol
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, DecimalField, \
    SelectMultipleField, IntegerField, FloatField, TextAreaField
from wtforms.ext.dateutil.fields import DateTimeField
from wtforms.validators import DataRequired
import pandas as pd
import os


# DASHBOARD
@app.route('/', methods=['GET', 'POST'])
@login_required([0, 1, 2, 3])
def index():
    return render_template('index.html', user=current_user)


# BEGIN LOGIN & LOGOUT FLOW


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page handling
    
    Returns:
        Rendered HTML Template or redirect: Render login page. If valid login, redirects to desired page, else render login page again.
    """

    form = LoginForm()
    if form.validate_on_submit():
        user = Personnel.query.filter_by(employee_id=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Authentication Failed')
            # return redirect(url_for('login'))
            return render_template('login.html', title='Sign In', form=form)
        if not user.account_active:
            flash('Account Disabled')
            # return redirect(url_for('login'))
            return render_template('login.html', title='Sign In', form=form)
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login0.html', title='Sign In', form=form)


class LoginForm(FlaskForm):
    """
        LoginForm is used to create the login page. 
    """
    # Username of personnel trying to login
    username = StringField('Username', validators=[DataRequired()])
    # Password of personnel trying to login
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


@app.route('/logout')
def logout():
    """Logs out user
    
    Returns:
        redirect: to login page or another page to be determined
    """

    # TODO: CREATE LOGOUT PAGE TEMPLATE
    logout_user()
    return redirect(url_for('login'))


# END LOGIN & LOGOUT FLOW
# BEGIN PERSONNEL PAGES


@app.route('/personnel', methods=['GET', 'POST'])
@login_required([0])
def personnelhub():
    """ 
    Personnel hub page
    Return: 
        HTML file type: The return value is a rendered template containing a table listing all the personnel
    """
    personneltable = PersonnelTable(Personnel.query.all(), classes=["table"], thead_classes=["thead-dark"])
    return render_template('personnelhub.html', personneltable=personneltable, user=current_user)


class PersonnelTable(Table):
    """
        PersonnelTable is used to build and format PersonnelHub.

        Attriubutes:
            account_active: boolean value indicating if the account is still
            active
            fullname: A string representing the fullname of the personnel
            position: A string representing the position the personnel has
            at the company
            category:
            employee_id: An integer that is used as a unique identifier for the employee

    """
    padded_id = Col('№', th_html_attrs={'class': 'personnel-id-col-head personnel-table-head'})
    # padded_id = LinkCol('№', 'personnelpage', url_kwargs=dict(employee_id='employee_id'), text_fallback=)
    account_active = BoolCol('Active', yes_display='&#10003;', no_display='&#10007;',
                             th_html_attrs={'class': 'personnel-active-col-head personnel-table-head'},
                             td_html_attrs={'class': 'personnel-active-item'})
    fullname = Col('Name', th_html_attrs={'class': 'personnel-name-col-head personnel-table-head'})
    position = Col('Position', th_html_attrs={'class': 'personnel-position-col-head personnel-table-head'})
    category_text = Col('Category', th_html_attrs={'class': 'personnel-category-col-head personnel-table-head'})
    employee_id = LinkCol('View', 'personnelpage', url_kwargs=dict(employee_id='employee_id'),
                          text_fallback=u"\U0001F441",
                          th_html_attrs={'class': 'personnel-view-col-head personnel-table-head d-print-none'},
                          td_html_attrs={'class': 'personnel-view-item d-print-none'})

    def sort_url(self, col_id, reverse=False):
        pass


@app.route('/personnel/create', methods=['GET', 'POST'])
@login_required([0])
def createpersonnel():
    """This function is used for creating a personnel using the CreatePersonnelForm
    
    Returns:
        rendered template or redirect: Renders create personnel template, if successful 
        submission redirects to personnel_hub
    """

    form = CreatePersonnelForm()
    if form.validate_on_submit():
        form_data = request.form
        person = Personnel()
        person.first_name = form_data['first_name']
        person.middle_i = form_data['middle_name']
        person.last_name = form_data['last_name']
        person.position = form_data['position']
        person.category = int(form_data['category'])

        person_start_date = form_data['start_date']
        person_start_date = datetime.strptime(person_start_date, "%Y-%m-%d")
        person_start_date = person_start_date.date()
        datetime.combine(person_start_date, datetime.min.time())
        person.start_time = person_start_date

        if form_data['end_date'] is not '':
            person_end_date = form_data['end_date']
            person_end_date = datetime.strptime(person_end_date, "%Y-%m-%d")
            person_end_date = person_end_date.date()
            datetime.combine(person_end_date, datetime.min.time())
            person.end_time = person_end_date

        person.rate = float(form_data['rate'])
        person.address = form_data['address']
        person.phone = form_data['phone']
        person.password_plain = form_data['password_plain']

        db.session.add(person)
        db.session.commit()

        return redirect(url_for('personnelhub'))
    return render_template("createpersonnel.html", form=form, user=current_user)


class CreatePersonnelForm(FlaskForm):
    """
        CreatePersonnelForm is used to create a personnel form. This form
        then can be used to store personnel data for viewing by the user. This
        form also allows the user to add new personnel entries.

        Attributes:
            first_name: A string representing the first name of the personnel
            middle_name: A string representing the middle name of the personnel
            last_name: A string representing the last name of the personnel
            position: A string indicating the position the personnel is within
            the company
            category:
            start_date: An integer representing the date the personnel started
            at the company
            end_date: An integer date of the date the personnel ended 
            at the company (if applicable)
            rate: A float of the pay rate for the employee(Salary)
            address: A string representing the address of the employee
            phone: A integer number of length 10 to represent a phone number 
    """
    first_name = StringField('First Time', validators=[DataRequired()])
    middle_name = StringField('Middle Name')
    last_name = StringField('Last Name', validators=[DataRequired()])
    position = StringField('Job Title', validators=[DataRequired()])
    category = SelectField('Category', choices=[('0', 'Back Office'), ('1', 'Shipping Manager'), ('2', 'Maintenance'),
                                                ('3', 'Driver')])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = NullableDateField('End Date')
    rate = DecimalField('Salary', validators=[DataRequired()], places=2)
    address = StringField('Address', validators=[DataRequired()])
    phone = StringField('Telephone', validators=[DataRequired()])
    password_plain = PasswordField('Password', validators=[DataRequired()])


@app.route('/personnel/<employee_id>', methods=['GET', 'POST'])
@login_required([0])
def personnelpage(employee_id):
    """Personnel page for viewing or editing personnel record
    Args:
    
        employee_id (int): ID of desired employee
    
    Returns:
           rendered template: View/Edit page
    """
    person = Personnel.query.get(employee_id)
    form = EditPersonnelForm(obj=person)
    form_data = request.form

    current_shipments = Shipment.query.filter(Shipment.arrival_status == None).all()
    driver_shipments = []
    for shipment in current_shipments:
        for driver in shipment.shipment_personnel:
            if driver.employee_id == person.employee_id:
                driver_shipments.append(shipment)

    if form.validate_on_submit():
        form.populate_obj(person)

        person_start_date = form_data['start_date']
        person_start_date = datetime.strptime(person_start_date, "%Y-%m-%d")
        person_start_date = person_start_date.date()
        datetime.combine(person_start_date, datetime.min.time())
        person.start_time = person_start_date

        if form_data['end_date'] is not '':
            person_end_date = form_data['end_date']
            person_end_date = datetime.strptime(person_end_date, "%Y-%m-%d")
            person_end_date = person_end_date.date()
            datetime.combine(person_end_date, datetime.min.time())
            person.end_time = person_end_date
        else:
            person.end_time = None

        db.session.add(person)
        db.session.commit()
    start_date = person.start_time
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = person.end_time
    if end_date is not None:
        end_date = end_date.strftime("%Y-%m-%d")
    else:
        end_date = ''
    return render_template("editpersonnel.html", form=form, person=person, start_date=start_date, end_date=end_date,
                           user=current_user, driver_shipments=driver_shipments)


class EditPersonnelForm(FlaskForm):
    """
    EditPersonnelForm is used to edit an existing personnel entry.

    Attributes:
        first_name: A string representing the first name of the personnel
        middle_i: A string representing the middle initial of the personnel
        last_name: A string representing the last name of the personnel
        position: A string indicating the position the personnel is within
        the company
        category:
        start_date: An integer representing the date the personnel started
        at the company
        end_date: An integer date of the date the personnel ended 
        at the company (if applicable)
        rate: A float of the pay rate for the employee(Salary)
    """
    first_name = StringField('First Time', validators=[DataRequired()])
    middle_i = StringField('Middle Name')
    last_name = StringField('Last Name', validators=[DataRequired()])
    position = StringField('Job Title', validators=[DataRequired()])
    category = SelectField('Category', choices=[('0', 'Back Office'), ('1', 'Shipping Manager'), ('2', 'Maintenance'),
                                                ('3', 'Driver')])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = NullableDateField('End Date')
    rate = DecimalField('Salary', validators=[DataRequired()], places=2)
    address = StringField('Address', validators=[DataRequired()])
    phone = StringField('Telephone', validators=[DataRequired()])


@app.route('/personnel/<employee_id>/password', methods=['GET', 'POST'])
def setpassword(employee_id):
    """Page/Modal for changing exisisting password.

    Used on both personnel page and profile page
    Args:
    
        employee_id (int): ID of desired employee to set password
    
    Returns:
        rendered template: code for modal
    """

    person = Personnel.query.get(employee_id)
    form = ChangePasswordForm(obj=person)
    if form.validate_on_submit():
        form_data = request.form
        person.password_plain = form_data['password_plain']
        db.session.add(person)
        db.session.commit()
        return jsonify(status='ok')
    return render_template('setpasswordmodal.html', form=form, person=person, user=current_user)


class ChangePasswordForm(FlaskForm):
    """
        ChangePasswordForm is used to create a page to change your password.
        
        Attributes:
            password_plain: Password field on the flask form
    """
    password_plain = PasswordField("Password", validators=[DataRequired()])


# END PERSONNEL PAGES
# BEGIN SHIPMENTS PAGES


@app.route('/shipments', methods=['GET', "POST"])
@login_required([0, 1, 3])
def shipmentshub():
    """Page for viewing shipments

    Returns:
        rendered template: code for page
    """
    form = FilterShipmentForm()
    if request.args.get('filter') == 'incoming':
        shipmenttable = ShipmentTable(Shipment.query.order_by(Shipment.depart_time.desc()).filter_by(shipment_type=0).all(),
                                      classes=["table"], thead_classes=["thead-dark"])
    elif request.args.get('filter') == 'outgoing':
        shipmenttable = ShipmentTable(Shipment.query.order_by(Shipment.depart_time.desc()).filter_by(shipment_type=1).all(),
                                      classes=["table"], thead_classes=["thead-dark"])
    else:
        shipmenttable = ShipmentTable(Shipment.query.order_by(Shipment.depart_time.desc()).all(), classes=["table"],
                                  thead_classes=["thead-dark"])

    return render_template('shipmenthub.html', form=form, shipmenttable=shipmenttable, user=current_user)


class FilterShipmentForm(FlaskForm):
    filter = SelectField("filter", choices=[('all', 'All'), ('incoming', 'Incoming'), ('outgoing', 'Outgoing')])


@app.route('/myshipments', methods=['GET', 'POST'])
@login_required([3])
def myshipments():
    if current_user.category == 3:
        form = FilterShipmentForm()
        myships = []

        if request.args.get('filter') == 'incoming':
            for s in Shipment.query.filter_by(shipment_type=0).all():
                if current_user in s.shipment_personnel:
                    myships.append(s)
            shipmenttable = ShipmentTable(myships, classes=["table"], thead_classes=["thead-dark"])
        elif request.args.get('filter') == 'outgoing':
            for s in Shipment.query.filter_by(shipment_type=1).all():
                if current_user in s.shipment_personnel:
                    myships.append(s)
            shipmenttable = ShipmentTable(myships, classes=["table"], thead_classes=["thead-dark"])
        else:
            for s in Shipment.query.all():
                if current_user in s.shipment_personnel:
                    myships.append(s)
            shipmenttable = ShipmentTable(myships, classes=["table"], thead_classes=["thead-dark"])
    else:
        flash('You cannot access this page.')
        return redirect(url_for('index'))
    return render_template('myshipments.html', form=form, shipmenttable=shipmenttable, user=current_user)

class ShipmentTable(Table):
    """
        ShipmentTable is used to build and format the ShipmentHub
        
        Attributes:
            padded_id:
            confirmed: A boolean value to represent if the shipment has been confirmed
            shipment_type:A boolean column to show whether the shipment is incoming or
            outgoing
            friendly_departure:
            friendly_arrival:
            source: A string to represent who sent or is sending the shipment
            destination: A string to represent who received or is receiving the shipment 
            ship_id: An integer number to uniquely identify shipments 
    """

    padded_id = Col('№', th_html_attrs={'class': 'shipment-id-col-head shipment-table-head'},
                    td_html_attrs={'data-title': '№'})
    # delivery confirmation
    confirmed = BoolCol('', no_display='', yes_display='&#10003;',
                        th_html_attrs={'class': 'shipment-confirmed-col-head d-print-none'},
                        td_html_attrs={'class': 'shipment-confirmed-item d-print-none'})
    # the type of shipment (incoming or outgoing)
    shipment_type = BoolCol('Type', no_display='Incoming ↙', yes_display='Outgoing ↗',
                            th_html_attrs={'class': 'shipment-type-col-head shipment-table-head'},
                            td_html_attrs={'class': 'shipment-type-item'})
    friendly_departure = Col('Departure', th_html_attrs={'class': 'shipment-depart-col-head shipment-table-head'})
    friendly_arrival = Col('Estimated Arrival',
                           th_html_attrs={'class': 'shipment-arrival-col-head shipment-table-head'})
    # Source location of where the shipment came from
    source = Col('Source', th_html_attrs={'class': 'shipment-source-col-head shipment-table-head'},
                 td_html_attrs={'class': 'shipment-source-col-item'})
    # Where the shipment is being sent to
    destination = Col('Destination', th_html_attrs={'class': 'shipment-destination-col-head shipment-table-head'},
                      td_html_attrs={'class': 'shipment-destination-col-item'})
    # Unique identifier for the shipment
    ship_id = LinkCol('View', 'shipmentpage', url_kwargs=dict(shipment_id='ship_id'),
                      text_fallback=u"\U0001F441",
                      th_html_attrs={'class': 'shipment-view-col-head shipment-table-head d-print-none'},
                      td_html_attrs={'class': 'shipment-view-item d-print-none'})

    def sort_url(self, col_id, reverse=True):
        pass


@app.route('/shipments/create', methods=['GET', 'POST'])
@login_required([0, 1])
def createshipment():
    """Page that allows user to create a shipment

    Returns:
        rendered template: code for page
    """
    form = CreateShipmentForm()
    form.drivers.choices = [(d.padded_id, d.fullname) for d in
                            Personnel.query.filter(Personnel.category == 3).order_by(Personnel.last_name)]
    form.vehicle_id.choices = [("", "")] + [(d.padded_id, d.vehicle_info) for d in Vehicle.query]
    if form.validate_on_submit():
        form_data = request.form
        shipment = Shipment()
        shipment_type = form_data['shipment_type']
        if shipment_type == '1':
            shipment.shipment_type = True
            manifest = Manifest()
            db.session.add(manifest)
            db.session.commit()
            shipment.manifest_id = manifest.manifest_id
        else:
            shipment.shipment_type = False
            purchase_order = PurchaseOrder()
            db.session.add(purchase_order)
            db.session.commit()
            shipment.po_id = purchase_order.po_id
        shipment.source_company = form_data['source_company']
        shipment.source_address = form_data['source_address']
        shipment.destination_company = form_data['destination_company']
        shipment.destination_address = form_data['destination_address']
        depart_time = form_data['depart_time']
        depart_time = isoparse(depart_time)
        shipment.depart_time = depart_time
        est_arrival_time = form_data['est_time_arrival']
        est_arrival_time = isoparse(est_arrival_time)
        shipment.est_time_arrival = est_arrival_time
        drivers_data = form.drivers.data
        for driver in drivers_data:
            driver = Personnel.query.get(int(driver))
            shipment.shipment_personnel.append(driver)
        shipment.vehicle_id = int(form.vehicle_id.data)
        db.session.add(shipment)
        db.session.commit()
        return redirect(url_for('shipmentshub'))
    return render_template('createshipment.html', user=current_user, form=form)


class CreateShipmentForm(FlaskForm):
    """
        CreateShipmentForm is used to create a shipment form. This form
        then can be used to store shipment data for viewing by the user. This
        form also allows the user to add new equipment entries.
    
        Attributes:
            shipment_type:A boolean column to show whether the shipment is incoming or
            outgoing
            source_company: A field that takes a  string to represent who sent or is sending the shipment
            source_address: A field that takes a string of the address of the source company
            destination_company: A field that takes a string to represent who received or is receiving the shipment 
            destination_address: A field that takes a string of the destination address
            est_time_arrival: A date/time field
            vehicle_id: A field that takes an integer of the vehicle ID delivering the shipment
            drivers: A field which allows you to select multiple drivers 
    """
    shipment_type = SelectField("Shipment Type", choices=[('0', 'Incoming ↙'), ('1', 'Outgoing ↗')])
    source_company = StringField('Source Company', validators=[DataRequired()])
    source_address = StringField('Source Address', validators=[DataRequired()])
    destination_company = StringField('Destination Company', validators=[DataRequired()])
    destination_address = StringField('Destination Address', validators=[DataRequired()])
    depart_time = DateTimeField('Departure Time', validators=[DataRequired()], display_format='%Y-%m-%d %H:%M')
    est_time_arrival = DateTimeField('Estimated Arrival Time', validators=[DataRequired()],
                                     display_format='%Y-%m-%d %H:%M')
    vehicle_id = SelectField("Vehicle", validators=[DataRequired()])
    drivers = SelectMultipleField("Driver")


@app.route('/shipments/<shipment_id>', methods=['GET', 'POST'])
@login_required([0, 1, 3])
def shipmentpage(shipment_id):
    """Page/Modal for shipments.
    Args:
    
        shipment_id (int): ID of desired shipment 
    
    Returns:
        rendered template: code for modal
    """
    shipment = Shipment.query.get(shipment_id)
    form = EditShipmentForm(obj=shipment)
    form.drivers.choices = [(d.padded_id, d.fullname) for d in
                            Personnel.query.filter(Personnel.category == 3).order_by(Personnel.last_name)]
    form.vehicle_id.choices = [("", "")] + [(d.padded_id, d.vehicle_info) for d in Vehicle.query]

    drivers = []
    for driver in shipment.shipment_personnel:
        drivers.append(driver.padded_id)

    vehicle_id = Vehicle.query.get(shipment.vehicle_id)
    vehicle_id = vehicle_id.padded_id
    vehicle_id = [vehicle_id]

    if form.validate_on_submit():
        form.populate_obj(shipment)
        for driver in shipment.shipment_personnel:
            shipment.shipment_personnel.remove(driver)
        drivers_data = form.drivers.data
        for driver in drivers_data:
            driver = Personnel.query.get(int(driver))
            shipment.shipment_personnel.append(driver)

        db.session.add(shipment)
        db.session.commit()
        return redirect('shipments')

    if request.method == 'POST' and request.values.get('action') == 'toggleShipmentStatus':
        if shipment.arrival_status:
            shipment.arrival_status = None
        else:
            shipment.arrival_status = datetime.now()

    start_date = shipment.depart_time
    start_date = start_date.strftime("%Y-%m-%d %H:%m")
    end_date = shipment.est_time_arrival
    end_date = end_date.strftime("%Y-%m-%d %H:%m")

    return render_template("editshipment.html", form=form, shipment=shipment, start_date=start_date,
                           end_date=end_date, user=current_user, drivers=drivers, vehicle_id=vehicle_id)


class EditShipmentForm(FlaskForm):
    """
        EditShipmentForm is used to edit the shipment form.
        Attributes:
            shipment_type:A boolean column to show whether the shipment is incoming or
            outgoing
            source_company: A field that takes a  string to represent who sent or is sending the shipment
            source_address: A field that takes a string of the address of the source company
            destination_company: A field that takes a string to represent who received or is receiving the shipment 
            destination_address: A field that takes a string of the destination address
            est_time_arrival: a date/time field
            vehicle_id: A field that takes an integer of the vehicle ID delivering the shipment
            drivers: A field which allows you to select multiple drivers 
    """
    source_company = StringField('Source Company', validators=[DataRequired()])
    source_address = StringField('Source Address', validators=[DataRequired()])
    destination_company = StringField('Destination Company', validators=[DataRequired()])
    destination_address = StringField('Destination Address', validators=[DataRequired()])
    depart_time = DateTimeField('Departure Time', validators=[DataRequired()], display_format='%Y-%m-%d %H:%M')
    est_time_arrival = DateTimeField('Estimated Arrival Time', validators=[DataRequired()],
                                     display_format='%Y-%m-%d %H:%M')
    vehicle_id = SelectField("Vehicle", validators=[DataRequired()])
    drivers = SelectMultipleField("Driver")


@app.route('/shipments/<shipment_id>/manifest', methods=['GET', 'POST'])
@login_required([0, 1, 3])
def shipmentmanifest(shipment_id):
    """  
        Depending on what the user does shipmentmanifest will:
        - create a new manifest
        - delete a manifest
        - edit manifest
        - toggle payment

        Returns:
            rendered template: code for shipment manifest
    """
    if request.method == 'POST':
        shipment = Shipment.query.get(shipment_id)
        manifest = Manifest.query.get(shipment.manifest_id)
        if request.values.get('action') == 'new':
            item = Item()
            manifest.items.append(item)
            db.session.add(manifest)
            db.session.commit()
            return jsonify(
                action='new',
                id=item.item_id
            )
        elif request.values.get('action') == 'delete':
            deletable = request.values.get('id')
            deletable = Item.query.get(int(deletable))
            manifest.items.remove(deletable)
            db.session.delete(deletable)
            db.session.add(manifest)
            db.session.commit()
            return jsonify(
                action='delete',
                id=deletable.item_id
            )
        elif request.values.get('action') == 'edit' and request.values.get('id'):
            edit = request.values.get('id')
            edit = Item.query.get(int(edit))
            edit.brand = request.values.get('brand')
            edit.description = request.values.get('description')
            edit.cost = float(request.values.get('cost'))
            edit.number = int(request.values.get('quantity'))
            db.session.add(edit)
            db.session.add(manifest)
            db.session.commit()
            return jsonify(
                action='edit',
                id=edit.item_id,
                brand=edit.brand,
                description=edit.description,
                cost=edit.cost,
                quantitiy=edit.number
            )
        elif request.values.get('action') == 'togglePayment':
            if shipment.payment_status:
                shipment.payment_status = False
            else:
                shipment.payment_status = True
            db.session.add(shipment)
            db.session.commit()
            return jsonify(
                action='togglePayment',
                paymentStatus=shipment.payment_status
            )
    form = ShippingAndHandlingForm()
    shipment = Shipment.query.get(shipment_id)
    manifest = Manifest.query.get(shipment.manifest_id)
    manifest_table = ManifestTable(manifest.items, classes=["table table-hover"], thead_classes=[""])
    if form.validate_on_submit():
        form_data = request.form
        manifest.shipping_handling = float(form_data['shipping_and_handling'])
        db.session.add(manifest)
        db.session.commit()
        return jsonify(
            # total=manifest.total
            action='okay'
        )
    if request.values.get('action') == 'refresh':
        return manifest_table.__html__()
    if request.values.get('action') == 'sh':
        return str(manifest.total)
    return render_template('manifestview.html', user=current_user, shipment=shipment, manifest=manifest,
                           manifest_table=manifest_table, form=form)


class ManifestTable(Table):
    """ 
        ManifestTable is used to build and format ManifestHub 

        Attributes:
            table_id: An ID to unique to that table
            item_id: An integer to uniquely identify the item being ordered
            brand: A string to represent the brand of the item
            description: A string to describe the item
            cost: A float value of the item before shipping and handling
            number: An integer value to represent the quantity being ordered
            total_cost: A float value of the total cost of the item including shipping and handling
    """
    # Table ID for manifest
    table_id = 'manifest_table'
    # Unique identifier for the item being ordered
    item_id = Col('№')
    # The brand of the item
    brand = Col('Item Brand', td_html_attrs={'class': 'align-middle manifest-brand-col-item'})
    # A quick desciption of what the item is
    description = Col('Description', td_html_attrs={'class': 'align-middle manifest-description-col-item'})
    # friendly_cost = Col('Item Unit Cost', td_html_attrs={'class': 'align-middle text-right manifest-cost-col-item'}, th_html_attrs={'class': 'text-right'})
    cost = Col('Item Unit Price', td_html_attrs={'class': 'align-middle text-right manifest-cost-col-item'},
               th_html_attrs={'class': 'text-right'})
    # Quanitity of the item
    number = Col('Quantity', td_html_attrs={'class': 'align-middle text-right manifest-quantity-col-item'},
                 th_html_attrs={'class': 'text-right'})
    # friendly_total_cost = Col('Cost', td_html_attrs={'class': 'align-middle text-right manifest-total-col-item'},
    #                           th_html_attrs={'class': 'text-right'})
    # Total cost of the item
    total_cost = Col('Cost', td_html_attrs={'class': 'align-middle text-right manifest-total-col-item'},
                     th_html_attrs={'class': 'text-right'})


@app.route('/shipments/<shipment_id>/purchase-order', methods=['GET', 'POST'])
@login_required([0, 1, 3])
def shipmentpurchaseorder(shipment_id):
    """Page/Modal for shipment purchase orders.

    Args:
    
        shipment_id (int): ID of desired shipement to view purchase order.
    
    Returns:
        rendered template: code for modal
    """
    if request.method == 'POST':
        shipment = Shipment.query.get(shipment_id)
        purchase_order = PurchaseOrder.query.get(shipment.po_id)
        if request.values.get('action') == 'new':
            item = Item()
            purchase_order.items.append(item)
            db.session.add(purchase_order)
            db.session.commit()
            return jsonify(
                action='new',
                id=item.item_id
            )
        elif request.values.get('action') == 'delete':
            deletable = request.values.get('id')
            deletable = Item.query.get(int(deletable))
            purchase_order.items.remove(deletable)
            db.session.delete(deletable)
            db.session.add(purchase_order)
            db.session.commit()
            return jsonify(
                action='delete',
                id=deletable.item_id
            )
        elif request.values.get('action') == 'edit' and request.values.get('id'):
            edit = request.values.get('id')
            edit = Item.query.get(int(edit))
            edit.brand = request.values.get('brand')
            edit.description = request.values.get('description')
            edit.cost = float(request.values.get('cost'))
            edit.number = int(request.values.get('quantity'))
            edit.status = int(request.values.get('status'))
            db.session.add(edit)
            db.session.add(purchase_order)
            db.session.commit()
            return jsonify(
                action='edit',
                id=edit.item_id,
                brand=edit.brand,
                description=edit.description,
                status=edit.status_text,
                cost=edit.cost,
                quantitiy=edit.number
            )
        elif request.values.get('action') == 'togglePayment':
            if shipment.payment_status:
                shipment.payment_status = False
            else:
                shipment.payment_status = True
            db.session.add(shipment)
            db.session.commit()
            return jsonify(
                action='togglePayment',
                paymentStatus=shipment.payment_status
            )
    form = ShippingAndHandlingForm()
    shipment = Shipment.query.get(shipment_id)
    purchase_order = PurchaseOrder.query.get(shipment.po_id)
    purchase_order_table = PurchaseOrderTable(purchase_order.items, classes=["table table-hover"], thead_classes=[""])
    if form.validate_on_submit():
        form_data = request.form
        purchase_order.shipping_handling = float(form_data['shipping_and_handling'])
        db.session.add(purchase_order)
        db.session.commit()
        return jsonify(
            # total=manifest.total
            action='okay'
        )
    if request.values.get('action') == 'refresh':
        return purchase_order_table.__html__()
    if request.values.get('action') == 'sh':
        return str(purchase_order.total)
    return render_template('purchaseorderview.html', user=current_user, shipment=shipment,
                           purchase_order=purchase_order, purchase_order_table=purchase_order_table, form=form)


class PurchaseOrderTable(Table):
    """
        PurchaseOrderTable is used to build and format PurchaseOrderHub.
    
            table_id: An ID that is unique to that table
            item_id: An integer to uniquely identify the item being ordered
            brand: A string to represent the brand of the item
            description: A string to describe the item
            cost: A float value of the item before shipping and handling
            number: An integer value to represent the quantity being ordered
            total_cost: A float value of the total cost of the item including shipping and handling
    """
    table_id = 'purchase_order_table'
    item_id = Col('№')
    brand = Col('Item Brand', td_html_attrs={'class': 'align-middle po-brand-col-item'})
    description = Col('Description', td_html_attrs={'class': 'align-middle po-description-col-item'})
    status_text = Col('Item Status', td_html_attrs={'class': 'align-middle po-status-col-item'})
    cost = Col('Item Unit Price', td_html_attrs={'class': 'align-middle text-right po-cost-col-item'},
               th_html_attrs={'class': 'text-right'})
    number = Col('Quantity', td_html_attrs={'class': 'align-middle text-right po-quantity-col-item'},
                 th_html_attrs={'class': 'text-right'})
    total_cost = Col('Cost', td_html_attrs={'class': 'align-middle text-right po-total-col-item'},
                     th_html_attrs={'class': 'text-right'})


class ShippingAndHandlingForm(FlaskForm):
    """
        ShippingAndHandlingForm is used to create the shipping and handling form.
        Attributes:
            shipping_and_handling: A float field for the shipping and handling cost
    """
    shipping_and_handling = FloatField('Shipping and Handling')


# END SHIPMENT PAGES
# BEGIN MAINTENANCE PAGES

class MaintenanceTable(Table):
    """
        MaintenanceTable is used to build and format MaintenanceHub.
        Attributes:
            table_id: a string to uniquely identify the table
            maintenance_type: A column for a maintenance type string
            description: A column for a description of the maintenance
            date_time: A column for date/time
    """

    table_id = 'maintenancetable'
    # added_id = Col('№', th_html_attrs={'class': 'maintenance-id-col-head maintenance-table-head'})
    padded_vehicle_id = Col('Vehicle №', td_html_attrs={'class': 'align-middle maintenance-col-item'})
    maintenance_type = Col('Maintenance Type', td_html_attrs={'class': 'align-middle maintenance-col-item'})
    date_time = Col('Maintenance Complete', td_html_attrs={'class': 'align-middle maintenance-col-item'})
    maintenance_id = LinkCol('View', 'maintenancepage',
                             url_kwargs=dict(equip_id='vehicle_id', maintenance_id='maintenance_id'),
                             text_fallback=u"\U0001F441",
                             th_html_attrs={'class': 'maintenance-view-col-head maintenance-table-head d-print-none'},
                             td_html_attrs={'class': 'maintenance-view-item d-print-none'})


@app.route('/maintenance-records', methods=['GET', 'POST'])
@login_required([0, 1, 2])
def maintenancehub():
    """Page/Modal for viewing all the maintenance records.
    
    Returns:
        rendered template: code for modal
    """
    maintenancetable = MaintenanceTable(Maintenance.query.order_by(Maintenance.date_time.desc()).all(), classes=["table"], thead_classes=["thead-dark"])
    return render_template('maintenancehub.html', maintenancetable=maintenancetable, user=current_user)


# BEGIN MAINTENANCE > PARTS PAGES

# TODO: CREATE PARTS HUB (Hassan Muhammad)
@app.route('/parts')
@login_required([0, 1, 2])
def parthub():
    """Page/Modal for viewing all the part records.
    
    Returns:
        rendered template: code for modal
    """
    parttable = PartTable(Part.query.all(), classes=["table"], thead_classes=["thead-dark"])
    return render_template('parthub.html', parttable=parttable, user=current_user)


class PartTable(Table):
    """
        PartTable is used to build and format PartHub.

        Attributes:
            padded_id: A column for
            desciption: A column for a description of the part
            brand: A column for the part brand
            inventory: A column for the companies inventory of the part
            cost: A column for the cost of the part
            special_order: A boolean column for distinguishing if the part was special ordered
            part_id: A column for the part ID
    """
    # Pad the ID
    padded_id = Col('№', th_html_attrs={'class': 'part-id-col-head part-table-head'})
    # Description of the part
    description = Col('Description', th_html_attrs={'class': 'brand-col-head part-table-head'})
    # Brand of the part
    brand = Col('Brand', th_html_attrs={'class': 'brand-col-head part-table-head'})
    # How many items that the company has in inventory
    inventory = Col('Inventory', th_html_attrs={'class': 'inventory-col-head part-table-head'})
    cost = Col('Cost', th_html_attrs={'class': 'cost-col-head part-table-head'})
    # source = Col('Source', th_html_attrs={'class': 'part-source-col-head part-table-head'},
    #              td_html_attrs={'class': 'part-source-col-item'})
    # Value to distinguish if the part was special ordered
    special_order = BoolCol('Special Order', no_display='', yes_display='&#10003;',
                            th_html_attrs={'class': 'special-order-col-head part-table-head'},
                            td_html_attrs={'class': 'special-order-item'})
    # Unique Identifier for the part
    part_id = LinkCol('View', 'partpage', url_kwargs=dict(part_id='part_id'),
                      text_fallback=u"\U0001F441",
                      th_html_attrs={'class': 'part-view-col-head part-table-head d-print-none'},
                      td_html_attrs={'class': 'part-view-item d-print-none'})

    def sort_url(self, col_id, reverse=False):
        pass


# TODO: INVESTIGATE DB PROBLEMS
@app.route('/parts/create', methods=['GET', 'POST'])
@login_required([0, 1, 2])
def createparts():
    """Page/Modal for creating a new part record.
    
    Returns:
        rendered template: code for modal
    """
    form = CreatePartsForm()

    if form.validate_on_submit():
        form_data = request.form
        part = Part()
        part.brand = form_data['brand']
        part.description = form_data['description']
        part.inventory = form_data['inventory']
        part.cost = form_data['cost']
        part.source = form_data['source']

        if form_data['special_order']:
            part.special_order = True
        else:
            part.special_order = False

        db.session.add(part)
        db.session.commit()
        return redirect(url_for('parthub'))

    return render_template('createparts.html', user=current_user, form=form)


class CreatePartsForm(FlaskForm):
    """
        CreatePartsForm is used to create a part form. This form
        then can be used to store part data for viewing by the user. This
        form also allows the user to add new part entries.

        Attributes:
            brand: A field that requires a string for the brand of the part
            description: A field that requires a string description of the part
            inventory: An integer field for the inventory of the part
            cost: A float field for the cost of the part
            source: A string field for where the part was ordered from
            special_order: A boolean field to distinguish if the part was special ordered
    """
    brand = StringField("Brand", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    inventory = IntegerField("Inventory", validators=[DataRequired()])
    cost = FloatField("Cost", validators=[DataRequired()])
    source = StringField("Source", validators=[DataRequired()])
    special_order = BooleanField("Special")


@app.route('/parts/<part_id>', methods=['GET', 'POST'])
@login_required([0, 1, 2])
def partpage(part_id):
    """Page/Modal for the part page.

    Args:
    
        part_id (int): ID of desired part to view.
    
    Returns:
        rendered template: code for modal
    """
    parts = Part.query.get(part_id)
    form = EditPartForm(obj=parts)
    form_data = request.form
    if form.validate_on_submit():
        form.populate_obj(parts)

        db.session.add(parts)
        db.session.commit()

    return render_template("editpart.html", form=form, parts=parts, user=current_user)


class EditPartForm(FlaskForm):
    """
        EditPartForm is used to edit the part form.

        Attributes:
            brand: A field that requires a string for the brand of the part
            description: A field that requires a string description of the part
            inventory: An integer field for the inventory of the part
            cost: A float field for the cost of the part
            source: A string field for where the part was ordered from
            special_order: A boolean field to distinguish if the part was special ordered
    """
    # Brand of the part
    brand = StringField("Brand", validators=[DataRequired()])
    # Description of what the part is used for 
    description = StringField("Description", validators=[DataRequired()])
    # How many the company has in stock
    inventory = IntegerField("Inventory", validators=[DataRequired()])
    # The cost of the part
    cost = FloatField("Cost", validators=[DataRequired()])
    source = StringField("Source", validators=[DataRequired()])
    special_order = BooleanField("Special")


# END PARTS PAGES

# BEGIN MAINTENANCE PAGES


# END MAINTENANCE > PARTS PAGES
# BEGIN MAINTENANCE > EQUIPMENT PAGES


@app.route('/equipment', methods=['GET', "POST"])
@app.route('/maintenance', methods=['GET', "POST"])
@login_required([0, 1, 2])
def equipmenthub():
    """Page/Modal for viewing the equipment hub.

    Returns:
        rendered template: code for modal
    """
    # Populate the equipmenttable with all the equipment in the database
    equipmenttable = EquipmentTable(Vehicle.query.all(), classes=["table"], thead_classes=["thead-dark"])
    return render_template('equipmenthub.html', equipmenttable=equipmenttable, user=current_user)


class EquipmentTable(Table):
    """
        EquipmentTable is used to build and format EquipmentHub
        Attributes:
            padded_id:
            make: string column that hold the make of the vehicle
            model: string column that holds the model of the vehicle
            year: integer column that holds the year of the vehicle
            vehicle_type: string column that holds the vehicle type 
            active: Boolean column of the vehicles availability
            vin: integer column that holds the VIN of the vehicle
            vehicle_id: integer column that holds the vehicle ID that is unique to the
            company
    """
    padded_id = Col('№', th_html_attrs={'class': 'vehicle-id-col-head vehicle-table-head'})
    active = BoolCol('Active', yes_display='&#10003;', no_display='&#10007;',
                     th_html_attrs={'class': 'vehicle-active-col-head vehicle-table-head'},
                     td_html_attrs={'class': 'vehicle-active-item'})
    make = Col('Make', th_html_attrs={'class': 'make-col-head vehicle-table-head'})
    model = Col('Model', th_html_attrs={'class': 'model-col-head vehicle-table-head'})
    year = Col('Year', th_html_attrs={'class': 'year-col-head vehicle-table-head'})
    vehicle_type = Col('Type', th_html_attrs={'class': 'brand-col-head vehicle-table-head'})
    vehicle_id = LinkCol('View', 'equipmentpage', url_kwargs=dict(vehicle_id='vehicle_id'),
                         text_fallback=u"\U0001F441",
                         th_html_attrs={'class': 'vehile-view-col-head vehicle-table-head d-print-none'},
                         td_html_attrs={'class': 'vehicle-view-item d-print-none'})

    def sort_url(self, col_id, reverse=False):
        pass


@app.route('/equipment/create', methods=['GET', 'POST'])
@login_required([0, 1, 2])
def createequipment():
    """Page/Modal for creating a new equipment entry.

    Returns:
        rendered template: code for modal
    """
    form = CreateEquipmentForm()
    if form.validate_on_submit():
        form_data = request.form
        truck = Vehicle()
        truck.make = form_data['make']
        truck.model = form_data['model']
        truck.year = form_data['year']
        truck.vehicle_type = form_data['vehicle_type']
        active = form_data['active']
        if active == '1':
            truck.active = False
        else:
            truck.active = True
        truck.vin = form_data['vin']

        db.session.add(truck)
        db.session.commit()

        return redirect(url_for('equipmenthub'))
    return render_template('createequipment.html', form=form, user=current_user)


class CreateEquipmentForm(FlaskForm):
    """
        CreateEquipmentForm is used to create an equipment form. This form
        then can be used to store equipment data for viewing by the user. This
        form also allows the user to add new equipment entries.

        Attributes:
            vin: integer field that holds the VIN of the vehicle
            vehicle_type: string field that holds the vehicle type 
            make: string field that hold the make of the vehicle
            model: string field that holds the model of the vehicle
            year: integer field that holds the year of the vehicle
            active: Boolean field of the vehicles availability
            company
    """
    # Vin of the vehicle
    vin = StringField('VIN', validators=[DataRequired()])
    # The type of vehicle 
    vehicle_type = StringField('Type', validators=[DataRequired()])
    # Make of the vehicle
    make = StringField('Make', validators=[DataRequired()])
    # Model of the vehicle
    model = StringField('Model', validators=[DataRequired()])
    # Year the vehicle was made
    year = StringField('Year', validators=[DataRequired()])
    # Is the vehicle active
    active = SelectField("Active", choices=[('0', 'Active'), ('1', 'Inactive')])


@app.route('/equipment/<vehicle_id>', methods=['GET', 'POST'])
@login_required([0, 1, 2])
def equipmentpage(vehicle_id):
    """Page/Modal for the equipment page.
    Args:
        vehicle_id (int): ID of desired vehicle to view.
    
    Returns:
        rendered template: code for modal
    """
    vehicle = Vehicle.query.get(vehicle_id)
    form = EditEquipmentForm(obj=vehicle)
    form_data = request.form

    current_maintenance = Maintenance.query.filter(Maintenance.vehicle_id == vehicle.vehicle_id)
    vehicle_maintenance = []
    for maintenance in current_maintenance:
        if maintenance.vehicle_id == vehicle.vehicle_id:
            vehicle_maintenance.append(maintenance)

    form1 = AddPartsEquipmentForm(prefix='form1')

    form1.part.choices = [("", "")] + [(d.padded_id, "{} {}".format(d.brand, d.description)) for d in Part.query]

    partstable = EquipmentPartsTable(vehicle.vehicle_parts, classes=["table"], thead_classes=["thead-dark"])

    if request.method == 'POST':
        if request.values.get('action') == 'delete':
            deletable = request.values.get('id')
            deletable = Part.query.get(int(deletable))
            vehicle.vehicle_parts.remove(deletable)
            db.session.add(vehicle)
            db.session.commit()
            return jsonify(
                action='delete',
                id=deletable.part_id
            )
        elif request.form['btn'] == 'Save':
            if form.validate_on_submit():
                form.populate_obj(vehicle)
                db.session.add(vehicle)
                db.session.commit()
        elif request.form['btn'] == 'Add':
            if form1.validate_on_submit():
                if form1.part.data:
                    part = Part.query.get(form1.part.data)
                    vehicle.vehicle_parts.append(part)
                    db.session.add(vehicle)
                    db.session.commit()

    return render_template("editequipment.html", form=form, form1=form1, vehicle=vehicle, user=current_user,
                           vehicle_maintenance=vehicle_maintenance, partstable=partstable)


class EditEquipmentForm(FlaskForm):
    vin = StringField('VIN', validators=[DataRequired()])
    vehicle_type = StringField('Type', validators=[DataRequired()])
    make = StringField('Make', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    active = SelectField("Active", choices=[('0', 'Active'), ('1', 'Inactive')])


class AddPartsEquipmentForm(FlaskForm):
    part = SelectField("Part")


class EquipmentPartsTable(Table):
    table_id = 'parts_table'
    part_id = Col('ID', td_html_attrs={'class': ''})
    brand = Col('Brand', td_html_attrs={'class': 'align-middle'})
    description = Col('Brand', td_html_attrs={'class': 'align-middle'})


# END MAINTENANCE > EQUIPMENT PAGES
# BEGIN MAINTENANCE > EQUIPMENT > MAINTENANCE PAGES


@app.route('/equipment/<equip_id>/maintenance/create', methods=['GET', 'POST'])
@login_required([0, 1, 2])
def createmaintenance(equip_id):
    """Page/Modal for creating maintenance record.

    Used on both personnel page and profile page
    Args:
        equip_id (int): ID of the equip the maintenance is mapped to
    
    Returns:
        rendered template: code for modal
    """
    form = CreateMaintenanceForm()
    vehicle = Vehicle.query.get(equip_id)
    if form.validate_on_submit():
        form_data = request.form
        maintenance = Maintenance()
        maintenance.maintenance_type = form_data['maintenance_type']
        maintenance.vehicle_id = equip_id
        date_time = form_data['date_time']
        date_time = isoparse(date_time)
        maintenance.date_time = date_time
        maintenance.description = form_data['description']
        db.session.add(maintenance)
        db.session.commit()
        print(maintenance.maintenance_id)
        return redirect(url_for('maintenancepage', equip_id=equip_id, maintenance_id=maintenance.maintenance_id))
    return render_template('createmaintenace.html', user=current_user, form=form, vehicle=vehicle)


class CreateMaintenanceForm(FlaskForm):
    """
        CreateMaintenanceForm is used to create the maintenance form. This form
        then can be used to store maintenance data for viewing by the user. This
        form also allows the user to add new maintenance entries.
    
        Attributes:
            maintenance_type: string field that stores the type of maintenance that is needed 
            description: TextAreaField that is used for description of the maintenance
            date_time: DateTimeField is for storing when the maintenance was done
    """
    # The type of maintenance that is being requested
    maintenance_type = StringField('Maintenance Type', validators=[DataRequired()])
    # A description of what is needing to be fixed
    description = TextAreaField('Maintenance Description', validators=[DataRequired()])
    # the date the maintenance was done
    date_time = DateTimeField('Maintenance Time', validators=[DataRequired()], display_format='%Y-%m-%d %H:%M')


@app.route('/equipment/<equip_id>/maintenance/<maintenance_id>', methods=['GET', 'POST'])
@login_required([0, 1, 2])
def maintenancepage(equip_id, maintenance_id):
    """Page/Modal for the specified maintenance record.

    Args:
    
        maintenance_id (int): ID of desired maintenance record to view.
    
    Returns:
        rendered template: code for modal
    """
    vehicle = Vehicle.query.get(equip_id)
    maintenance = Maintenance.query.get(maintenance_id)
    form = EditMaintenanceForm(obj=maintenance, prefix='form0')
    form1 = AddPartsMaintenanceForm(prefix='form1')

    form1.part.choices = [("", "")] + [(d.padded_id, "{} {}".format(d.brand, d.description)) for d in Part.query]

    partstable = MaintenancePartsTable(maintenance.maintenance_parts, classes=["table"], thead_classes=["thead-dark"])

    if request.method == 'POST':
        if request.values.get('action') == 'delete':
            deletable = request.values.get('id')
            deletable = Part.query.get(int(deletable))
            maintenance.maintenance_parts.remove(deletable)
            db.session.add(maintenance)
            db.session.commit()
            return jsonify(
                action='delete',
                id=deletable.part_id
            )
        elif request.form['btn'] == 'Save':
            if form.validate_on_submit():
                form.populate_obj(maintenance)
                db.session.add(maintenance)
                db.session.commit()
        elif request.form['btn'] == 'Add':
            if form1.validate_on_submit():
                if form1.part.data:
                    part = Part.query.get(form1.part.data)
                    maintenance.maintenance_parts.append(part)
                    db.session.add(maintenance)
                    db.session.commit()
    return render_template("editmaintenance.html", form=form, form1=form1, maintenance=maintenance, user=current_user,
                           vehicle=vehicle, partstable=partstable)


class EditMaintenanceForm(FlaskForm):
    # The type of maintenance that is being requested
    maintenance_type = StringField('Maintenance Type', validators=[DataRequired()])
    # A description of what is needing to be fixed
    description = TextAreaField('Maintenance Description', validators=[DataRequired()])
    # the date the maintenance was done
    date_time = DateTimeField('Maintenance Time', validators=[DataRequired()], display_format='%Y-%m-%d %H:%M')


class AddPartsMaintenanceForm(FlaskForm):
    part = SelectField("Part")


class MaintenancePartsTable(Table):
    table_id = 'parts_table'
    part_id = Col('ID', td_html_attrs={'class': ''})
    brand = Col('Brand', td_html_attrs={'class': 'align-middle'})
    description = Col('Brand', td_html_attrs={'class': 'align-middle'})


# END MAINTENANCE > EQUIPMENT > MAINTENANCE PAGES
# END MAINTENANCE PAGES
# BEGIN REPORTING PAGES


class PayrollReportForm(FlaskForm):
    start_date = DateTimeField('Starting Date for Report', validators=[DataRequired()], display_format='%Y-%m-%d')
    end_date = DateTimeField('Ending Date for Report', validators=[DataRequired()], display_format='%Y-%m-%d')


@app.route('/payrollreport', methods=['GET', 'POST'])
@login_required([0])
def payrollreport():
    """Page/Modal for payroll page.

    Returns:
        rendered template: code for modal
    """
    form = PayrollReportForm()

    if form.validate_on_submit():
        form_data = request.form
        filename = "payroll_report.csv"

        start_date = form_data['start_date']
        end_date = form_data['end_date']

        employees = Personnel.query.filter(Personnel.start_time < end_date, Personnel.end_time == None).all() + \
                    Personnel.query.filter(Personnel.start_time < end_date, Personnel.end_time > start_date).all()

        monthly_rates = [e.rate / 12.0 for e in employees]
        f_names = [e.first_name for e in employees]
        l_names = [e.last_name for e in employees]
        yearly_rates = [e.rate for e in employees]
        biweekly_rates = [e.rate / 26.0 for e in employees]
        weekly_rates = [e.rate / 52.0 for e in employees]

        df = pd.DataFrame({"First Name": f_names, "Last Name": l_names, "Weekly Pay": weekly_rates,
                           "Biweekly Pay": biweekly_rates, "Monthly Pay": monthly_rates, "Yearly Pay": yearly_rates})

        # write csv without a tempfile
        path = os.path.join(app.config['TEMPFILE_DIR'], filename)
        df.to_csv(path)
        return send_from_directory(directory=app.config['TEMPFILE_DIR'], filename=filename)

    return render_template('payrollreport.html', form=form, user=current_user)


@app.route('/generatepayroll', methods=['GET'])
@login_required([0])
def generatepayroll():
    """Page/Modal for generating a payroll report.

    Returns:
        send_from_directory(): the filename with the path to where the file will be stored
    """
    filename = "payroll_report.csv"

    employees = Personnel.query.filter_by(end_time=None).all()

    monthly_rates = [e.rate / 12.0 for e in employees]
    f_names = [e.first_name for e in employees]
    l_names = [e.last_name for e in employees]
    yearly_rates = [e.rate for e in employees]

    df = pd.DataFrame({"First Name": f_names, "Last Name": l_names,
                       "Monthly Pay": monthly_rates, "Yearly Pay": yearly_rates})

    # write csv without a tempfile
    path = os.path.join(app.config['TEMPFILE_DIR'], filename)
    df.to_csv(path, encoding='utf-8')
    return send_from_directory(directory=app.config['TEMPFILE_DIR'], filename=filename)


@app.route('/vehiclereport', methods=['GET'])
@login_required([0, 1, 2])
def vehiclereport():
    """Page/Modal for vehicle report.

    Returns:
        rendered template: code for modal
    """
    vehicles = Vehicle.query.all()
    return render_template('vehiclereport.html', vehicles=vehicles, user=current_user)


@app.route('/generatevehiclereport/<vehicle_id>', methods=['GET'])
@login_required([0, 1, 2])
def generatevehiclereport(vehicle_id):
    """Page/Modal for generating a vehicle report.

        Args:
        
            vehicle_id (int): ID of vehicle to generate a report for.
        
        Returns:
            send_from_directory(): the filename with the path to where the file will be stored
    """
    filename = "maintenance_report_vehicle" + str(vehicle_id) + ".csv"

    maintenance = Maintenance.query.filter_by(vehicle_id=vehicle_id).all()

    types = [m.maintenance_type for m in maintenance]
    descriptions = [m.description for m in maintenance]
    date_times = [m.date_time for m in maintenance]
    part_ids = [m.maintenance_parts for m in maintenance]
    ### add parts to report in string format --> "Brand Cost, Brand Cost"

    df = pd.DataFrame({"Date": date_times, "Types": types, "Description": descriptions, "Parts": part_ids})
    path = os.path.join(app.config['TEMPFILE_DIR'], filename)
    df.to_csv(path, encoding='utf-8')

    return send_from_directory(directory=app.config['TEMPFILE_DIR'], filename=filename)


class MaintenanceReportForm(FlaskForm):
    start_date = DateTimeField('Starting Date for Report', validators=[DataRequired()], display_format='%Y-%m-%d')
    end_date = DateTimeField('Ending Date for Report', validators=[DataRequired()], display_format='%Y-%m-%d')


@app.route('/maintenancereport', methods=['GET', 'POST'])
@login_required([0, 1, 2])
def maintenancereport():
    """Page/Modal for maintenance report.

    Returns:
        rendered template: code for modal
    """
    form = MaintenanceReportForm()

    if form.validate_on_submit():
        form_data = request.form
        filename = "maintenance_report.csv"

        start_date = form_data['start_date']
        end_date = form_data['end_date']

        maintenance = Maintenance.query.filter(Maintenance.date_time.between(start_date, end_date)).all()
        dates = [m.date_time for m in maintenance]
        types = [m.maintenance_type for m in maintenance]
        descriptions = [m.description for m in maintenance]
        vehicles = [Vehicle.query.filter_by(vehicle_id=m.vehicle_id).first() for m in maintenance]
        vehicle_ds = [str(v.year) + " " + str(v.make) + " " + str(v.model) + " VIN#:" + str(v.vin) for v in vehicles]
        parts = [m.maintenance_parts for m in maintenance]
        costs = [m.total() for m in maintenance]

        df = pd.DataFrame({"Date": dates, "Maintenance Type": types, "Description": descriptions,
                           "Vehicle": vehicle_ds, "Parts": parts, "Cost": costs})

        # write csv without a tempfile
        path = os.path.join(app.config['TEMPFILE_DIR'], filename)
        df.to_csv(path)
        return send_from_directory(directory=app.config['TEMPFILE_DIR'], filename=filename)

    return render_template('maintenancereport.html', form=form, user=current_user)


@app.route('/incomingreport', methods=['GET', 'POST'])
@login_required([0, 1])
def incomingreport():
    """Page/Modal for incoming report.

    Returns:
        rendered template: code for modal
    """
    shipments = Shipment.query.filter_by(shipment_type=False).all()
    return render_template('incomingreport.html', shipments=shipments, user=current_user)


@app.route('/generateincomingreport', methods=['GET'])
@login_required([0, 1])
def generateincomingreport():
    """Page/Modal for generating incoming report.

    Returns:
        send_from_directory(): A directory on the local machine to store the report.
    """
    filename = "incoming_ship_report.csv"

    shipments = Shipment.query.filter_by(shipment_type=False).all()

    arrival_status = [shipment.arrival_status for shipment in shipments]
    payment_status = [shipment.payment_status for shipment in shipments]
    depart_time = [shipment.depart_time for shipment in shipments]
    est_time_arrival = [shipment.est_time_arrival for shipment in shipments]
    source_company = [shipment.source_company for shipment in shipments]
    source_address = [shipment.source_address for shipment in shipments]
    destination_company = [shipment.destination_company for shipment in shipments]
    destination_address = [shipment.destination_address for shipment in shipments]
    confirmation = [shipment.confirmation for shipment in shipments]
    totals = [PurchaseOrder.query.filter_by(po_id=s.po_id).first().total for s in shipments]
    report_total = sum(totals)

    vehicles = [Vehicle.query.filter_by(vehicle_id=s.vehicle_id).first() for s in shipments]
    vehicle_ds = [str(v.year) + " " + str(v.make) + " " + str(v.model) + " VIN#:" + str(v.vin) for v in vehicles]
    ### add parts to report in string format --> "Brand Cost, Brand Cost"

    df = pd.DataFrame({"Depart Date": depart_time, "Arrival Times": est_time_arrival,
                       "Source Company": source_company, "Source Address": source_address,
                       "Destination Company": destination_company,
                       "Destination Address": destination_address, "Confirmation": confirmation, "Total": totals,
                       "Total Cost Incoming Shipments": report_total})
    path = os.path.join(app.config['TEMPFILE_DIR'], filename)
    df.to_csv(path, encoding='utf-8')

    return send_from_directory(directory=app.config['TEMPFILE_DIR'], filename=filename)


@app.route('/outgoingreport', methods=['GET', 'POST'])
@login_required([0, 1])
def outgoingreport():
    """Page/Modal for outgoing report.

    Returns:
        rendered template: code for modal
    """
    shipments = Shipment.query.filter_by(shipment_type=True).all()
    return render_template('outgoingreport.html', shipments=shipments, user=current_user)


@app.route('/generategoingreport', methods=['GET'])
@login_required([0, 1])
def generateoutgoingreport():
    """Page/Modal for generating outgoing report.

    Returns:
        send_from_directory(): a directory on the local machine to store the report
    """
    filename = "outgoing_ship_report.csv"

    shipments = Shipment.query.filter_by(shipment_type=True).all()

    arrival_status = [shipment.arrival_status for shipment in shipments]
    payment_status = [shipment.payment_status for shipment in shipments]
    depart_time = [shipment.depart_time for shipment in shipments]
    est_time_arrival = [shipment.est_time_arrival for shipment in shipments]
    source_company = [shipment.source_company for shipment in shipments]
    source_address = [shipment.source_address for shipment in shipments]
    destination_company = [shipment.destination_company for shipment in shipments]
    destination_address = [shipment.destination_address for shipment in shipments]
    confirmation = [shipment.confirmation for shipment in shipments]
    totals = [Manifest.query.filter_by(manifest_id=s.manifest_id).first().total for s in shipments]
    report_total = sum(totals)

    vehicles = [Vehicle.query.filter_by(vehicle_id=s.vehicle_id).first() for s in shipments]
    vehicle_ds = [str(v.year) + " " + str(v.make) + " " + str(v.model) + " VIN#:" + str(v.vin) for v in vehicles]
    ### add parts to report in string format --> "Brand Cost, Brand Cost"

    df = pd.DataFrame({"Depart Date": depart_time, "Arrival Times": est_time_arrival,
                       "Source Company": source_company, "Source Address": source_address,
                       "Destination Company": destination_company,
                       "Destination Address": destination_address, "Confirmation": confirmation, "Total": totals,
                       "Total Cost Outgoing Shipments": report_total})
    path = os.path.join(app.config['TEMPFILE_DIR'], filename)
    df.to_csv(path)

    return send_from_directory(directory=app.config['TEMPFILE_DIR'], filename=filename)

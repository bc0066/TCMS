from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login


class Personnel(UserMixin, db.Model):
    """
        The Personnel object contains personnel properties.
        This class is used to initialize the database with personnel info.

        Attributes: 
            employee_id: integer value that uniquely identifies them
            first_name: String value of the personnel's first name
            middle_i: String value of the personnel's middle initial
            last_name: String value of the personnel's last name
            address: String value of the personnel's address
            phone: integer value of the personnel's phone number
            rate: Float value for the Salary of the personnel
            start_time: DateTime value of when the personnel joined the company
            end_time: DateTime value of when the personnel left the company (If applicable)
            position: String value of the Position that the personnel held at the company
            category: String value of the category the personnel belongs to
            password: String value of the password for the personnel
            drivers: database relationship 
    """
    __tablename__ = 'personnel'
    employee_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    middle_i = db.Column(db.String)
    last_name = db.Column(db.String)
    address = db.Column(db.String)
    phone = db.Column(db.String)
    rate = db.Column(db.Float)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    position = db.Column(db.String)
    category = db.Column(db.Integer)
    password = db.Column(db.String)

    drivers = db.relationship('Driver', backref='personnel')

    @property
    def password_plain(self):
        raise AttributeError('password_plain is not a readable attribute')

    @password_plain.setter
    def password_plain(self, password_plain):
        """ Take a password and generate a hash
        Args:      
            password_plain (str): plaintext of the password.
        """
        self.password = generate_password_hash(password_plain)

    def verify_password(self, password_plain):
        """Check the hash of the passed in password and compare it to the users password hash.

        Args:
        
            password_plain (str): plaintext of the password.
        
        Returns:
            return if the values of the personnel password and password_plain are equal
        """
        return check_password_hash(self.password, password_plain)

    def __repr__(self):
        return '<Personnel %r %r %r>' % (self.employee_id, self.last_name, self.category_text)

    def get_id(self):
        """Get the ID of the personnel.
        
        Returns:
            employee id
        """
        return self.employee_id

    def as_dict(self):
        """Get the ID of the personnel.
        
        Returns:
            employee id
        """
        return {self.padded_id: self.fullname}

    @property
    def fullname(self):
        """Get the fullname of the personnel.
        
        Returns:
            fullname of personnel: str(first, middle, last)
        """
        return '%s %s %s' % (self.first_name, self.middle_i, self.last_name)

    @property
    def account_active(self):
        """check to see if the personnel account is still active. 
        
        Returns:
            bool
        """
        if self.end_time is not None:
            return False
        return True

    @property
    def is_active(self):
        """check to see if the personnel account is still active. 
        
        Returns:
            bool
        """
        if self.end_time is not None:
            return False
        return True

    @property
    def padded_id(self):
        """format the personnel ID. 
        
        Returns:
            formatted employee_id(int)
        """
        return '{:06d}'.format(self.employee_id)

    @property
    def category_text(self):
        category = {
            0: 'Back Office',
            1: 'Shipping Manager',
            2: 'Maintenance',
            3: 'Driver'
        }
        return category.get(self.category)


vehicle_parts = db.Table('vehicle_parts',
                         db.Column('vehicle_id', db.Integer, db.ForeignKey('vehicles.vehicle_id'), primary_key=True),
                         db.Column('part_id', db.Integer, db.ForeignKey('parts.part_id'), primary_key=True)
                         )


class Vehicle(db.Model):
    """
        The Vehicle object contains vehicle properties
        Attributes:
            vehicle_id: Integer value that uniquely identifies a vehicle
            make: String value for the make of the vehicle
            model: String value for the model of the vehicle
            year: String value of the year the vehicle was made
            vehicle_type: String value for what type of vehicle it is
            active: Boolean value to represent if the vehicle is active
            vin: String value of the vin number associated with the vehicle
    """
    __tablename__ = 'vehicles'
    vehicle_id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String)
    model = db.Column(db.String)
    year = db.Column(db.String)
    vehicle_type = db.Column(db.String)
    active = db.Column(db.Boolean)
    vin = db.Column(db.String)

    @property
    def padded_id(self):
        """format the vehicle ID. 
        
        Returns:
            formatted vehicle_id(int)
        """
        return '{:06d}'.format(self.vehicle_id)

    @property
    def vehicle_info(self):
        """  
        Returns:
            Vehicle information
        """
        return '%s:%s %s (%s)' % (self.vehicle_type, self.make, self.model, self.year)

    drivers = db.relationship('Driver', backref='vehicles')
    maintenance = db.relationship('Maintenance', backref='vehicles')
    shipments = db.relationship('Shipment', backref='vehicles')

    vehicle_parts = db.relationship('Part', secondary=vehicle_parts, lazy='subquery',
                                    backref=db.backref('vehicles', lazy=True))


class Driver(db.Model):
    """
        The Driver object contains driver properties

        Attributes:
            driver_id: Integer value that uniquely identifies the driver
            employee_id: Integer value that correlates to a personnel
            vehicle: Integer value that uniquely identifies the vehicle that
            the driver will drive
    """
    __tablename__ = 'drivers'
    driver_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('personnel.employee_id'))
    vehicle = db.Column(db.Integer, db.ForeignKey('vehicles.vehicle_id'))


class Part(db.Model):
    """
        The Part object contains part properties

        Attributes:
            part_id: Integer value that uniquely identifies the part
            brand: String value that states the brand of the part
            description: String value with a description of the part
            inventory: Integer value with the quantity of the part
            cost: Float value of the cost of the part
            source: String value that states where the part came from
            special: Boolean value stating if the part is special
            special_order: Boolean value that states if the part had to 
            be special ordered
    """
    __tablename__ = 'parts'
    part_id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String)
    description = db.Column(db.String)
    inventory = db.Column(db.Integer)
    cost = db.Column(db.Float)
    source = db.String(db.String)
    special = db.String(db.Boolean)
    special_order = db.Column(db.Boolean)

    @property
    def padded_id(self):
        """format the part ID. 
        
        Returns:
            formatted part_id(int)
        """
        return '{:06d}'.format(self.part_id)


maintenance_parts = db.Table('maintenance_parts',
                             db.Column('maintenance_id', db.Integer, db.ForeignKey('maintenance.maintenance_id'),
                                       primary_key=True),
                             db.Column('part_id', db.Integer, db.ForeignKey('parts.part_id'), primary_key=True)
                             )


class Maintenance(db.Model):
    """
        The Maintenance object contains maintenance properties
        Attributes:
            maintenance_id: Integer value that uniquely identifies the maintenance record
            maintenance_type: String value stating the type of maintenance 
            description: String value stating a description of the maintenance
            date_time: DateTime value of when the maintenance was done
            vehicle_id: Integer value of the vehicle having maintenance done to it
    """
    __tablename__ = 'maintenance'
    maintenance_id = db.Column(db.Integer, primary_key=True)
    maintenance_type = db.Column(db.String)
    description = db.Column(db.String)
    date_time = db.Column(db.DateTime)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.vehicle_id'))

    maintenance_parts = db.relationship('Part', secondary=maintenance_parts, lazy='subquery',
                                        backref=db.backref('maintenance', lazy=True))

    def total(self):
        part_costs = [Part.query.filter_by(part_id=mp.part_id).first().cost for mp in self.maintenance_parts]
        return sum(part_costs)

    @property
    def padded_vehicle_id(self):
        return '{:06d}'.format(self.vehicle_id)


manifest_items = db.Table('manifest_items',
                          db.Column('manifest_id', db.Integer, db.ForeignKey('manifests.manifest_id'),
                                    primary_key=True),
                          db.Column('item_id', db.Integer, db.ForeignKey('items.item_id'), primary_key=True)
                          )

po_items = db.Table('po_items',
                    db.Column('po_id', db.Integer, db.ForeignKey('purchaseorders.po_id'),
                              primary_key=True),
                    db.Column('item_id', db.Integer, db.ForeignKey('items.item_id'), primary_key=True)
                    )


class Manifest(db.Model):
    """
        The Manifest object contains manifest properties
        Attributes:
            manifest_id: Integer value to uniquely identify a manifest
            shipping_handling: Float value of the shipping and handling that
            will be applied to a manifest
            total: Float value of the subtotal + shipping and handling
    """
    __tablename__ = 'manifests'
    manifest_id = db.Column(db.Integer, primary_key=True)
    shipping_handling = db.Column(db.Float)
    total = db.Column(db.Float)

    @property
    def subtotal(self):
        """ Calculate the sub total for the item 
        
        Returns:
            subtotal (float)
        """
        subtotal = 0
        for item in self.items:
            subtotal += item.total_cost
        return subtotal

    @property
    def total(self):
        """ Calculate the actual total of the item. This is done by add shipping and 
            handling to the subtotal. If there is no shipping and handling just return subtotal. 
        
        Returns:
            subtotal
            subtotal + shipping_handling
        """
        if self.shipping_handling:
            return self.subtotal + self.shipping_handling
        return self.subtotal

    # purchaseorders = db.relationship('PurchaseOrder', backref='manifests')
    shipments = db.relationship('Shipment', backref='manifests')
    items = db.relationship('Item', secondary=manifest_items, lazy='subquery',
                            backref=db.backref('manifests', lazy=True))


class Item(db.Model):
    """
        The Item object contains item properties
        Attributes:
            item_id: Integer value that uniquely identifies the item
            brand: String of the brand of the item
            description: String of a description of the item
            cost: Float value of the cost of the item
            number: Integer value of the quantity of items
            status: Integer value of the status of the item
    """
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String)
    description = db.Column(db.String)
    cost = db.Column(db.Float)
    number = db.Column(db.Integer)
    status = db.Column(db.Integer)

    @property
    def total_cost(self):
        """ Calculate the total cost of the Item. This is done by taking the item cost and
            multiply by the quantity. 
        
        Returns:
            cost * number (float): this returns the cost of the item * the quantity ordered
        """
        if self.cost and self.number:
            return self.cost * float(self.number)
        else:
            return 0

    @property
    def status_text(self):
        """ Get the status of the item 
        
        Returns:
            status of the item
        """
        status = {
            0: 'Shipped',
            1: 'Back Ordered',
            2: 'Unavailable'
        }
        return status.get(self.status)

    def __repr__(self):
        return "<Item %r: %r %r>" % (self.item_id, self.brand, self.description)


class PurchaseOrder(db.Model):
    """
    The PurchaseOrder object contains purchase order properties
    Attributes:
        po_id: Integer value that uniquely identifies the purchase order
        status: Integer of the status of the purchase order
        shipping_handling: Float value of the shipping and handling that will be applied
        total: Float value of the total cost 
    """

    __tablename__ = 'purchaseorders'
    po_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer)  ##status coded by number
    shipping_handling = db.Column(db.Float)
    total = db.Column(db.Float)

    # manifest_id = db.Column(db.Integer, db.ForeignKey('manifests.manifest_id'))

    @property
    def subtotal(self):
        """ Calculate the subtotal of the item. 
        
        Returns:
            subtotal (float)
        """
        subtotal = 0
        for item in self.items:
            subtotal += item.total_cost
        return subtotal

    @property
    def total(self):
        """ Calculate the actual total of the item. This is done by add shipping and 
            handling to the subtotal. If there is no shipping and handling just return subtotal. 
        
        Returns:
            subtotal
            subtotal + shipping_handling
        """
        if self.shipping_handling:
            return self.subtotal + self.shipping_handling
        return self.subtotal

    shipments = db.relationship('Shipment', backref='purchaseorders')
    items = db.relationship('Item', secondary=po_items, lazy='subquery',
                            backref=db.backref('purchaseorders', lazy=True))


shipment_drivers = db.Table('shipment_drivers',
                            db.Column('ship_id', db.Integer, db.ForeignKey('shipments.ship_id'), primary_key=True),
                            db.Column('driver_id', db.Integer, db.ForeignKey('drivers.driver_id'), primary_key=True)
                            )

shipment_personnel = db.Table('shipment_personnel',
                              db.Column('ship_id', db.Integer, db.ForeignKey('shipments.ship_id'), primary_key=True),
                              db.Column('employee_id', db.Integer, db.ForeignKey('personnel.employee_id'),
                                        primary_key=True)
                              )


class Shipment(db.Model):
    """
    The Shipment object contains the properties of a Trucking 
    Company shipment.
    Attributes:
        ship_id: Integer value that uniquely identifies the shipment
        arrival_status: DateTime 
        payment_status: Boolean value that states whether the purchase order 
                        was paid for
        depart_time: DateTime value of when the shipment departed
        est_time_arrival: DateTime of the estimated day the shipment
                          will arrive
        shipment_type: Boolean value stating the type of shipment
        source_company: String value of the company that sent the shipment
        source_address: String value of the address of the source company
        destination_company: String value of the company that is receiving
                             the shipment
        destination_address: String value of the address of the destination
                             company
        confirmation: Boolean value stating that the shipment was confirmed
        
        vehicle_id: Integer value that uniquely identifies the vehicle to 
                    the shipment
        manifest_id: Integer value that uniquely identifies the manifest to
                     the shipment
        po_id: Integer value that uniquely identifies the purchase order
               to the shipment
    """
    __tablename__ = 'shipments'
    ship_id = db.Column(db.Integer, primary_key=True)
    arrival_status = db.Column(db.DateTime)
    payment_status = db.Column(db.Boolean)
    depart_time = db.Column(db.DateTime)
    est_time_arrival = db.Column(db.DateTime)
    shipment_type = db.Column(db.Boolean)
    source_company = db.Column(db.String)
    source_address = db.Column(db.String)
    destination_company = db.Column(db.String)
    destination_address = db.Column(db.String)
    confirmation = db.Column(db.Boolean)

    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.vehicle_id'))
    manifest_id = db.Column(db.Integer, db.ForeignKey('manifests.manifest_id'))
    po_id = db.Column(db.Integer, db.ForeignKey('purchaseorders.po_id'))

    shipment_drivers = db.relationship('Driver', secondary=shipment_drivers, lazy='subquery',
                                       backref=db.backref('shipments', lazy=True))
    shipment_personnel = db.relationship('Personnel', secondary=shipment_personnel, lazy='subquery',
                                         backref=db.backref('shipments', lazy=True))

    @property
    def padded_id(self):
        return '{:06d}'.format(self.ship_id)

    @property
    def source(self):
        return '%s\r\n%s' % (self.source_company, self.source_address)

    @property
    def destination(self):
        return '%s\r\n%s' % (self.destination_company, self.destination_address)

    @property
    def friendly_departure(self):
        return '%s' % (self.depart_time.strftime('%Y-%m-%d %H:%M'))

    @property
    def friendly_arrival(self):
        return '%s' % (self.est_time_arrival.strftime('%Y-%m-%d %H:%M'))

    @property
    def friendly_confirmation(self):
        return '%s' % (self.arrival_status.strftime('%Y-%m-%d %H:%M'))

    @property
    def friendly_shipment_type(self):
        if self.shipment_type:
            return "Outgoing ↗"
        return "Incoming ↙"

    @property
    def confirmed(self):
        if self.arrival_status:
            return True
        return False

    def __repr__(self):
        if self.shipment_type:
            return "<Outgoing Shipment %r MANIFEST:%r %r to %r>" % (
                self.ship_id, self.manifest_id, self.source, self.destination)
        return "<Incoming Shipment %r PO:%r %r to %r>" % (self.ship_id, self.po_id, self.source, self.destination)


@login.user_loader
def load_user(employee_id):
    return Personnel.query.get(int(employee_id))

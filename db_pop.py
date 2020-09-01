import os
from pprint import pprint as pp
from random import randint, sample, choice
import string
from app.models import *
from faker import Faker
from datetime import timedelta
fake = Faker()

cur_dir = os.getcwd()


def generate_phones():
    """ Generate phone numbers

    Return:
        Outfile with a list of phone numbers
    """
    outfile = open(os.path.join(cur_dir, "app", "phones.txt"), 'w')
    for i in range(1, 3000):
        first = randint(100, 999)
        second = randint(100, 999)
        third = randint(1000, 9999)
        phone = str(first) + "-" + str(second) + "-" + str(third) + '\n'
        outfile.write(phone)
    return True


def readNumberFile(phoneInFile=os.path.join(cur_dir, "app", "phones.txt")):
    """ Read the file containing numbers to store in a list

    Return:
        List of phone numbers
    """
    phones = open(phoneInFile, 'r')
    phoneList = []
    for phone in phones:
        phoneList.append(phone)
    return phoneList

def readCompanyFile(companyInFile=os.path.join(cur_dir, "app", "company.txt")):
    """ Read the file containing numbers to store in a list

        Return:
            List of company names
        """
    companies = open(companyInFile, 'r')
    companyList = []
    for company in companies:
        companyList.append(company)
    return companyList

def readNameFile(nameinFile=os.path.join(cur_dir, "app", "names.txt")):
    """Read the file containing names to store in a list

    Return:
        Outfile with a list of names
    """
    file1 = open(nameinFile, 'r')
    file2 = open("outfile.txt", 'w')
    names = file1.readlines()
    nameList = []
    for i in range(1, 100):
        firstLastList = []
        randFirstName = randint(1, 5000)
        firstLastList.append(names[randFirstName])
        randLastName = randint(1, 5000)
        firstLastList.append(names[randLastName])
        nameList.append(firstLastList)
        file2.write(str(firstLastList))
    pp(str(nameList))
    return nameList


def gen_Date_Time():
    """ Generate Date and Time
    
    Return:
        String with the month, day, and year
    """
    month = randint(1, 12)
    day = randint(1, 30)
    year = randint(2009, 2019)
    return (str(month) + '-' + str(day) + '-' + str(year))


def vin_generator(size=17, chars=string.ascii_uppercase + string.digits):
    """ Generate vin number
    Inputs: 
    Return:
        String of numbers(VIN)
    """
    return ''.join(choice(chars) for _ in range(size))


def gen_maintenance():
    """ A function that will randomly generate maintenance records in
        the database. In this case we wanted 500 maintenance records in
        our database. This value is can be changed to however many entries 
        in the database the user desires.
    
    Return:
        List of maintenance records that contain:
            - Maintenance ID
            - Maintenance Type
            - Description
            - Date/Time
            - Vehicle ID
    """
    vehIDList = list(range(Vehicle.query.all()[-1].vehicle_id))[1:]
    maint = []
    count = 0
    for i in range(0, 500):
        count += 1
        j = i
        if i >= 25:
            j = randint(0, 24)
        vehID = vehIDList[j]
        maintenance = []
        if i < 50:
            maintenance.append(randint(1, 1000))
            maintenance.append("Brakes")
            maintenance.append("Change Brakes")
            maintenance.append(gen_Date_Time())
            maintenance.append(vehID)
        elif i < 100:
            maintenance.append(randint(100, 10000))
            maintenance.append("Transmission Fluid")
            maintenance.append("Change the Transmission Fluid")
            maintenance.append(gen_Date_Time())
            maintenance.append(vehID)
        elif i < 150:
            maintenance.append(i + count)
            maintenance.append("Oil Change")
            maintenance.append("Change the oil on the truck")
            maintenance.append(gen_Date_Time())
            maintenance.append(vehID)
        elif i < 200:
            maintenance.append(i + count)
            maintenance.append("Tire Change and Rotation")
            maintenance.append("Change tires")
            maintenance.append(gen_Date_Time())
            maintenance.append(vehID)
        elif i < 250:
            maintenance.append(i + count)
            maintenance.append("Alignment")
            maintenance.append("Align tires")
            maintenance.append(gen_Date_Time())
            maintenance.append(vehID)
        elif i < 300:
            maintenance.append(i + count)
            maintenance.append("Brake pad replacement")
            maintenance.append("Replace Brake pads on truck")
            maintenance.append(gen_Date_Time())
            maintenance.append(vehID)
        elif i < 350:
            maintenance.append(i + count)
            maintenance.append("Replace fan belt")
            maintenance.append("Replace fan belt")
            maintenance.append(gen_Date_Time())
            maintenance.append(vehID)
        elif i < 400:
            maintenance.append(i + count)
            maintenance.append("Windshield wiper replacement")
            maintenance.append("Windshield wiper replacement")
            maintenance.append(gen_Date_Time())
            maintenance.append(vehID)
        elif i < 450:
            maintenance.append(i + count)
            maintenance.append("Tire Change")
            maintenance.append("Change tires")
            maintenance.append(gen_Date_Time())
            maintenance.append(vehID)
        else:
            maintenance.append(i + count)
            maintenance.append("Tire rotation")
            maintenance.append("Tire rotation")
            maintenance.append(gen_Date_Time())
            maintenance.append(vehID)
        maint.append(maintenance)
    return maint


def gen_vehicles():
    """ Generate vehicle records
    
    Return:
        List of vehicle records that contain:
            - Vehicle ID
            - Make
            - Model
            - Year
            - Vehicle Type
            - VIN
    """
    make_model = []
    for i in range(0, 25):
        makeModel = []
        if i < 7:
            makeModel.append(i + 1)
            makeModel.append("Kenworth")
            makeModel.append("W900")
            makeModel.append("2014")
            makeModel.append("Semi-Truck")
            makeModel.append(vin_generator())

        elif i < 14:
            makeModel.append(i + 1)
            makeModel.append("Freightliner")
            makeModel.append("Cabover")
            makeModel.append("2015")
            makeModel.append("Semi-Truck")
            makeModel.append(vin_generator())

        elif i < 21:
            makeModel.append(i + 1)
            makeModel.append("Peterbilt")
            makeModel.append("379")
            makeModel.append("2018")
            makeModel.append("Semi-Truck")
            makeModel.append(vin_generator())

        elif i < 22:
            makeModel.append(i + 1)
            makeModel.append("GMC")
            makeModel.append("Savana")
            makeModel.append("2018")
            makeModel.append("Box Truck")
            makeModel.append(vin_generator())

        else:
            makeModel.append(i + 1)
            makeModel.append("Ford")
            makeModel.append("F250")
            makeModel.append("2018")
            makeModel.append("Pickup Truck")
            makeModel.append(vin_generator())

        make_model.append(makeModel)
    return make_model


def gen_parts():
    """ Generate part records
    
    Return:
        List of part records that contain:
            - Part ID
            - Brand
            - Description
            - Inventory
            - Cost
            - Source
    """
    partList = []
    for i in range(0, 25):
        part = []
        if i == 0:
            part.append(randint(100, 10000))
            part.append("STP")
            part.append("Extended Oil Life Filter")
            part.append("10")
            part.append("12.99")
            part.append("AutoZone")
        elif i == 1:
            part.append(randint(100, 10000))
            part.append("Mobil")
            part.append("5W40 synthetic diesel oil.")
            part.append("10")
            part.append("25.47")
            part.append("AutoZone")
        elif i == 2:
            part.append(randint(100, 10000))
            part.append("Bridgestone")
            part.append("M835A Ecopia Tire")
            part.append("50")
            part.append("512.00")
            part.append("Bridgestone")
        elif i == 3:
            part.append(randint(100, 10000))
            part.append("X2 Power")
            part.append("Battery")
            part.append("5")
            part.append("416.99")
            part.append("Batteries Plus")
        elif i == 4:
            part.append(randint(100, 10000))
            part.append("Cummins")
            part.append("Air Compressor")
            part.append("5")
            part.append("632.00")
            part.append("BigMachineParts")
        elif i == 5:
            part.append(randint(100, 10000))
            part.append("Goodyear")
            part.append("Fan Belt")
            part.append("10")
            part.append("12.50")
            part.append("Advanced Auto Parts")
        elif i == 6:
            part.append(randint(100, 10000))
            part.append("Castrol")
            part.append("10 Gal Transmission Fluid")
            part.append("8")
            part.append("190.00")
            part.append("AutoZone")
        elif i == 7:
            part.append(randint(100, 10000))
            part.append("Rain-X")
            part.append("Windshield Wiper Blades")
            part.append("10")
            part.append("23.99")
            part.append("AutoZone")
        elif i == 8:
            part.append(randint(100, 10000))
            part.append("Meritor")
            part.append("Brake Pads")
            part.append("5")
            part.append("70.67")
            part.append("Nick's Truck Parts")
        elif i == 9:
            part.append(randint(100, 10000))
            part.append("Castrol")
            part.append("10W30 Synthetic motor oil.")
            part.append("5")
            part.append("22.67")
            part.append("AutoZone")
        elif i == 10:
            part.append(randint(100, 10000))
            part.append("Moog")
            part.append("Tie Rod")
            part.append("5")
            part.append("170.67")
            part.append("Nick's Truck Parts")
        elif i == 11:
            part.append(randint(100, 10000))
            part.append("SPPC")
            part.append("Brake Lights")
            part.append("5")
            part.append("93.67")
            part.append("AutoZone")
        elif i == 12:
            part.append(randint(100, 10000))
            part.append("SPPC")
            part.append("Headlights")
            part.append("5")
            part.append("120.97")
            part.append("AutoZone")
        elif i == 13:
            part.append(randint(100, 10000))
            part.append("Denso")
            part.append("Spark Plugs")
            part.append("5")
            part.append("14.67")
            part.append("AutoZone")
        elif i == 14:
            part.append(randint(100, 10000))
            part.append("Bussman")
            part.append("Fuses")
            part.append("10")
            part.append("3.97")
            part.append("AutoZone")
        elif i == 15:
            part.append(randint(100, 10000))
            part.append("Omega")
            part.append("AC Kit")
            part.append("5")
            part.append("670.67")
            part.append("Raneys Truck Parts")
        elif i == 16:
            part.append(randint(100, 10000))
            part.append("Freightliner")
            part.append("Compact Auxilary Heater 7500")
            part.append("5")
            part.append("499.97")
            part.append("Nick's Truck Parts")
        elif i == 17:
            part.append(randint(100, 10000))
            part.append("Platinum")
            part.append("Radiator")
            part.append("5")
            part.append("995.75")
            part.append("Nick's Truck Parts")
        elif i == 18:
            part.append(randint(100, 10000))
            part.append("Omega")
            part.append("Power Steering pump")
            part.append("5")
            part.append("264.95")
            part.append("Nick's Truck Parts")
        elif i == 19:
            part.append(randint(100, 10000))
            part.append("Goodyear")
            part.append("Suspension Air Spring")
            part.append("5")
            part.append("228.00")
            part.append("Nick's Truck Parts")
        elif i == 20:
            part.append(randint(100, 10000))
            part.append("Castrol")
            part.append("Fully Synthetic 0W30 Motor Oil.")
            part.append("5")
            part.append("20.67")
            part.append("Nick's Truck Parts")
        elif i == 21:
            part.append(randint(100, 10000))
            part.append("Cascadia")
            part.append("Window Regulator")
            part.append("5")
            part.append("59.95")
            part.append("Nick's Truck Parts")
        elif i == 22:
            part.append(randint(100, 10000))
            part.append("Meritor")
            part.append("Wind shield wiper fluid")
            part.append("5")
            part.append("70.67")
            part.append("Nick's Truck Parts")
        elif i == 23:
            part.append(randint(100, 10000))
            part.append("Caterpillar")
            part.append("Transmission Speed Sensor")
            part.append("5")
            part.append("70.67")
            part.append("Nick's Truck Parts")
        else:
            part.append(randint(100, 10000))
            part.append("Duralast")
            part.append("Brake Rotor")
            part.append("10")
            part.append("51.99")
            part.append("AutoZone")
        partList.append(part)
    return partList

def db_pop_shipments(db):
    """ Populate database with shipments
        inputs:
            db - instance of FlaskSQLAlchemy to do db operations
    """

    vehicle_ids = [v.vehicle_id for v in Vehicle.query.all()]
    drivers = [p for p in Personnel.query.all() if p.category == 3]
    companies = readCompanyFile()
    n = 20
    for n in range(n):
        shipment = Shipment()
        shipment.destination_company = sample(companies, 1)[0]
        shipment.destination_address = fake.address()
        shipment.source_address = fake.address()
        shipment.source_company = sample(companies, 1)[0]
        shipment.shipment_type = randint(0, 1)
        shipment.confirmation = randint(0, 1)
        shipment.payment_status = randint(0, 1)
        shipment.vehicle_id = sample(vehicle_ids, 1)[0]
        shipment.shipment_personnel = sample(drivers, 3)
        shipment.depart_time = fake.date_time_between(start_date='-5y', end_date='-1d', tzinfo=None)
        shipment.est_time_arrival = shipment.depart_time + timedelta(days=7)
        shipment.arrival_status = shipment.est_time_arrival
        if shipment.shipment_type == '1':
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
        db.session.add(shipment)
        db.session.commit()

    return True

def db_pop_personnel(db):
    """ Populate database with personnel
    inputs:
        db - instance of FlaskSQLAlchemy to do db operations
    """

    # get data
    phones = readNumberFile()
    names = readNameFile()
    middle_is = string.ascii_uppercase  # string
    street_names = ['Main Street', 'Dublin Avenue', 'First Street', 'Fourteenth Avenue',
                    'Washington Circle', 'Jefferson Way', 'Johnson Boulevard', 'Adams Trail']
    zip_codes = ['23421', '23456', '23590', '23481', '23406']
    cities = ['Huntsville', 'Madison', 'Athens', 'Hampton Cove', 'Owens Cross Roads']
    positions = ['Driver', 'Office Worker', 'Shipment Manager', 'Maintenance Worker']
    categories = [0, 1, 2, 3]

    # get n entries (n<100)
    n = 20
    phones = phones[:n]
    names = names[:n]

    for name, phone in zip(names, phones):
        # get data for personnel
        first_name = name[0].rstrip('\n')
        last_name = name[1].rstrip('\n')
        middle_i = middle_is[randint(0, 25)]
        ph = phone.rstrip('\n')
        address = str(randint(10, 5000)) + ' ' + sample(street_names, 1)[0] + \
                  ' ' + sample(cities, 1)[0] + ', AL ' + sample(street_names, 1)[0]
        start_date = fake.date_between(start_date='-30y', end_date='today')
        rate = float(randint(15000, 150000))
        category = categories[randint(0, 3)]

        if category == 0:
            position = "Office Worker"
        elif category == 1:
            position = "Shipment Manager"
        elif category == 2:
            position = "Maintenance"
        else:
            position = "Driver"
            # populate Personnel
        p = Personnel()
        p.first_name = first_name
        p.last_name = last_name
        p.middle_i = middle_i
        p.address = address
        p.phone = ph
        p.rate = rate
        p.start_time = start_date
        p.position = position
        p.password_plain = 'password'
        p.category = category

        db.session.add(p)
        db.session.commit()


    return True


def vehicle_db_pop(db):
    """ Populate the database with vehicles
    inputs:
        db - instance of FlaskSQLAlchemy to do db operations
    """
    vehicle = gen_vehicles()

    for veh in vehicle:
        # vehicle_id = veh[0]
        make = veh[1]
        model = veh[2]
        year = veh[3]
        vehicle_type = veh[4]
        active = True
        vin = veh[5]

        v = Vehicle()
        # v.vehicle_id = vehicle_id
        v.make = make
        v.model = model
        v.year = year
        v.vehicle_type = vehicle_type
        v.active = active
        v.vin = vin

        db.session.add(v)
        db.session.commit()
    return True


def db_pop_parts(db):
    """ Populate database with parts
    inputs:
        db - instance of FlaskSQLAlchemy to do db operations
    """
    parts = gen_parts()

    for part in parts:
        # part_id = part[0]
        brand = part[1]
        description = part[2]
        inventory = part[3]
        cost = part[4]
        source = part[5]
        special_order = False

        p = Part()
        # p.part_id = part_id
        p.brand = brand
        p.description = description
        p.inventory = inventory
        p.cost = cost
        p.source = source
        p.special_order = special_order

        db.session.add(p)
        db.session.commit()
    return True


def db_pop_maintenance(db):
    """ Populate database with maintenance records
    inputs:
        db - instance of FlaskSQLAlchemy to do db operations
    """
    maintenance = gen_maintenance()

    for maint in maintenance:
        # maintenance_id = maint[0]
        maintenance_type = maint[1]
        description = maint[2]
        date_time = maint[3]
        vehicle_id = maint[4]

        m = Maintenance()
        # m.maintenance_id = maintenance_id
        m.maintenance_type = maintenance_type
        m.description = description
        m.date_time = fake.date_between(start_date='-10y', end_date='today')
        m.vehicle_id = vehicle_id

        db.session.add(m)
        db.session.commit()
    return True

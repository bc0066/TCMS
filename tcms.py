from app import app, db
from app.models import Personnel, Vehicle, Driver, Part, Maintenance, Manifest, Item, PurchaseOrder, Shipment

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Personnel=Personnel,
                Vehicle=Vehicle, Driver=Driver, Part=Part,
                Maintenance=Maintenance, Manifest=Manifest,
                Item=Item, PurchaseOrder=PurchaseOrder,
                Shipment=Shipment)


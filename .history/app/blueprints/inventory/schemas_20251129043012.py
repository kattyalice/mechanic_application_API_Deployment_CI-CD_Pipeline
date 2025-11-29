from app.extensions import ma
from app.models import Inventory
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        include_fk = True
        load_instance = False
        dump_only = ("tickets",)
        unknown = "exclude"

    tickets = fields.List(fields.Nested("ServiceTicketSchema", exclude=("parts",)), dump_only=True)


inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)

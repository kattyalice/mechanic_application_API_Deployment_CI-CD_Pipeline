from application.extensions import ma
from application.models import ServiceTicket
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        include_fk = True
        load_instance = False
        dump_only = ("customer", "mechanics", "parts")
        unknown = "exclude"

    customer = fields.Nested("CustomerSchema", exclude=("service_tickets",), dump_only=True)

    mechanics = fields.List(fields.Nested("MechanicSchema", exclude=("tickets",)), dump_only=True)

    parts = fields.List(fields.Nested("InventorySchema", exclude=("tickets",)), dump_only=True)

    VIN = fields.String(required=True)


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)

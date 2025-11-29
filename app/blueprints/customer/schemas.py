from app.extensions import ma
from app.models import Customer
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_fk = True
        load_instance = False
        dump_only = ("service_tickets",)
        unknown = "exclude"
        
    email = fields.Email(required=False)

    service_tickets = fields.List(
        fields.Nested("ServiceTicketSchema", exclude=("customer",)),
        dump_only=True
    )

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


class LoginSchema(ma.Schema):
    email = ma.Email(required=True)
    password = ma.String(required=True, load_only=True)

login_schema = LoginSchema()
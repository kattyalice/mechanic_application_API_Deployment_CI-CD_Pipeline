from app.extensions import ma
from app.models import Mechanic
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        include_fk = True
        load_instance = False
        dump_only = ("tickets",)
        unknown = "exclude"
        
    email = ma.Email(required=False)

    tickets = fields.List(
        fields.Nested("ServiceTicketSchema", exclude=("mechanics",)),
        dump_only=True
    )

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

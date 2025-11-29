from app import create_app
from app.models import db
from config import ProdcutionConfig

app = create_app('ProductionConfig')

with app.app_context():
    db.create_all()
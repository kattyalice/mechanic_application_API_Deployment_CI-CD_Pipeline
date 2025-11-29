from app import create_app
from app.models import db
from config import ProductionConfig
from flask import redirect

app = create_app("ProductionConfig")

@app.route("/", methods=['GET'])
def index():
    return redirect('/api/docs')

with app.app_context():
    db.create_all()
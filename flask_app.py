from app import create_app
from config import ProductionConfig
from flask import redirect

app = create_app("ProductionConfig")

@app.route("/", methods=["GET"])
def index():
    return redirect("/api/docs")

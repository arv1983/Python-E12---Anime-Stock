from flask import Flask
from .views.blueprint import bp

app = Flask(__name__)
app.register_blueprint(bp)
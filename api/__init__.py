from flask import Flask
from flask_cors import CORS
from api.endpoints import pelayanan_bp


api = Flask(__name__)
CORS(api)

api.register_blueprint(pelayanan_bp)
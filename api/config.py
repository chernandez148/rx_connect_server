#server/api/config.py

import os

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy import MetaData

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure Stripe API key and other environment variables
app.config['DOMAIN_URL'] = os.environ.get('DOMAIN_URL')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)
migrate = Migrate(app, db)
db.init_app(app)

# Instantiate CORS
CORS(app, resources={r"/*": {"origins": os.environ.get('DOMAIN_URL')}})

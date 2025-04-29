#server/api/config.py

import os
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy import MetaData
from flask_jwt_extended import JWTManager
from api.utils.blacklist import is_token_revoked
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.instance_path = None  # Critical for Vercel serverless

# Configure Stripe API key and other environment variables
app.config['DOMAIN_URL'] = os.environ.get('DOMAIN_URL')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Handle Neon PostgreSQL connection
database_url = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

# Connection pool settings for serverless
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 5,
    'max_overflow': 2
}

# SQLAlchemy metadata configuration
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize extensions
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)
jwt = JWTManager(app)
jwt.token_in_blocklist_loader(is_token_revoked)

# CORS configuration
CORS(app, resources={r"/*": {"origins": os.environ.get('DOMAIN_URL')}})

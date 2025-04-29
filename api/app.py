from config import app
from routes.index_routes import index_bp
from routes.pharmacy_routes import pharmacy_bp
from routes.user_routes import user_bp
from routes.patient_routes import patient_bp
from routes.prescription_routes import prescription_bp
from routes.transfer_routes import transfer_bp
from routes.auth_routes import auth_bp

from models.pharmacies import Pharmacy
from models.users import User
from models.patients import Patient
from models.prescriptions import Prescription
from models.transfers import Transfer

def create_app():
    app.register_blueprint(index_bp)
    app.register_blueprint(pharmacy_bp) 
    app.register_blueprint(user_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(prescription_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(auth_bp) 
    return app

app = create_app()

if __name__ == '__main__':
    app.run()
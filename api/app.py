from api.config import app
from api.routes.index_routes import index_bp
from api.routes.pharmacy_routes import pharmacy_bp
from api.routes.user_routes import user_bp
from api.routes.patient_routes import patient_bp
from api.routes.prescription_routes import prescription_bp
from api.routes.transfer_routes import transfer_bp
from api.routes.auth_routes import auth_bp

from api.models.pharmacies import Pharmacy
from api.models.users import User
from api.models.patients import Patient
from api.models.prescriptions import Prescription
from api.models.transfers import Transfer

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
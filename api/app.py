from config import app
from routes.index_routes import index_bp
from routes.pharmacy_routes import pharmacy_bp
from routes.user_routes import user_bp
from routes.patient_routes import patient_bp

from models.pharmacies import Pharmacy
from models.users import User
from models.patients import Patient

def create_app():
    app.register_blueprint(index_bp)
    app.register_blueprint(pharmacy_bp) 
    app.register_blueprint(user_bp)
    app.register_blueprint(patient_bp)
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
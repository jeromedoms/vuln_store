from flask import Flask
from config import Config
from models.database import init_db
from routes import register_blueprints
import os
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('user_actions.log'),
        logging.StreamHandler()
    ]
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Create upload directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Initialize database
    init_db()
    
    # Register blueprints
    register_blueprints(app)
    
    # Create flags
    if not os.path.exists('flags'):
        os.makedirs('flags')
    
    with open('flags/user_flag.txt', 'w') as f:
        f.write('USER_FLAG{Th1s_1s_th3_u53r_fl4g}')
    
    with open('flags/root_flag.txt', 'w') as f:
        f.write('ROOT_FLAG{Th1s_1s_th3_r00t_fl4g}')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
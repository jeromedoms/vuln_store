from .auth import auth_bp
from .products import products_bp
from .cart import cart_bp
from .seller import seller_bp
from .admin import admin_bp
from .files import files_bp
from .tools import tools_bp
from flask import render_template

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(tools_bp)
    
    # Home page
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('notFound.html')
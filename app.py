from dotenv import load_dotenv          # <-- обязательно добавь
load_dotenv()                           # <-- обязательно добавь

from flask import Flask
from routes.main import main_bp
from routes.catalog import catalog_bp
from routes.orders import orders_bp
from routes.fence import fence_bp
from routes.snow_guard import snow_guard_bp

app = Flask(__name__)
app.secret_key = 'super-secret-key-change-before-deploy'

app.register_blueprint(main_bp)
app.register_blueprint(catalog_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(fence_bp)
app.register_blueprint(snow_guard_bp, url_prefix='/snow_guard')

if __name__ == '__main__':
    app.run(debug=True)
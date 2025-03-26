from flask import Flask
from app.config import configure_app
from app.routes import register_routes

app = Flask(__name__)

# Configure the application
configure_app(app)

# Register routes
register_routes(app)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
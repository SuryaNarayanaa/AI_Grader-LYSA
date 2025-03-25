from flask import Flask
from app.config import configure_app
import routes

# Create the Flask application
app = Flask(__name__)

# Configure the application
configure_app(app)

# Register routes
routes.register_routes(app)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
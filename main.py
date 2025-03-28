import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
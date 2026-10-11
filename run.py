import os
import sys

# Ensure current folder is first in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    print("\n========================================================")
    print("  AI-Powered Customer Feedback Analysis System")
    print("  Running locally on http://127.0.0.1:5000")
    print("========================================================\n")
    app.run(host='127.0.0.1', port=5000, debug=True)

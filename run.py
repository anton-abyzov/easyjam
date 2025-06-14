"""Run the EasyJam application"""

import sys
sys.path.append('.')

from easyjam.app import app

if __name__ == "__main__":
    print("Starting EasyJam Guitar Strumming Assistant...")
    print("Open http://localhost:5005 in your browser")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, port=5005)
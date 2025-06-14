"""Run the EasyJam application with 3D ALOHA simulation"""

import sys
sys.path.append('.')

from easyjam.app_3d import app

if __name__ == "__main__":
    print("Starting EasyJam 3D Guitar Strumming Assistant...")
    print("Checking for ALOHA environment...")
    
    try:
        import gym_aloha
        print("✅ ALOHA environment found! 3D simulation available.")
    except ImportError:
        print("⚠️  ALOHA not installed. Running in 2D mode.")
        print("   To enable 3D simulation, run: pip install gym-aloha")
    
    print("\nOpen http://localhost:5005 in your browser")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, port=5005)
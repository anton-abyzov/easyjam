"""Flask application with 3D ALOHA robot simulation"""

from flask import Flask, render_template, jsonify, request, Response
import json
import threading
import time
import numpy as np
from dataclasses import asdict
import cv2
import base64

from easyjam.simulation.aloha_guitar import AlohaGuitarEnv, ALOHA_AVAILABLE
from easyjam.music.chords import (
    ChordProgression, CHORD_LIBRARY, PATTERN_LIBRARY,
    get_chord_suggestions, get_pattern_suggestions
)

app = Flask(__name__)

# Global state
aloha_env = None
current_progression = None
is_playing = False
play_thread = None
latest_frame = None
frame_lock = threading.Lock()


def initialize_aloha():
    """Initialize ALOHA environment"""
    global aloha_env
    
    if ALOHA_AVAILABLE:
        print("Initializing ALOHA environment...")
        aloha_env = AlohaGuitarEnv(render_mode="rgb_array")
        aloha_env.reset()
        print("ALOHA environment ready!")
    else:
        print("ALOHA not available. Install with: pip install gym-aloha")
        aloha_env = None


def play_progression_3d():
    """Background thread for playing with ALOHA simulation"""
    global is_playing, current_progression, aloha_env, latest_frame
    
    if not aloha_env or not ALOHA_AVAILABLE:
        print("ALOHA environment not available")
        return
    
    pattern_phase = 0.0
    phase_speed = 0.05
    
    while is_playing and current_progression:
        # Get next strum
        strum = current_progression.get_next_strum()
        
        if strum in ['down', 'up']:
            # Generate strumming motion
            for phase in np.arange(0, 1, phase_speed):
                if not is_playing:
                    break
                
                action = aloha_env.generate_strum_action(strum, phase)
                obs, _, _, _, _ = aloha_env.step(action)
                
                # Capture frame for streaming
                frame = aloha_env.render()
                if frame is not None:
                    with frame_lock:
                        latest_frame = frame
                
                time.sleep(0.02)  # 50Hz update
        
        elif strum == 'rest':
            # Hold position
            beat_duration = current_progression.pattern.get_duration_per_beat()
            time.sleep(beat_duration)
        
        # Check if we need to advance chord
        if current_progression.current_pattern_index == 0:
            current_progression.advance_chord()


@app.route('/')
def index():
    """Main page"""
    return render_template('index_3d.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    def generate():
        global latest_frame
        
        while True:
            with frame_lock:
                if latest_frame is not None:
                    # Encode frame as JPEG
                    _, buffer = cv2.imencode('.jpg', latest_frame)
                    frame_bytes = buffer.tobytes()
                    
                    # Yield frame in multipart format
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.03)  # ~30 FPS
    
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/chords')
def get_chords():
    """Get available chords"""
    difficulty = request.args.get('difficulty', 3, type=int)
    suggestions = get_chord_suggestions(difficulty)
    
    chords = {}
    for name in suggestions:
        chord = CHORD_LIBRARY[name]
        chords[name] = {
            'name': chord.name,
            'frets': chord.frets,
            'difficulty': chord.difficulty
        }
    
    return jsonify(chords)


@app.route('/api/patterns')
def get_patterns():
    """Get available strumming patterns"""
    difficulty = request.args.get('difficulty', 3, type=int)
    suggestions = get_pattern_suggestions(difficulty)
    
    patterns = {}
    for name in suggestions:
        pattern = PATTERN_LIBRARY[name]
        patterns[name] = {
            'name': pattern.name,
            'pattern': pattern.pattern,
            'tempo': pattern.tempo,
            'difficulty': pattern.difficulty
        }
    
    return jsonify(patterns)


@app.route('/api/play', methods=['POST'])
def play():
    """Start playing a chord progression"""
    global current_progression, is_playing, play_thread
    
    data = request.json
    chords = data.get('chords', ['G', 'C', 'D', 'Em'])
    pattern = data.get('pattern', 'basic_alternating')
    
    # Stop current playback if any
    is_playing = False
    if play_thread and play_thread.is_alive():
        play_thread.join()
    
    # Create new progression
    current_progression = ChordProgression(chords, pattern)
    
    # Start playback thread
    is_playing = True
    play_thread = threading.Thread(target=play_progression_3d)
    play_thread.start()
    
    return jsonify({'status': 'playing'})


@app.route('/api/stop', methods=['POST'])
def stop():
    """Stop playing"""
    global is_playing
    
    is_playing = False
    
    return jsonify({'status': 'stopped'})


@app.route('/api/robot_state')
def get_robot_state():
    """Get current robot state"""
    state = {
        'current_chord': current_progression.get_current_chord().name if current_progression else None,
        'is_playing': is_playing,
        'aloha_available': ALOHA_AVAILABLE
    }
    
    return jsonify(state)


@app.route('/api/tempo', methods=['POST'])
def set_tempo():
    """Update tempo"""
    global current_progression
    
    data = request.json
    tempo = data.get('tempo', 120)
    
    if current_progression:
        current_progression.pattern.tempo = tempo
    
    return jsonify({'tempo': tempo})


@app.route('/api/simulation_type')
def get_simulation_type():
    """Check which simulation is available"""
    return jsonify({
        'type': '3d' if ALOHA_AVAILABLE else '2d',
        'aloha_available': ALOHA_AVAILABLE
    })


# Initialize ALOHA on startup
initialize_aloha()


if __name__ == '__main__':
    app.run(debug=True, port=5005)
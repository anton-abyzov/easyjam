"""Flask application for EasyJam guitar strumming assistant"""

from flask import Flask, render_template, jsonify, request
import json
import threading
import time
from dataclasses import asdict

from easyjam.simulation.robot_arm import RobotArmSimulator
from easyjam.music.chords import (
    ChordProgression, CHORD_LIBRARY, PATTERN_LIBRARY,
    get_chord_suggestions, get_pattern_suggestions
)


app = Flask(__name__)

# Global state
robot = RobotArmSimulator()
current_progression = None
is_playing = False
play_thread = None


def play_progression():
    """Background thread for playing the progression"""
    global is_playing, current_progression, robot
    
    while is_playing and current_progression:
        # Get next strum
        strum = current_progression.get_next_strum()
        
        if strum in ['down', 'up']:
            # Generate trajectory
            trajectory = robot.generate_strum_trajectory(strum, speed=2.0)
            
            # Execute trajectory
            for target_pos in trajectory:
                if not is_playing:
                    break
                    
                robot.target_angles = robot.inverse_kinematics_2d(target_pos)
                robot.update()
                time.sleep(0.02)  # 50Hz update rate
        
        elif strum == 'rest':
            # Wait for the beat duration
            beat_duration = current_progression.pattern.get_duration_per_beat()
            time.sleep(beat_duration)
        
        # Check if we need to advance chord (every 4 beats for 4/4 time)
        if current_progression.current_pattern_index == 0:
            current_progression.advance_chord()


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


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
    play_thread = threading.Thread(target=play_progression)
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
    positions = robot.forward_kinematics()
    
    state = {
        'joint_angles': robot.joint_angles.tolist(),
        'end_effector_pos': positions[-1].tolist() if len(positions) > 0 else [0, 0],
        'current_chord': current_progression.get_current_chord().name if current_progression else None,
        'is_playing': is_playing
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
# EasyJam - Guitar Strumming Assistant with 3D Robot Simulation

EasyJam is an accessibility-focused application that helps people with disabilities play guitar by automating the strumming motion while they focus on chord formation. Built for the LeRobot Hackathon, it now features **3D ALOHA robot simulation** for realistic visualization.

## 🎸 Quick Start

### Basic Installation (2D Mode)
```bash
conda create -n easyjam python=3.10
conda activate easyjam
pip install -r requirements.txt
python run.py
```

### Full Installation (3D ALOHA Mode) 🚀
```bash
conda create -n easyjam python=3.10
conda activate easyjam
pip install -r requirements.txt

# Install ALOHA simulation (optional but recommended)
pip install gym-aloha

# Run with 3D visualization
python run_3d.py
```

**Open Browser**: Navigate to `http://localhost:5005`

## 🎯 How to Use EasyJam

### Step 1: Build Your Chord Progression
- Click chord buttons to select (G, C, D, Em, Am, E, A, F, Bm)
- Selected chords appear highlighted
- Example progression: G → C → D → Em

### Step 2: Choose Strumming Pattern
- **Basic Down**: Simple downstrokes (beginners)
- **Basic Alternating**: Down-up pattern (most common)
- **Folk Pattern**: Classic acoustic style
- **Rock Pattern**: Energetic with syncopation
- **Reggae Pattern**: Off-beat emphasis
- **Flamenco Pattern**: Fast, complex rhythms

### Step 3: Set Your Tempo
- Adjust slider: 60-200 BPM
- Start slow (80 BPM) for learning
- Standard tempo: 120 BPM

### Step 4: Play!
- Click **▶️ Play** or press **Space bar**
- Watch the robot arm strum in real-time
- Stop anytime with **⏹️ Stop**

## 🤖 Robot Visualization Modes

### 3D ALOHA Simulation (Recommended)
When ALOHA is installed, you get:
- **Dual-arm robot**: Realistic ALOHA robot with two 7-DOF arms
- **Left arm**: Holds guitar neck and forms chords
- **Right arm**: Performs strumming motions
- **Multiple camera views**: High, low, and wrist cameras
- **Real-time rendering**: Smooth 3D visualization

### 2D Fallback Mode
Without ALOHA, the app shows:
- **Simple 2D view**: Guitar and robot arm representation
- **Blue Links**: Robot arm segments
- **Red Dots**: Joint positions
- **Green Dot**: End effector (pick)

The robot performs realistic strumming motions using inverse kinematics to generate smooth trajectories.

## ♿ Accessibility Features

- **Large Buttons**: Easy to click
- **High Contrast**: Clear visibility
- **Keyboard Navigation**: Full Tab support
- **Screen Reader**: ARIA labels throughout
- **Font Size Control**: A-, A, A+ buttons
- **Keyboard Shortcuts**: Space = Play/Stop
- **Responsive Design**: Works on mobile

## 🔧 API Endpoints

- `GET /` - Main interface
- `GET /api/chords?difficulty=3` - Get available chords
- `GET /api/patterns?difficulty=3` - Get strumming patterns
- `POST /api/play` - Start playing (body: `{chords: [], pattern: ""}`)
- `POST /api/stop` - Stop playing
- `GET /api/robot_state` - Get current robot position
- `POST /api/tempo` - Update tempo (body: `{tempo: 120}`)

## 🏗️ Architecture

### 1. Robot Simulation (`easyjam/simulation/robot_arm.py`)
- 6-DOF robot arm simulation
- Forward/inverse kinematics solver
- Smooth trajectory generation
- Real-time state updates

### 2. Music System (`easyjam/music/chords.py`)
- 12 chord definitions with fingering
- 6 strumming patterns
- Tempo-aware timing
- Chord progression management

### 3. Web Interface (`easyjam/app.py`)
- Flask REST API
- Real-time WebSocket-like updates
- Accessible HTML/CSS/JS
- Responsive design

## 🔌 Connecting to Real SO101 Robot (Future)

To use with actual hardware:

1. **Install LeRobot dependencies**:
```bash
pip install lerobot[feetech]
```

2. **Modify `app.py`** to import real robot:
```python
from lerobot.common.robots.so101_follower import SO101Follower

# Initialize hardware
robot = SO101Follower(port="/dev/tty.usbmodem...")
robot.connect()
```

3. **Update strumming logic** to send real commands:
```python
robot.send_action({
    "shoulder_pan.pos": angles[0],
    "shoulder_lift.pos": angles[1],
    "elbow_flex.pos": angles[2],
    "wrist_roll.pos": angles[3],
    "wrist_flex.pos": angles[4],
    "gripper.pos": angles[5]
})
```

## 🎵 Example Progressions

### Beginner
- **Two Chord**: G → D (Folk pattern, 100 BPM)
- **Classic**: C → G → Am → F (Basic alternating, 90 BPM)

### Intermediate  
- **Country**: G → Em → C → D (Folk pattern, 120 BPM)
- **Pop**: Am → F → C → G (Rock pattern, 130 BPM)

### Advanced
- **Barre Practice**: F → Bm → C → G (120 BPM)
- **Fast Strumming**: Any progression with Flamenco pattern at 140+ BPM

## 🧪 Testing

Run the robot simulation test:
```bash
python test_simulation.py
```

This displays an animated matplotlib window showing the robot performing strumming patterns.

## 🚀 Future Enhancements

- [ ] Real SO101 hardware integration
- [ ] MIDI input for chord selection
- [ ] Voice control ("Play G chord")
- [ ] Guitar tab import (.gp5, .txt)
- [ ] Recording and export features
- [ ] Metronome sync
- [ ] Multiple guitar types (acoustic, electric, bass)
- [ ] Fingerpicking patterns
- [ ] Chord recognition from audio

## 🤝 Contributing

We welcome contributions! Priority areas:
- Accessibility improvements
- New chord types (jazz, extended)
- Additional strumming patterns
- Hardware integration
- Mobile app development

## 📝 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- Built for LeRobot Hackathon 2024
- Inspired by the need for accessible music tools
- Thanks to the LeRobot team for the robotics framework
- Special thanks to musicians with disabilities who inspired this project

---

**Made with ❤️ for making music accessible to everyone**
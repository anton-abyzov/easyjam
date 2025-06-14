# EasyJam - Guitar Strumming Assistant with LeRobot

## Project Overview
EasyJam is an accessibility-focused application that helps people with disabilities play guitar by automating the strumming motion while they focus on chord formation. The app uses LeRobot's simulation environment to demonstrate robot-assisted guitar playing.

## Architecture Plan

### 1. Simulation Environment Setup
Since SO101 doesn't have a built-in simulation, we'll:
- Use `gym-xarm` simulation as a base (6-DOF arm similar to SO101)
- Adapt the xarm environment for guitar strumming motions
- Create custom task definitions for strumming patterns

### 2. Core Components

#### A. Guitar Strumming Simulation
- **Environment**: Modified gym-xarm environment
- **Task**: Strumming motion patterns (up/down strokes)
- **Guitar Model**: Simple rectangular target area representing strings
- **Success Metrics**: Timing accuracy, stroke consistency

#### B. Chord Detection System
- **Input Methods**:
  - Text-based chord input (e.g., "G", "C", "D", "Em")
  - MIDI keyboard input for chord selection
  - Voice commands for accessibility
- **Chord Library**: Common chord progressions and patterns

#### C. Strumming Pattern Engine
- **Pattern Types**:
  - Basic: Down-up patterns
  - Intermediate: Syncopated rhythms
  - Advanced: Fingerpicking simulations
- **Tempo Control**: 60-200 BPM adjustable
- **Dynamics**: Soft/Medium/Hard strumming intensity

#### D. User Interface
- **Accessibility Features**:
  - Large buttons with high contrast
  - Voice feedback
  - Keyboard shortcuts
  - Screen reader compatibility
- **Controls**:
  - Chord selector
  - Pattern selector
  - Tempo slider
  - Start/Stop/Pause buttons
  - Visual metronome

### 3. Implementation Steps

1. **Environment Setup**
   - Install LeRobot with xarm simulation
   - Create custom guitar strumming environment
   - Define reward functions for accurate strumming

2. **Strumming Motion Development**
   - Create trajectory generators for different patterns
   - Implement timing synchronization
   - Add motion smoothing for realistic strumming

3. **Training Policy**
   - Use behavior cloning or reinforcement learning
   - Train on various strumming patterns
   - Optimize for smooth, human-like motions

4. **User Interface Development**
   - Build Flask-based web interface
   - Implement real-time visualization
   - Add accessibility features

5. **Integration**
   - Connect UI to simulation
   - Implement real-time pattern execution
   - Add recording/playback features

### 4. Technical Stack
- **Backend**: Python, Flask
- **Simulation**: LeRobot (gym-xarm), PyBullet/MuJoCo
- **Frontend**: HTML/CSS/JavaScript with accessibility focus
- **Audio**: MIDI integration for chord input/output
- **ML**: PyTorch for policy training

### 5. Future Extensions
- Real SO101 hardware support
- Guitar tablature import
- Multi-instrument support
- Collaborative playing features
- Mobile app version

## Next Steps
1. Set up LeRobot with xarm simulation
2. Create basic strumming environment
3. Implement simple down-up pattern
4. Build minimal UI for testing
5. Iterate based on accessibility testing
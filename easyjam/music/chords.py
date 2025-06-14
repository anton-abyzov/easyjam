"""Chord definitions and strumming patterns"""

from dataclasses import dataclass
from typing import List, Dict
import numpy as np


@dataclass
class Chord:
    """Represents a guitar chord"""
    name: str
    frets: List[int]  # Fret positions for each string (0 = open, -1 = muted)
    fingering: List[int]  # Which finger to use (0 = none)
    difficulty: int  # 1-5 difficulty rating
    
    def __str__(self):
        return f"{self.name} chord"


@dataclass 
class StrummingPattern:
    """Represents a strumming pattern"""
    name: str
    pattern: List[str]  # List of 'down', 'up', 'mute', 'rest'
    tempo: int  # BPM
    time_signature: tuple  # e.g., (4, 4)
    difficulty: int  # 1-5 difficulty rating
    
    def get_duration_per_beat(self):
        """Get duration in seconds per beat"""
        return 60.0 / self.tempo
    
    def get_pattern_duration(self):
        """Get total duration of the pattern"""
        beats = len(self.pattern) / self.time_signature[0]
        return beats * self.get_duration_per_beat()


# Common chord definitions
CHORD_LIBRARY = {
    # Open chords
    'G': Chord('G', [3, 2, 0, 0, 3, 3], [3, 2, 0, 0, 4, 4], 1),
    'C': Chord('C', [-1, 3, 2, 0, 1, 0], [0, 3, 2, 0, 1, 0], 1),
    'D': Chord('D', [-1, -1, 0, 2, 3, 2], [0, 0, 0, 1, 3, 2], 1),
    'Em': Chord('Em', [0, 2, 2, 0, 0, 0], [0, 2, 3, 0, 0, 0], 1),
    'Am': Chord('Am', [-1, 0, 2, 2, 1, 0], [0, 0, 2, 3, 1, 0], 1),
    'E': Chord('E', [0, 2, 2, 1, 0, 0], [0, 2, 3, 1, 0, 0], 1),
    'A': Chord('A', [-1, 0, 2, 2, 2, 0], [0, 0, 1, 2, 3, 0], 1),
    
    # Barre chords
    'F': Chord('F', [1, 3, 3, 2, 1, 1], [1, 3, 4, 2, 1, 1], 3),
    'Bm': Chord('Bm', [-1, 2, 4, 4, 3, 2], [0, 1, 3, 4, 2, 1], 3),
    
    # Power chords
    'G5': Chord('G5', [3, 5, 5, -1, -1, -1], [1, 3, 4, 0, 0, 0], 2),
    'A5': Chord('A5', [-1, 0, 2, 2, -1, -1], [0, 0, 1, 2, 0, 0], 2),
    'D5': Chord('D5', [-1, -1, 0, 2, 3, -1], [0, 0, 0, 1, 3, 0], 2),
}


# Common strumming patterns
PATTERN_LIBRARY = {
    # Basic patterns
    'basic_down': StrummingPattern(
        'Basic Down', 
        ['down', 'rest', 'down', 'rest'],
        120, (4, 4), 1
    ),
    
    'basic_alternating': StrummingPattern(
        'Basic Alternating',
        ['down', 'up', 'down', 'up'],
        120, (4, 4), 1
    ),
    
    'folk_pattern': StrummingPattern(
        'Folk Pattern',
        ['down', 'down', 'up', 'rest', 'up', 'down', 'up', 'rest'],
        100, (4, 4), 2
    ),
    
    'rock_pattern': StrummingPattern(
        'Rock Pattern',
        ['down', 'rest', 'down', 'up', 'rest', 'up', 'down', 'up'],
        130, (4, 4), 2
    ),
    
    'reggae_pattern': StrummingPattern(
        'Reggae Pattern',
        ['rest', 'up', 'rest', 'up', 'rest', 'up', 'rest', 'up'],
        80, (4, 4), 3
    ),
    
    'flamenco_pattern': StrummingPattern(
        'Flamenco Pattern',
        ['down', 'up', 'up', 'down', 'up', 'down', 'down', 'up'],
        140, (4, 4), 4
    ),
}


class ChordProgression:
    """Manages chord progressions"""
    
    def __init__(self, chords: List[str], pattern: str = 'basic_alternating'):
        self.chords = [CHORD_LIBRARY.get(c, CHORD_LIBRARY['C']) for c in chords]
        self.pattern = PATTERN_LIBRARY.get(pattern, PATTERN_LIBRARY['basic_alternating'])
        self.current_chord_index = 0
        self.current_pattern_index = 0
        
    def get_current_chord(self):
        """Get the current chord"""
        return self.chords[self.current_chord_index]
    
    def get_next_strum(self):
        """Get the next strum action"""
        strum = self.pattern.pattern[self.current_pattern_index]
        self.current_pattern_index = (self.current_pattern_index + 1) % len(self.pattern.pattern)
        return strum
    
    def advance_chord(self):
        """Move to the next chord in the progression"""
        self.current_chord_index = (self.current_chord_index + 1) % len(self.chords)
        
    def reset(self):
        """Reset the progression"""
        self.current_chord_index = 0
        self.current_pattern_index = 0


def get_chord_suggestions(difficulty_level: int = 1) -> List[str]:
    """Get chord suggestions based on difficulty level"""
    suggestions = []
    for name, chord in CHORD_LIBRARY.items():
        if chord.difficulty <= difficulty_level:
            suggestions.append(name)
    return suggestions


def get_pattern_suggestions(difficulty_level: int = 1) -> List[str]:
    """Get pattern suggestions based on difficulty level"""
    suggestions = []
    for name, pattern in PATTERN_LIBRARY.items():
        if pattern.difficulty <= difficulty_level:
            suggestions.append(name)
    return suggestions


if __name__ == "__main__":
    # Test chord progression
    progression = ChordProgression(['G', 'C', 'D', 'Em'], 'folk_pattern')
    
    print(f"Playing chord progression with {progression.pattern.name}")
    print(f"Tempo: {progression.pattern.tempo} BPM")
    
    for i in range(16):
        if i % 4 == 0:
            print(f"\nChord: {progression.get_current_chord().name}")
            if i > 0:
                progression.advance_chord()
        
        strum = progression.get_next_strum()
        print(f"  Beat {i+1}: {strum}")
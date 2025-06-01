"""
Audio Manager for Dino Game
Handles all audio-related functionality including background music and sound effects
"""

import pygame
import os
import time

class AudioManager:
    def __init__(self):
        """Initialize the audio manager"""
        self.sounds = {}
        self.music_file = None
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.music_enabled = True
        self.sound_enabled = True
        
        # Try to initialize the mixer
        self.audio_available = False
        try:
            pygame.mixer.init()
            self.audio_available = True
            print("Audio system initialized successfully")
        except pygame.error as e:
            print(f"Audio system initialization failed: {e}")
            print("Game will run without sound")
            return
            
        # Load background music
        self.load_music()
        
        # Load sound effects
        self.load_sounds()
    
    def load_music(self):
        """Load background music from the audio directory"""
        if not self.audio_available:
            return
            
        # Look for background music file in the audio directory
        if os.path.exists('audio'):
            bgm_path = os.path.join('audio', 'game_bgm.mp3')
            if os.path.exists(bgm_path):
                self.music_file = bgm_path
                print(f"Background music loaded: {self.music_file}")
            else:
                # If specific file not found, use any MP3 file
                for file in os.listdir('audio'):
                    if file.lower().endswith('.mp3') and not file.lower().startswith('8-bit-jump') and not file.lower().startswith('game-over'):
                        self.music_file = os.path.join('audio', file)
                        print(f"Background music loaded: {self.music_file}")
                        break
        
        if not self.music_file:
            print("No background music found in audio directory")
    
    def load_sounds(self):
        """Load sound effects from the audio directory"""
        if not self.audio_available:
            return
            
        # Load jump sound
        jump_path = os.path.join('audio', '8-bit-jump.mp3')
        if os.path.exists(jump_path):
            try:
                self.sounds['jump'] = pygame.mixer.Sound(jump_path)
                self.sounds['jump'].set_volume(self.sound_volume)
                print(f"Jump sound loaded: {jump_path}")
            except pygame.error as e:
                print(f"Could not load jump sound: {e}")
        
        # Load game over sound
        game_over_path = os.path.join('audio', 'game-over.mp3')
        if os.path.exists(game_over_path):
            try:
                self.sounds['game_over'] = pygame.mixer.Sound(game_over_path)
                self.sounds['game_over'].set_volume(self.sound_volume)
                print(f"Game over sound loaded: {game_over_path}")
            except pygame.error as e:
                print(f"Could not load game over sound: {e}")
    
    def play_music(self):
        """Start playing background music in a loop"""
        if not self.audio_available or not self.music_file or not self.music_enabled:
            return
            
        try:
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            print("Background music started")
        except pygame.error as e:
            print(f"Could not play background music: {e}")
    
    def stop_music(self):
        """Stop the background music"""
        if not self.audio_available:
            return
            
        try:
            pygame.mixer.music.stop()
            print("Background music stopped")
        except pygame.error as e:
            print(f"Error stopping music: {e}")
    
    def pause_music(self):
        """Pause the background music"""
        if not self.audio_available:
            return
            
        try:
            pygame.mixer.music.pause()
        except pygame.error:
            pass
    
    def unpause_music(self):
        """Unpause the background music"""
        if not self.audio_available:
            return
            
        try:
            pygame.mixer.music.unpause()
        except pygame.error:
            pass
    
    def play_sound(self, sound_name):
        """Play a sound effect by name"""
        if not self.audio_available or not self.sound_enabled:
            return
            
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except pygame.error:
                pass
    
    def toggle_music(self):
        """Toggle background music on/off"""
        if not self.audio_available:
            return
            
        self.music_enabled = not self.music_enabled
        
        if self.music_enabled:
            self.play_music()
        else:
            self.stop_music()
        
        return self.music_enabled
    
    def toggle_sound(self):
        """Toggle sound effects on/off"""
        if not self.audio_available:
            return
            
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        if not self.audio_available:
            return
            
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except pygame.error:
            pass
    
    def set_sound_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        if not self.audio_available:
            return
            
        self.sound_volume = max(0.0, min(1.0, volume))
        
        for sound in self.sounds.values():
            try:
                sound.set_volume(self.sound_volume)
            except pygame.error:
                pass

# Create a global instance for easy importing
audio_manager = None

def initialize():
    """Initialize the audio manager"""
    global audio_manager
    audio_manager = AudioManager()
    return audio_manager

def get_instance():
    """Get the audio manager instance, creating it if necessary"""
    global audio_manager
    if audio_manager is None:
        audio_manager = AudioManager()
    return audio_manager

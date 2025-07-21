import pgzrun
import pygame
import av
import os
import numpy as np
import time
import sys
from raphael_level import run_raphael_level
from donatello_level import run_donatello_level
from leonardo_level import run_leonardo_level
from mars import run_mars_level
from pygame import Rect

# Game state
game_states = {
    "START_SCREEN": 0,
    "INTRO": 1,
    "RAPHAEL_LEVEL": 2,
    "DONATELLO_LEVEL": 3,
    "LEONARDO_LEVEL": 4,
    "MARS_LEVEL": 5,
    "GAME_OVER": 6
}
current_state = game_states["START_SCREEN"]
current_level = None
level_completed = False

# Video and intro variables
intro_playing = False
video_start_time = 0
frame_duration = 0
text_visible = True
text_timer = 0
text_flash_interval = 0.5
intro_audio_sound = None
playback_speed_multiplier = 1.2

# Skip button variables
skip_button_visible = False
skip_button_rect = Rect(0, 0, 120, 40)
skip_button_hover = False
skip_button_timer = 0

# Game over timer
game_over_timer = 0

# Video playback variables
intro_video_path = "videos/intro.mp4"
intro_audio_path = "sounds2/intro_audio.mp3"
intro_container = None
video_stream = None
video_surface = None

# Screen size
WIDTH = 1250
HEIGHT = 720

def setup_skip_button():
    """Position the skip button in the bottom right corner with some margin"""
    global skip_button_rect
    skip_button_rect = Rect(WIDTH - 150, HEIGHT - 60, 120, 40)

# Initialize pygame
pygame.init()
pygame.mixer.init()
setup_skip_button()

def reset_game_state():
    """Reset all game state variables"""
    global current_state, current_level, level_completed, intro_playing
    global video_start_time, text_visible, text_timer, skip_button_visible
    global intro_container, video_stream, video_surface, intro_audio_sound, skip_button_timer
    global game_over_timer

    current_state = game_states["START_SCREEN"]
    current_level = None
    level_completed = False
    intro_playing = False
    video_start_time = 0
    text_visible = True
    text_timer = 0
    skip_button_visible = False
    skip_button_timer = 0
    game_over_timer = 0

    # Reset video related variables
    if intro_container:
        intro_container.close()
    intro_container = None
    video_stream = None
    video_surface = None

    # Stop any playing audio
    if intro_audio_sound:
        intro_audio_sound.stop()
        intro_audio_sound = None

# Music
def play_start_music():
    pygame.mixer.music.load('sounds2/start.mp3')
    pygame.mixer.music.play(-1, start=2.0)

def stop_start_music():
    pygame.mixer.music.stop()

# Load intro video
def load_intro():
    global intro_container, video_stream, frame_duration
    try:
        intro_container = av.open(intro_video_path)
        video_stream = next(s for s in intro_container.streams if s.type == 'video')
        if video_stream.average_rate:
            frame_duration = 1.0 / float(video_stream.average_rate)
        else:
            frame_duration = 0.033
    except Exception as e:
        print(f"Error loading intro video: {e}")

def play_video_frame():
    global intro_container, video_stream, video_surface, intro_playing, video_start_time
    global current_state, level_completed, skip_button_visible, skip_button_timer

    if intro_container and video_stream and intro_playing:
        current_time = time.time()
        if current_time - video_start_time >= frame_duration / playback_speed_multiplier:
            video_start_time = current_time
            try:
                frame = next(intro_container.decode(video_stream))
                frame_np = frame.to_ndarray(format='rgb24')
                video_surface = pygame.surfarray.make_surface(frame_np).convert()
                return True
            except (StopIteration, av.EOFError):
                intro_playing = False
                if current_level == "raphael":
                    current_state = game_states["RAPHAEL_LEVEL"]
                elif current_level == "donatello":
                    current_state = game_states["DONATELLO_LEVEL"]
            except OSError as e:
                print(f"Error decoding video frame: {e}")
                intro_playing = False
    return False
def play_intro_audio():
    global intro_audio_sound
    try:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        intro_audio_sound = pygame.mixer.Sound(intro_audio_path)
        intro_audio_sound.play()
    except Exception as e:
        print(f"Error playing intro audio: {e}")

def run_current_level():
    global current_state, level_completed, current_level

    try:
        if current_level == "raphael":
            level_completed = run_raphael_level()
        elif current_level == "donatello":
            level_completed = run_donatello_level()
        elif current_level == "leonardo":
            level_completed = run_leonardo_level()
        elif current_level == "mars":
            level_completed = run_mars_level()

        # Handle level completion consistently for all levels
        if level_completed:
            # If level is completed successfully, return to start screen
            reset_game_state()
            play_start_music()
        else:
            # If level is not completed successfully, go to game over state
            current_state = game_states["GAME_OVER"]
    except Exception as e:
        print(f"Error running level: {e}")
        current_state = game_states["GAME_OVER"]

def skip_intro():
    global intro_playing, current_state, current_level
    intro_playing = False
    if current_level == "raphael":
        current_state = game_states["RAPHAEL_LEVEL"]
    elif current_level == "donatello":
        current_state = game_states["DONATELLO_LEVEL"]
    elif current_level == "leonardo":
        current_state = game_states["LEONARDO_LEVEL"]
    elif current_level == "mars":
        current_state = game_states["MARS_LEVEL"]
    if intro_audio_sound:
        intro_audio_sound.stop()

def update_skip_button_hover(pos):
    global skip_button_hover
    skip_button_hover = skip_button_rect.collidepoint(pos)

def update():
    global text_timer, text_visible, skip_button_visible, skip_button_timer, game_over_timer

    if current_state == game_states["START_SCREEN"]:
        text_timer += 1 / 60
        if text_timer >= text_flash_interval:
            text_timer = 0
            text_visible = not text_visible

    elif current_state == game_states["INTRO"]:
        play_video_frame()
        # Update skip button timer and visibility
        skip_button_timer += 1 / 60
        if skip_button_timer >= 0.5:  # Show after 0.5 seconds
            skip_button_visible = True

    elif current_state in [game_states["RAPHAEL_LEVEL"], game_states["DONATELLO_LEVEL"], game_states["LEONARDO_LEVEL"], game_states["MARS_LEVEL"]]:
        run_current_level()

    elif current_state == game_states["GAME_OVER"]:
        # Add a delay before resetting the game state
        global game_over_timer

        game_over_timer += 1 / 60  # Increment timer (assuming 60 FPS)

        # After 2 seconds, reset the game state and return to start screen
        if game_over_timer >= 2:
            reset_game_state()
            play_start_music()

def draw():
    screen.fill("black")

    if current_state == game_states["START_SCREEN"]:
        screen.blit('tbg', (0, 0))
        if text_visible:
            screen.draw.text("Press 1 for Raphael Level", (450, 500), fontsize=40, color="white")
            screen.draw.text("Press 2 for Donatello Level", (450, 560), fontsize=40, color="white")
            screen.draw.text("Press 3 for Leonardo Level", (450, 620), fontsize=40, color="white")

    elif current_state == game_states["INTRO"] and video_surface:
        rotated_surface = pygame.transform.rotate(video_surface, -90)
        flipped_surface = pygame.transform.flip(rotated_surface, True, False)
        rotated_rect = flipped_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(flipped_surface, rotated_rect)

        if skip_button_visible:
            button_color = (200, 0, 0) if skip_button_hover else (150, 0, 0)
            screen.draw.filled_rect(Rect(skip_button_rect), button_color)
            screen.draw.text("Skip", (skip_button_rect.x + 30, skip_button_rect.y + 10),
                             fontsize=25, color="white")

    elif current_state in [game_states["RAPHAEL_LEVEL"], game_states["DONATELLO_LEVEL"], game_states["LEONARDO_LEVEL"], game_states["MARS_LEVEL"]]:
        screen.draw.text("Game is running...", (100, 100), fontsize=40, color="white")

    elif current_state == game_states["GAME_OVER"]:
        screen.draw.text("Game Over - Returning to Start Screen", (WIDTH//2 - 200, HEIGHT//2), fontsize=40, color="white")

def on_key_down(key):
    global current_state, current_level, intro_playing, video_start_time, skip_button_timer

    if current_state == game_states["START_SCREEN"]:
        if key == keys.K_1:
            current_level = "raphael"
        elif key == keys.K_2:
            current_level = "donatello"
        elif key == keys.K_3:
            current_level = "leonardo"
        elif key == keys.K_4:
            current_level = "mars"
        else:
            current_level = "raphael"
        current_state = game_states["INTRO"]
        intro_playing = True
        play_intro_audio()
        stop_start_music()
        video_start_time = time.time()
        skip_button_timer = 0
        skip_button_visible = False
        load_intro()

def on_mouse_down(pos):
    global current_state, current_level

    if current_state == game_states["INTRO"] and skip_button_visible and skip_button_rect.collidepoint(pos):
        skip_intro()
    elif current_state == game_states["START_SCREEN"]:
        current_level = "raphael"
        on_key_down(keys.K_1)

def on_mouse_move(pos):
    if current_state == game_states["INTRO"] and skip_button_visible:
        update_skip_button_hover(pos)

# Initialize game
load_intro()
play_start_music()

pgzrun.go()

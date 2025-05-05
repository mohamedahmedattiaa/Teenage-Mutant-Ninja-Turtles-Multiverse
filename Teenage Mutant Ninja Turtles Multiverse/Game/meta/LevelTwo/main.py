import pgzrun
import pygame
import av
import os
import numpy as np
import time

# Game state
game_started = False
intro_playing = False
audio_playing = False
show_start_screen = True
video_start_time = 0
frame_duration = 0
text_visible = True
text_timer = 0
text_flash_interval = 0.5
intro_audio_sound = None
playback_speed_multiplier = 1.2

# Video playback variables
intro_video_path = "videos/intro.mp4"
intro_audio_path = "sounds/intro_audio.mp3"
intro_container = None
video_stream = None
video_surface = None

# Screen size
WIDTH = 1250
HEIGHT = 720

# Music
def play_start_music():
    pygame.mixer.music.load('sounds/start.mp3')
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
            print(f"Video Average Frame Rate: {video_stream.average_rate:.2f} FPS, Frame Duration: {frame_duration:.4f} seconds")
        else:
            print("Warning: Could not determine video frame rate. Using default.")
            frame_duration = 0.033
    except Exception as e:
        print(f"Error loading intro video: {e}")

# Play a single frame
def play_video_frame():
    global intro_container, video_stream, video_surface, intro_playing, video_start_time, frame_duration, playback_speed_multiplier, game_started
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
                game_started = True
            except OSError as e:
                print(f"Error decoding video frame: {e}")
                intro_playing = False
                game_started = True
    return False

# Play intro audio
def play_intro_audio():
    global intro_audio_sound, audio_playing
    try:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        intro_audio_sound = pygame.mixer.Sound(intro_audio_path)
        intro_audio_sound.play()
        audio_playing = True
    except pygame.error as e:
        print(f"Pygame error: {e}")
    except FileNotFoundError:
        print(f"Audio file not found: {intro_audio_path}")

# Update function
def update():
    global text_timer, text_visible
    if intro_playing:
        play_video_frame()
    elif show_start_screen:
        text_timer += 1 / 60
        if text_timer >= text_flash_interval:
            text_timer = 0
            text_visible = not text_visible

# Draw function
def draw():
    screen.fill("black")
    if show_start_screen:
        screen.blit('tbg', (0, 0))  # NOTE: tbg.png must be inside images/
        if text_visible:
            screen.draw.text("Press any button to start", (450, 560), fontsize=40, color="white")
    elif video_surface:
        rotated_surface = pygame.transform.rotate(video_surface, -90)
        flipped_surface = pygame.transform.flip(rotated_surface, True, False)
        rotated_rect = flipped_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(flipped_surface, rotated_rect)
    elif game_started:
        screen.draw.text("Game is running...", (100, 100), fontsize=40, color="white")

# Start video and audio
def on_key_down():
    global intro_playing, show_start_screen, video_start_time
    if show_start_screen:
        show_start_screen = False
        intro_playing = True
        play_intro_audio()
        stop_start_music()
        video_start_time = time.time()

# Load video and music
load_intro()
play_start_music()

pgzrun.go()

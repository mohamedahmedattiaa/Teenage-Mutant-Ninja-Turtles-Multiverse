import pyzero
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
intro_video_path = r"/Game/meta/videos/intro.mp4"
intro_audio_path = r"/Game/meta/sounds/intro_audio.mp3"
intro_container = None
video_stream = None
video_surface = None

# Screen size
WIDTH = 1250
HEIGHT = 720

# Load background image
background_image_path = r'D:\projects\project\Game\meta\images\tbg.png'
background_image = None

# Setup pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Start Screen")

clock = pygame.time.Clock()

# Music
def play_start_music():
    pygame.mixer.music.load(r'/Game/meta/sounds/start.mp3')
    pygame.mixer.music.play(-1, start=2.0)

def stop_start_music():
    pygame.mixer.music.stop()

# Function to load the intro video and get frame rate
def load_intro():
    global intro_container, video_stream, frame_duration
    try:
        intro_container = av.open(intro_video_path)
        video_stream = next(s for s in intro_container.streams if s.type == 'video')
        if video_stream.average_rate:
            frame_duration = 1.0 / float(video_stream.average_rate)
            print(f"Video Average Frame Rate: {video_stream.average_rate:.2f} FPS, Frame Duration: {frame_duration:.4f} seconds")
        else:
            print("Warning: Could not determine video frame rate. Playback might be too fast.")
            frame_duration = 0.033  # Default to ~30 FPS
    except Exception as e:
        print(f"Error loading intro video: {e}")

# Function to play the next video frame with timing
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
                return False
            except Exception as e:
                print(f"Error decoding video frame: {e}")
                intro_playing = False
                game_started = True
                return False
    return False

def play_intro_audio():
    global intro_audio_sound, audio_playing
    try:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        intro_audio_sound = pygame.mixer.Sound(intro_audio_path)
        intro_audio_sound.play()
        audio_playing = True
    except Exception as e:
        print(f"Pygame error loading or playing intro audio: {e}")

def update_game():
    global game_started, intro_playing, text_timer, text_visible, show_start_screen

    if intro_playing:
        play_video_frame()
    elif show_start_screen:
        text_timer += clock.get_time() / 1000.0
        if text_timer >= text_flash_interval:
            text_timer = 0
            text_visible = not text_visible

def draw_game():
    screen.fill((0, 0, 0))
    if show_start_screen:
        if background_image:
            screen.blit(background_image, (0, 0))
        if text_visible:
            font = pygame.font.Font(None, 60)
            text = font.render("Press any button to start", True, (255, 255, 255))
            screen.blit(text, (450, 560))
    elif video_surface:
        rotated_surface = pygame.transform.rotate(video_surface, -90)
        flipped_surface = pygame.transform.flip(rotated_surface, True, False)
        rotated_rect = flipped_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(flipped_surface, rotated_rect)
    elif game_started:
        font = pygame.font.Font(None, 60)
        text = font.render("Game is running...", True, (255, 255, 255))
        screen.blit(text, (100, 100))

def main():
    global intro_playing, show_start_screen, video_start_time, background_image

    load_intro()
    play_start_music()

    try:
        background_image = pygame.image.load(background_image_path)
    except Exception as e:
        print(f"Error loading background image: {e}")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if show_start_screen:
                    show_start_screen = False
                    intro_playing = True
                    play_intro_audio()
                    stop_start_music()
                    video_start_time = time.time()

        update_game()
        draw_game()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

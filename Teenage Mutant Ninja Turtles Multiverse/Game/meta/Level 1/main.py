import pygame
import os

# ========== Initialize ==========
pygame.init()
pygame.mixer.init()

# ========== Screen Settings ==========
WIDTH, HEIGHT = 1200, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Leonardo Game")
clock = pygame.time.Clock()
FPS = 60

# ========== Game State ==========
game_started = False
show_start_screen = True
text_visible = True
text_timer = 0
text_flash_interval = 0.5
player_action = None

# ========== Paths ==========
ASSET_PATH = os.path.join(r"C:\Users\mena\Desktop\MyLevel1", 'assets')
IMAGE_PATH = os.path.join(ASSET_PATH, 'images')
SOUND_PATH = os.path.join(ASSET_PATH, 'sounds')

# ========== Load Assets ==========
background = pygame.transform.scale(
    pygame.image.load(os.path.join(r"C:\Users\mena\Desktop\MyLevel1\images", "background.png")).convert_alpha(),
    (WIDTH, HEIGHT)
)


start_music_path = os.path.join(SOUND_PATH, "start_sound.wav")
sigh_sound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "sigh.wav"))
moan_sound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "group_pain_sound.wav"))

# ========== Player ==========
from player import Player
player = Player(100, 500)

# ========== Start Music ==========
pygame.mixer.music.load(start_music_path)
pygame.mixer.music.play(-1, start=2.0)

# ========== Game Loop ==========
running = True
while running:
    dt = clock.tick(FPS) / 1000  # لتحسين التحديث حسب الوقت الحقيقي

    # ========== Event Handling ==========
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if show_start_screen:
                show_start_screen = False
                game_started = True
                sigh_sound.play()
                pygame.mixer.music.stop()

            elif game_started and player_action is None:
                if event.key == pygame.K_h:
                    player_action = "help"
                    moan_sound.play()
                    player.set_state('damaging')

                elif event.key == pygame.K_b:
                    player_action = "go_to_boss"
                    player.set_state('combo1')

    # ========== Update ==========
    if show_start_screen:
        text_timer += dt
        if text_timer >= text_flash_interval:
            text_timer = 0
            text_visible = not text_visible
    elif game_started:
        player.update(dt)

    # ========== Draw ==========
    screen.blit(background, (0, 0))

    if show_start_screen:
        if text_visible:
            font = pygame.font.SysFont(None, 50)
            text_surface = font.render("Press any button to start", True, (255, 255, 255))
            screen.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, 560)))

    elif game_started:
        font = pygame.font.SysFont(None, 40)
        screen.blit(font.render("Game is running...", True, (255, 255, 255)), (100, 100))

        if player_action is None:
            msg = "Press H to help the injured or B to go to the boss."
        elif player_action == "help":
            msg = "You helped the injured... Now continue your journey."
        else:
            msg = "You chose to fight the boss!"

        screen.blit(font.render(msg, True, (255, 255, 255)), (350, 300))
        player.draw(screen)

    pygame.display.flip()

pygame.quit()

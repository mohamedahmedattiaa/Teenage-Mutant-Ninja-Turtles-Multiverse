import pygame
import sys
import random

def run_donatello_level():
    pygame.init()

    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Donatello Coin Challenge")
    clock = pygame.time.Clock()

    # ================== sounds ==================
    pygame.mixer.init()
    pygame.mixer.music.load("sounds3/background_music.mp3")
    coin_sound = pygame.mixer.Sound("sounds3/coin.mp3")
    correct_sound = pygame.mixer.Sound("sounds3/correct.wav")
    wrong_sound = pygame.mixer.Sound("sounds3/wrong.wav")
    boss_alert_sound = pygame.mixer.Sound("sounds3/boss_alert.wav")
    game_over = pygame.mixer.Sound("sounds3/gameover.mp3")
    win_sound = pygame.mixer.Sound("sounds3/win.mp3")
    dialogue_sound = pygame.mixer.Sound("sounds3/dialogue.mp3")

    # ================== colors and fonts ==================
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    PURPLE = (128, 0, 128)
    BLUE = (0, 0, 255)
    GRAY = (100, 100, 100)
    DARK_GRAY = (50, 50, 50)
    LIGHT_PURPLE = (180, 120, 180)  # For hover effect

    font = pygame.font.SysFont("arial", 36)
    big_font = pygame.font.SysFont("arial", 48)
    small_font = pygame.font.SysFont("arial", 30)

    # ================== images ==================
    don_frames = [pygame.image.load(f"images3/walk{i}.png").convert_alpha() for i in range(1, 3)]
    fall_frames = [pygame.image.load(f"images3/die{i}.png").convert_alpha() for i in range(1, 3)]
    yellow_question_img = pygame.transform.scale(pygame.image.load("images3/yellow.png").convert_alpha(), (40, 40))
    red_question_img = pygame.transform.scale(pygame.image.load("images3/red.png").convert_alpha(), (40, 40))
    bg_img = pygame.transform.scale(pygame.image.load("images3/world9.png").convert(), (WIDTH, HEIGHT))
    monster_stand_frames = [pygame.image.load(f"images3/attack{i}.png").convert_alpha() for i in range(1, 17)]
    monster_die_frames = [pygame.image.load(f"images3/Death{i}.png").convert_alpha() for i in range(1, 9)]
    question_box_img = pygame.transform.scale(pygame.image.load("images3/box.png").convert_alpha(), (600, 600))
    intro_img = pygame.image.load("images3/intro_scene.png").convert()

    # ================== questions ==================
    questions = [
        {"text": "What keyword defines a function in Python?", "answer": "def"},
        {"text": "Which loop is commonly used with range()?", "answer": "for"},
        {"text": "What keyword returns a value from a function?", "answer": "return"},
        {"text": "What data type is used to store True or False?", "answer": "bool"},
        {"text": "Which keyword is used to start a conditional?", "answer": "if"},
        {"text": "How do you start a comment in Python?", "answer": "#"},
        {"text": "What data structure uses keys and values?", "answer": "dict"},
    ]

    def generate_questions():
        coins = []
        for i in range(6):
            coins.append(
                {"x": random.randint(800, 3000), "y": random.randint(250, 350), "collected": False, "trigger": False})
        coins.append({"x": random.randint(3200, 4000), "y": random.randint(250, 350), "collected": False, "trigger": True})
        return coins

    def draw_text(surface, text, pos, font, color=RED, shadow=False):
        if shadow:
            shadow_text = font.render(text, True, BLACK)
            surface.blit(shadow_text, (pos[0] + 2, pos[1] + 2))
        rendered = font.render(text, True, color)
        surface.blit(rendered, pos)

    def draw_dialog_bubble(surface, text, pos, width=1000, height=100, alpha=180):
        bubble = pygame.Surface((width, height), pygame.SRCALPHA)
        bubble.fill((0, 0, 0, alpha))
        surface.blit(bubble, pos)
        draw_text(surface, text, (pos[0] + 20, pos[1] + 25), font, WHITE)

    def show_end_screen(message, color):
        screen.fill(BLACK)
        draw_text(screen, message, (WIDTH // 2 - 300, HEIGHT // 2), big_font, color)
        pygame.display.flip()
        pygame.time.wait(4000)

    # ================== pause menu ==================
    def draw_pause_menu(sound_on):
        # Draw the game background
        start_x = bg_offset % bg_img.get_width()
        for i in range(-1, (WIDTH // bg_img.get_width()) + 2):
            screen.blit(bg_img, (start_x + i * bg_img.get_width(), 0))

        # Semi-transparent overlay for blur effect
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark semi-transparent layer
        screen.blit(overlay, (0, 0))

        # Draw pause menu panel (centered, semi-transparent, rounded)
        panel_width, panel_height = 400, 300
        panel_x, panel_y = (WIDTH - panel_width) // 2, (HEIGHT - panel_height) // 2
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (50, 50, 50, 200), (0, 0, panel_width, panel_height), border_radius=20)
        screen.blit(panel, (panel_x, panel_y))

        # Pause menu title with shadow
        draw_text(screen, "Pause Menu", (panel_x + 100, panel_y + 30), big_font, WHITE, shadow=True)

        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()

        # Sound button
        sound_button = pygame.Rect(panel_x + 100, panel_y + 100, 200, 60)
        sound_color = LIGHT_PURPLE if sound_button.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, sound_color, sound_button, border_radius=10)
        sound_text = "Sound: ON" if sound_on else "Sound: OFF"
        draw_text(screen, sound_text, (panel_x + 120, panel_y + 110), font, WHITE, shadow=True)

        # Exit button
        exit_button = pygame.Rect(panel_x + 100, panel_y + 180, 200, 60)
        exit_color = LIGHT_PURPLE if exit_button.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, exit_color, exit_button, border_radius=10)
        draw_text(screen, "Exit Game", (panel_x + 120, panel_y + 190), font, WHITE, shadow=True)

        return sound_button, exit_button

    # Initialize game state
    coins = generate_questions()
    intro_dialogs = [
        "Donatello: I never thought this day would come...",
        "Donatello: The evil robots have taken over the world.",
        "Donatello: Cities, labs—even schools… all under their control.",
        "Donatello: But I won't stand by.",
        "Donatello: The answer isn't brute force…",
        "Donatello: It's their own weapon—",
        "Donatello: Intelligence.",
        "Donatello: If I can understand their system, solve their code problems,",
        "Donatello: I might destroy the virus before it spreads!.",
        "Donatello: I might free the world.",
        "Donatello: And I'm ready.",
        "Donatello: I'm Donatello…",
        "Donatello: and this is my fight.",
        "Press Enter to Start"
    ]
    show_intro = True
    intro_dialog_index = 0
    intro_dialogue_playing = False

    score = 0
    correct_answers = 0
    feedback = ""
    feedback_color = WHITE
    feedback_timer = 0

    show_question = False
    current_question = None
    user_input = ""

    bottom_limit = 300
    lives = 3
    is_dead = False
    death_timer = 0
    death_frame_index = 0

    monster_shown = False
    monster_state = "standing"
    monster_frame_index = 0
    monster_frame_timer = 0
    monster_frame_speed = 0.1

    monster_x = 1000
    monster_y = 620

    don_bar_x = 50
    don_bar_y = 50
    monster_bar_x = 50
    monster_bar_y = 100
    bar_max_width = 300
    bar_height = 25

    speed = 5
    x = 100
    y = HEIGHT - 150
    gravity = 0.5
    jump_speed = 12
    on_ground = True

    donatello_animation_timer = 0
    donatello_animation_delay = 200  # ms
    frame_index = 0
    facing_right = True

    red_img = red_question_img
    yellow_img = yellow_question_img
    question_box = question_box_img
    bg_offset = 0

    paused = False
    sound_on = True
    boss_alert_played = False

    level_completed = False
    level_failed = False

    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False  # Game was exited

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not show_intro:
                    paused = not paused  # Toggle pause state

                if show_intro and event.key == pygame.K_RETURN:
                    if intro_dialog_index < len(intro_dialogs) - 1:
                        intro_dialog_index += 1
                    else:
                        show_intro = False
                        dialogue_sound.stop()
                        if sound_on:
                            pygame.mixer.music.play(-1)

                if show_question and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        answer_correct = user_input.strip().lower() == current_question["answer"]
                        if sound_on:
                            boss_alert_sound.stop()
                        if answer_correct:
                            score += 1
                            correct_answers += 1
                            feedback = "Correct!"
                            feedback_color = GREEN
                            if current_question == questions[-1]:
                                monster_state = "dying"
                                monster_frame_index = 0
                                if sound_on:
                                    boss_alert_sound.stop()
                                    win_sound.play()
                            else:
                                if sound_on:
                                    correct_sound.play()
                        else:
                            lives -= 1
                            feedback = "Wrong!" if lives > 0 else "Game Over"
                            feedback_color = RED
                            if sound_on:
                                game_over.play()
                            if lives == 0:
                                is_dead = True
                                show_question = False
                                death_timer = 2
                        feedback_timer = 2
                        show_question = False
                        if current_question == questions[-1] and not answer_correct:
                            feedback = "The monster won!"
                            feedback_color = RED
                            is_dead = True
                            death_timer = 2
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    elif len(event.unicode) == 1:
                        user_input += event.unicode

            if paused and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                sound_button, exit_button = draw_pause_menu(sound_on)
                if sound_button.collidepoint(mouse_pos):
                    sound_on = not sound_on
                    if sound_on:
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.stop()
                        boss_alert_sound.stop()
                        dialogue_sound.stop()
                        coin_sound.stop()
                        correct_sound.stop()
                        wrong_sound.stop()
                        game_over.stop()
                        win_sound.stop()
                if exit_button.collidepoint(mouse_pos):
                    running = False
                    return False  # Game was exited

        if show_intro:
            if not intro_dialogue_playing:
                if sound_on:
                    dialogue_sound.play()
                intro_dialogue_playing = True

            screen.blit(intro_img, (0, 0))
            if intro_dialog_index < len(intro_dialogs):
                current_dialog = intro_dialogs[intro_dialog_index]
                draw_dialog_bubble(screen, current_dialog, (100, 580))
            pygame.display.flip()
            continue

        if paused:
            draw_pause_menu(sound_on)
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        if not show_question and not is_dead:
            moving = False
            if keys[pygame.K_RIGHT]:
                bg_offset -= speed
                facing_right = True
                moving = True
            elif keys[pygame.K_LEFT]:
                bg_offset += speed
                facing_right = False
                moving = True
            if moving:
                now = pygame.time.get_ticks()
                if now - donatello_animation_timer > donatello_animation_delay:
                    frame_index = (frame_index + 1) % len(don_frames)
                    donatello_animation_timer = now
            else:
                frame_index = 0
            if keys[pygame.K_SPACE] and on_ground:
                y_velocity = -jump_speed
                on_ground = False
            if not on_ground:
                y_velocity += gravity
                y += y_velocity
            if y >= bottom_limit:
                y = bottom_limit
                y_velocity = 0
                on_ground = True

            player_rect = pygame.Rect(x, y, don_frames[0].get_width(), don_frames[0].get_height())
            for coin in coins:
                coin_rect = pygame.Rect(coin["x"] + bg_offset, coin["y"], 40, 40)
                if not coin["collected"] and player_rect.colliderect(coin_rect):
                    coin["collected"] = True
                    if sound_on:
                        coin_sound.play()
                    if coin["trigger"]:
                        current_question = questions[-1]
                        monster_shown = True
                        if sound_on and not boss_alert_played:
                            boss_alert_sound.play()
                            boss_alert_played = True
                        if sound_on:
                            pygame.mixer.music.stop()
                    else:
                        if correct_answers < len(questions) - 1:
                            current_question = questions[correct_answers]
                    user_input = ""
                    show_question = True

        screen.fill(BLACK)
        start_x = bg_offset % bg_img.get_width()
        for i in range(-1, (WIDTH // bg_img.get_width()) + 2):
            screen.blit(bg_img, (start_x + i * bg_img.get_width(), 0))

        for coin in coins:
            if not coin["collected"]:
                img = red_img if coin["trigger"] else yellow_img
                screen.blit(img, (coin["x"] + bg_offset, coin["y"]))

        current_frame = fall_frames[death_frame_index] if is_dead else don_frames[frame_index]
        frame_to_draw = current_frame if facing_right else pygame.transform.flip(current_frame, True, False)
        screen.blit(frame_to_draw, (x, y))

        if monster_shown:
            monster_frame_timer += dt
            if monster_frame_timer >= monster_frame_speed:
                monster_frame_timer = 0
                monster_frame_index += 1
                if monster_state == "standing":
                    monster_frame_index %= len(monster_stand_frames)
                elif monster_state == "dying":
                    if monster_frame_index >= len(monster_die_frames):
                        monster_frame_index = len(monster_die_frames) - 1
            frame = (monster_stand_frames if monster_state == "standing" else monster_die_frames)[monster_frame_index]
            screen.blit(frame, frame.get_rect(midbottom=(monster_x, monster_y)))

        progress_ratio = correct_answers / len(questions)
        current_bar_width = int(bar_max_width * progress_ratio)
        bar_color = RED if lives == 1 else PURPLE
        pygame.draw.rect(screen, WHITE, (don_bar_x - 2, don_bar_y - 2, bar_max_width + 4, bar_height + 4))
        pygame.draw.rect(screen, bar_color, (don_bar_x, don_bar_y, current_bar_width, bar_height))

        monster_ratio = 1 - progress_ratio
        monster_width = int(bar_max_width * monster_ratio)
        pygame.draw.rect(screen, WHITE, (monster_bar_x - 2, monster_bar_y - 2, bar_max_width + 4, bar_height + 4))
        pygame.draw.rect(screen, BLUE, (monster_bar_x, monster_bar_y, monster_width, bar_height))

        if feedback_timer > 0:
            draw_text(screen, feedback, (WIDTH // 2 - 100, HEIGHT // 2), big_font, feedback_color)
            feedback_timer -= dt

        if show_question:
            screen.blit(question_box, (300, 100))
            draw_text(screen, current_question["text"], (350, 380), small_font, (0, 0, 139))
            input_text = small_font.render(user_input, True, BLACK)
            screen.blit(input_text, input_text.get_rect(center=(600, 520)))

        pygame.display.flip()

        if is_dead and death_timer > 0:
            death_timer -= dt
        elif is_dead and death_timer <= 0:
            show_end_screen("Game Over... Try Again!", RED)
            level_failed = True
            running = False
        elif monster_state == "dying" and monster_frame_index == len(monster_die_frames) - 1:
            show_end_screen("You Win! Virus Eliminated!", GREEN)
            level_completed = True
            running = False

    # Clean up
    pygame.mixer.music.stop()
    pygame.mixer.stop()

    # Return level completion status
    return level_completed and not level_failed

if __name__ == "__main__":
    run_donatello_level()
    pygame.quit()
    sys.exit()
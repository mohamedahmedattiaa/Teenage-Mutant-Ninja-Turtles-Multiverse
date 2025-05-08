import pygame
import sys
import random

import os

pygame.init()

# إعدادات الشاشة
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Donatello Coin Challenge")
clock = pygame.time.Clock()

# تحميل الصوتيات
pygame.mixer.init()
coin_sound = pygame.mixer.Sound("sounds/coin.wav")
correct_sound = pygame.mixer.Sound("sounds/correct.wav")
wrong_sound = pygame.mixer.Sound("sounds/wrong.wav")

# الألوان
WHITE = (255, 255, 255)
DARK_BLUE = (30, 30, 100)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# تحميل الصور
don_frames = [pygame.image.load(f"images/catch{i}.png").convert_alpha() for i in range(1, 3)]
fall_frames = [pygame.image.load(f"images/die{i}.png").convert_alpha() for i in range(1, 3)]
coin_img = pygame.transform.scale(pygame.image.load("images/coin.png").convert_alpha(), (40, 40))
bg_img = pygame.transform.scale(pygame.image.load("images/world9.png").convert(), (WIDTH, HEIGHT))
bg_width = bg_img.get_width()
monster_stand_frames = [pygame.image.load(f"images/attack{i}.png").convert_alpha() for i in range(1, 17)]
monster_die_frames = [pygame.image.load(f"images/Death{i}.png").convert_alpha() for i in range(1, 14)]

# الأسئلة
questions = [
    {"text": "What keyword defines a function in Python?", "answer": "def"},
    {"text": "Which loop is commonly used with range()?", "answer": "for"},
    {"text": "What keyword returns a value from a function?", "answer": "return"},
    {"text": "What data type is used to store True or False?", "answer": "bool"},
    {"text": "Which keyword is used to start a conditional?", "answer": "if"},
    {"text": "How do you start a comment in Python?", "answer": "#"},
    {"text": "Which function is used to get user input?", "answer": "input"},
    {"text": "What keyword creates a class?", "answer": "class"},
    {"text": "What operator is used for equality check?", "answer": "=="},

]

# إعداد اللاعب
x, y = 300, 300
y_velocity = 0
gravity = 0.5
jump_speed = 10
on_ground = True
speed = 5
frame_index = 0
frame_timer = 0
frame_speed = 0.15
bottom_limit = y
facing_right = True
is_dead = False
death_frame_index = 0
death_timer = 0

# الخلفية
bg_offset = 0


def generate_coins(num=10):
    return [{"x": random.randint(800, 3000), "y": random.randint(250, 350), "collected": False} for _ in range(num)]


coins = generate_coins(10)

# حالة السؤال
show_question = False
current_question = {}
user_input = ""
score = 0
lives = 3
feedback = ""
feedback_timer = 0
correct_answers = 0
monster_shown = False

# الخط
font = pygame.font.SysFont("arial", 36)
big_font = pygame.font.SysFont("arial", 48)

# الوحش
x,y=800,300
monster_state = "standing"
monster_frame_index = 0
monster_frame_timer = 0
monster_frame_speed = 0.2


def trigger_question():
    global show_question, current_question, user_input, correct_answers, monster_shown

    # عرض السؤال بناءً على الإجابات الصحيحة
    if correct_answers < len(questions):
        current_question = questions[correct_answers]
        show_question = True
        user_input = ""

    # بعد الإجابة الصحيحة الخامسة، يظهر الوحش وتصبح الجملة الحاسمة
    if correct_answers == 5 and not monster_shown:
        monster_shown = True
        current_question = {"text": "What data structure uses keys and values", "answer": "dict"}



def draw_text(surface, text, pos, font, color=WHITE):
    rendered = font.render(text, True, color)
    surface.blit(rendered, pos)


def show_end_screen(message, color):
    screen.fill((0, 0, 0))
    draw_text(screen, message, (WIDTH // 2 - 300, HEIGHT // 2), big_font, color)
    pygame.display.flip()
    pygame.time.wait(4000)


# ---------- Main Game Loop ----------
running = True
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if show_question and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                answer_correct = user_input.strip().lower() == current_question["answer"]
                if answer_correct:
                    score += 1
                    correct_answers += 1
                    feedback = "Correct!"
                    feedback_color = GREEN
                    correct_sound.play()
                else:
                    lives -= 1
                    feedback = "Wrong!" if lives > 0 else "Game Over"
                    feedback_color = RED
                    wrong_sound.play()
                    if lives == 0:
                        is_dead = True
                        show_question = False
                        death_timer = 2

                feedback_timer = 2
                show_question = False

                # السؤال النهائي
                if correct_answers >= 5 and monster_shown:
                    if answer_correct:
                        feedback = "You defeated the virus!"
                        feedback_color = GREEN
                        monster_state = "dying"
                        monster_frame_index = 0
                    else:
                        feedback = "The monster won!"
                        feedback_color = RED
                        is_dead = True
                        death_timer = 2
                        show_question = False

            elif event.key == pygame.K_BACKSPACE:
                user_input = user_input[:-1]
            elif len(event.unicode) == 1:
                user_input += event.unicode

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
            frame_timer += frame_speed
            if frame_timer >= 1:
                frame_timer = 0
                frame_index = (frame_index + 1) % len(don_frames)
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

        for coin in coins:
            coin_screen_x = coin["x"] + bg_offset
            if not coin["collected"] and abs(coin_screen_x - x) < 40 and abs(coin["y"] - y) < 40:
                coin["collected"] = True
                coin_sound.play()
                trigger_question()

    # رسم
    screen.fill((0, 0, 0))
    start_x = bg_offset % bg_width
    for i in range(-1, (WIDTH // bg_width) + 2):
        screen.blit(bg_img, (start_x + i * bg_width, 0))

    for coin in coins:
        if not coin["collected"]:
            screen.blit(coin_img, (coin["x"] + bg_offset, coin["y"]))

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
                    monster_frame_index = len(monster_die_frames) - 1  # توقف عند آخر فريم

        frame = (monster_stand_frames if monster_state == "standing" else monster_die_frames)[monster_frame_index]
        screen.blit(frame, (WIDTH // 2 - 100, HEIGHT // 2))

    draw_text(screen, f"Score: {score}", (20, 20), big_font)
    draw_text(screen, f"Lives: {lives}", (WIDTH - 180, 20), big_font)

    if feedback_timer > 0:
        draw_text(screen, feedback, (WIDTH // 2 - 100, HEIGHT // 2), big_font, feedback_color)
        feedback_timer -= dt

    if show_question:
        pygame.draw.rect(screen, WHITE, (280, 160, 720, 360))
        pygame.draw.rect(screen, DARK_BLUE, (300, 180, 680, 320))
        draw_text(screen, current_question["text"], (320, 200), font)
        draw_text(screen, f"Your Answer: {user_input}", (320, 420), big_font, YELLOW)

    pygame.display.flip()

    if is_dead and death_timer > 0:
        death_timer -= dt
    elif is_dead and death_timer <= 0:
        show_end_screen("Game Over... Try Again!", RED)
        running = False
    elif monster_state == "dying" and monster_frame_index == len(monster_die_frames) - 1:
        show_end_screen("You Win! Virus Eliminated!", GREEN)
        running = False

pygame.quit()
sys.exit()
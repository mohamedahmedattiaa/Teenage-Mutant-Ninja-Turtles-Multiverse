import pygame
from sprits import Spritesheet


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_image, attack_image, leg_attack_image, ult_image, shield_image):
        super().__init__()
        self.al = []  # Walk frames
        self.attack_frames = []  # Light attack frames
        self.leg_attack_frames = []  # Leg attack frames
        self.ult_frames = []  # Ult frames
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 150
        self.turtle_x = x
        self.turtle_y = y
        self.speed = 0.5  # Normal speed
        self.facing_right = True

        # طيران - متغيرات وخصائص الطيران
        self.is_flying = False
        self.fly_speed = 0.4  # سرعة الطيران الأساسية
        self.max_fly_speed = 0.8  # السرعة القصوى للطيران
        self.min_fly_speed = 0.2  # السرعة الدنيا للطيران
        self.fly_acceleration = 0.01  # تسارع الطيران
        self.current_fly_speed = self.fly_speed  # السرعة الحالية للطيران
        self.gravity = 0.015  # قوة الجاذبية منخفضة جداً كأننا في الفضاء
        self.vertical_velocity = 0  # السرعة الرأسية الحالية
        self.max_altitude = 50  # أقصى ارتفاع للطيران عن سطح الأرض
        self.ground_level = 720 - 92 * 2  # مستوى الأرض (ارتفاع الشاشة - ارتفاع الشخصية)

        # قفز - متغيرات وخصائص القفز
        self.is_jumping = False
        self.jump_count = 0
        self.jump_cooldown = 500  # الوقت بين القفزات (ملي ثانية)
        self.last_jump_time = 0
        self.jump_power = 1.8  # قوة القفزة منخفضة للتأثير الفضائي

        # Load sprite sheets
        sprite_sheet = Spritesheet(sprite_image)
        attack_sheet = Spritesheet(attack_image)
        leg_attack_sheet = Spritesheet(leg_attack_image)
        ult_sheet = Spritesheet(ult_image)
        shield_sheet = Spritesheet(shield_image)

        # Load walking frames (5 frames)
        for i in range(3):
            self.al.append(sprite_sheet.get_image(i, 70, 92, 2, (0, 0, 0, 0)))

        # Load light attack frames (3 frames)
        for i in range(3):
            self.attack_frames.append(attack_sheet.get_image(i, 90, 121, 2, (0, 0, 0)))

        # Load leg attack frames (4 frames)
        for i in range(3):
            self.leg_attack_frames.append(leg_attack_sheet.get_image(i, 89, 123, 2, (0, 0, 0)))

        # Load ult frames (4 frames)
        for i in range(4):
            self.ult_frames.append(ult_sheet.get_image(i, 80, 114, 2, (0, 0, 0)))

        # Load shield image (only one frame, scaled by 2)
        self.shield_image = shield_sheet.get_image(0, 68, 87, 2, (0, 0, 0))

        self.image = self.al[self.frame]
        self.frame_width = self.image.get_width()
        self.frame_height = self.image.get_height()

        self.is_attacking = False
        self.is_leg_attacking = False
        self.is_ulting = False
        self.is_shielding = False

    def update(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        moving = False
        attacking = False
        leg_attacking = False
        ulting = False
        shielding = False

        # تحديث متغيرات الطيران والقفز
        current_time = pygame.time.get_ticks()

        # التحكم في الدرع
        if mouse_buttons[2]:  # Right-click for shield
            shielding = True
            move_speed = 0.2  # Slower while shielding
        else:
            move_speed = self.speed
            shielding = False

        # زر الطيران - الفراغ Space
        if keys[pygame.K_SPACE]:
            self.is_flying = True
            # تسارع تدريجي عند الطيران
            if self.current_fly_speed < self.max_fly_speed:
                self.current_fly_speed += self.fly_acceleration
        else:
            self.is_flying = False
            # تباطؤ تدريجي عند التوقف عن الطيران
            if self.current_fly_speed > self.min_fly_speed:
                self.current_fly_speed -= self.fly_acceleration
            else:
                self.current_fly_speed = self.fly_speed

        # التحكم في الحركة الأفقية
        if keys[pygame.K_d]:  # Right
            self.turtle_x += move_speed
            self.facing_right = True
            moving = True
            if self.turtle_x + self.frame_width > 1280:
                self.turtle_x = 1280 - self.frame_width

        if keys[pygame.K_a]:  # Left
            self.turtle_x -= move_speed
            self.facing_right = False
            moving = True
            if self.turtle_x < 0:
                self.turtle_x = 0

        # التحكم في الحركة الرأسية
        if self.is_flying:
            # طيران لأعلى
            if keys[pygame.K_w]:
                self.vertical_velocity = -self.current_fly_speed
                moving = True
            # طيران لأسفل
            elif keys[pygame.K_s]:
                self.vertical_velocity = self.current_fly_speed
                moving = True
            else:
                # تعويم في الهواء عند الطيران بدون ضغط أي زر
                # تأثير تعويم خفيف كأننا في الفضاء
                self.vertical_velocity = self.vertical_velocity * 0.98  # تقليل السرعة تدريجياً للتعويم
        else:
            # تطبيق الجاذبية الخفيفة جداً (فضاء)
            self.vertical_velocity += self.gravity

            # القفز البطيء "الفضائي"
            if keys[pygame.K_w] and not self.is_jumping and current_time - self.last_jump_time > self.jump_cooldown:
                self.is_jumping = True
                self.vertical_velocity = -self.jump_power  # قوة قفز منخفضة
                self.last_jump_time = current_time
                moving = True

            # إضافة تأثير بطيء للحركة في الهواء
            if self.is_jumping or self.turtle_y < self.ground_level:
                # تقليل سرعة الحركة الأفقية في الهواء لتأثير الفضاء
                if keys[pygame.K_a] or keys[pygame.K_d]:
                    move_speed = move_speed * 0.9

        # تطبيق السرعة الرأسية على الموضع (بمعدل أبطأ للتأثير الفضائي)
        self.turtle_y += self.vertical_velocity

        # التحقق من الوصول إلى الأرض
        if self.turtle_y > self.ground_level:
            self.turtle_y = self.ground_level
            self.is_jumping = False
            # يرتد قليلاً عند لمس الأرض (تأثير الجاذبية المنخفضة)
            if abs(self.vertical_velocity) > 0.5:
                self.vertical_velocity = -self.vertical_velocity * 0.3  # ارتداد بنسبة 30%
            else:
                self.vertical_velocity = 0

        # التحقق من الحدود العلوية للشاشة
        if self.turtle_y < 0:
            self.turtle_y = 0
            self.vertical_velocity = 0

        # التحكم في الهجمات
        # Light attack
        if mouse_buttons[0] and not keys[pygame.K_LSHIFT]:
            attacking = True

        # Leg attack (Shift + Left click)
        if keys[pygame.K_LSHIFT] and mouse_buttons[0]:
            leg_attacking = True

        # Ult (press E)
        if keys[pygame.K_e]:
            ulting = True

        self.is_attacking = attacking
        self.is_leg_attacking = leg_attacking
        self.is_ulting = ulting
        self.is_shielding = shielding

        # Animation logic
        current_time = pygame.time.get_ticks()

        if self.is_shielding:
            self.image = self.shield_image  # Just show shield image (static)
        elif self.is_ulting:
            if current_time - self.last_update >= self.animation_cooldown:
                self.frame += 1
                self.last_update = current_time
                if self.frame >= len(self.ult_frames):
                    self.frame = 0
            self.image = self.ult_frames[self.frame]
        elif self.is_leg_attacking:
            if current_time - self.last_update >= self.animation_cooldown:
                self.frame += 1
                self.last_update = current_time
                if self.frame >= len(self.leg_attack_frames):
                    self.frame = 0
            self.image = self.leg_attack_frames[self.frame]
        elif self.is_attacking:
            if current_time - self.last_update >= self.animation_cooldown:
                self.frame += 1
                self.last_update = current_time
                if self.frame >= len(self.attack_frames):
                    self.frame = 0
            self.image = self.attack_frames[self.frame]
        elif moving or self.is_flying or self.is_jumping:
            if current_time - self.last_update >= self.animation_cooldown:
                self.frame += 1
                self.last_update = current_time
                if self.frame >= len(self.al):
                    self.frame = 0
            self.image = self.al[self.frame]
        else:
            self.frame = 0
            self.image = self.al[self.frame]

    def draw(self, surface):
        flipped_image = pygame.transform.flip(self.image, not self.facing_right, False)
        surface.blit(flipped_image, (self.turtle_x, self.turtle_y))
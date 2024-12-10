import arcade
import time
from soundlists import sound_list

SPRITE_SCALING = 0.4
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING)
SPRITE_SCALING_PROJECTILE = 0.2
PROJECTILE_SPEED = 4

MOVEMENT_SPEED = 3
ENEMY_SPEED = 0.75


class Enemy(arcade.Sprite):
    def __init__(self, image, scaling, speed):
        super().__init__(image, scaling)
        self.speed = ENEMY_SPEED
        self.last_atk_time = 0
        self.atk_cooldown = 1.0
        self.health = 30
        self.sound_list = sound_list

    def take_damage(self, amount):
        self.health -= amount
        arcade.play_sound(self.sound_list[3])
        if self.health <= 0:
            arcade.play_sound(self.sound_list[2])
            self.kill()

    def chasing(self, player_sprite):
        x_diff = player_sprite.center_x - self.center_x
        y_diff = player_sprite.center_y - self.center_y
        distance = (x_diff**2 + y_diff**2) ** 0.5

        if distance < 100:
            if distance > 5:
                x_step = (x_diff / distance) * self.speed
                y_step = (y_diff / distance) * self.speed
                self.center_x += x_step
                self.center_y += y_step

    def canIAtk(self):
        curtime = time.time()
        if curtime - self.last_atk_time >= self.atk_cooldown:
            self.last_atk_time = curtime
            return True
        return False

class Guard(Enemy):
    def __init__(self, image, scaling, speed):
        super().__init__(image, scaling, speed)

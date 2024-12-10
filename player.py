import arcade
import time

from soundlists import sound_list

SPRITE_SCALING = 0.4
MOVEMENT_SPEED = 3

class Player(arcade.Sprite):
    def __init__(self, image_path, scaling):
        super().__init__(image_path, scaling)
        self.health = 100
        self.max_health = 100
        self.attack_cooldown = 0.50
        self.last_attack_time = 0
        self.projectile_cooldown = 0.25
        self.last_projectile_time = 0
        self.base_movement_speed = MOVEMENT_SPEED
        self.current_movement_speed = MOVEMENT_SPEED
        self.sound_list = sound_list
  

    def can_attack(self):
        cur_time = time.time()
        if cur_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = cur_time
            return True
        return False
    
    def can_shoot(self):
        cur_time = time.time()
        if cur_time - self.last_projectile_time >= self.projectile_cooldown:
            self.last_projectile_time = cur_time
            return True
        return False

    def take_damage(self, amount):
        arcade.play_sound(self.sound_list[1])
        self.health = max(0, self.health - amount)

    def heal(self, amount):
        arcade.play_sound(self.sound_list[4])
        self.health = min(self.max_health, self.health + amount)

    def reset_health(self):
        self.health = self.max_health

    def move(self, key, modifiers):
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
         
    

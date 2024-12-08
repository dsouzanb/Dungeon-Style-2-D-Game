import arcade
import os
import math
import random
import time
import json

SPRITE_SCALING = 0.4
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING)

SPRITE_SCALING_PROJECTILE = 0.2
PROJECTILE_SPEED = 4

SCREEN_WIDTH = SPRITE_SIZE * 20
SCREEN_HEIGHT = SPRITE_SIZE * 14
SCREEN_TITLE = "Dungeon Game"

MOVEMENT_SPEED = 3
ENEMY_SPEED = 0.75


class Enemy(arcade.Sprite):
    def __init__(self, image, scaling, speed):
        super().__init__(image, scaling)
        self.speed = ENEMY_SPEED
        self.last_atk_time = 0
        self.atk_cooldown = 1.0
        self.health = 30

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
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


class healingItem(arcade.Sprite):
    def __init__(self, image, scaling, heal_amount):
        super().__init__(image, scaling)
        self.heal_amount = heal_amount


class Lava(arcade.Sprite):
    def __init__(self, image, scaling, damage_per_second):
        super().__init__(image, scaling)
        self.damage_per_second = damage_per_second


class Water(arcade.Sprite):
    def __init__(self, image, scaling, speed_modifier):
        super().__init__(image, scaling)
        self.speed_modifier = speed_modifier

    def apply_effect(self, player):
        player.current_movement_speed *= self.speed_modifier

class Guard(Enemy):
    def __init__(self, image, scaling, speed):
        super().__init__(image, scaling, speed)

class Room:
    def __init__(self):
        self.wall_list = arcade.SpriteList()
        self.background = None
        self.enemy_list = arcade.SpriteList()
        self.projectile_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()
        self.lava_list = arcade.SpriteList()
        self.water_list = arcade.SpriteList()
        self.dragon_spawned = False # use to track if dragon spawned

        self.boss_start_x = None
        self.boss_start_y = None

def load_rooms_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    rooms = []
    for room_index, room_data in enumerate(data["rooms"]):
        room = Room()
        for row_index, row in enumerate(room_data["layout"]):
            for col_index, col in enumerate(row):
                x = (col_index * SPRITE_SIZE) + 20
                y = ((len(room_data["layout"]) - row_index - 1) * SPRITE_SIZE) + 20
                if col == "W":
                    wall = arcade.Sprite(":resources:images/tiles/stone.png", SPRITE_SCALING)
                    wall.center_x = x
                    wall.center_y = y
                    room.wall_list.append(wall)
                elif col == "P":
                    room.player_start_x = x
                    room.player_start_y = y
                elif col == "E":
                    # Differentiate between enemy types based on room
                    if room_index == 1:  # Cave 2
                        goblin = Enemy("images/goblin.png", SPRITE_SCALING * 0.15, speed=1.2)
                        goblin.center_x = x
                        goblin.center_y = y
                        goblin.health = 40  
                        room.enemy_list.append(goblin)
                    elif room_index == 2: # Cave 3
                        guard = Guard("images/guard.png", SPRITE_SCALING * 0.3, speed=2)
                        guard.center_x = x
                        guard.center_y = y
                        guard.health = 50  
                        room.enemy_list.append(guard)
                    else:  # Other caves use skeletons
                        enemy = Enemy("images/skeleton_warrior.png", (SPRITE_SCALING *0.4), speed=2)
                        enemy.center_x = x
                        enemy.center_y = y
                        room.enemy_list.append(enemy)
                elif col == "L":
                    lava = Lava(":resources:images/tiles/lava.png", SPRITE_SCALING, damage_per_second=5)
                    lava.center_x = x
                    lava.center_y = y
                    room.lava_list.append(lava)
                elif col == "A":
                    water = Water(":resources:images/tiles/water.png", SPRITE_SCALING, speed_modifier=0.5)
                    water.center_x = x
                    water.center_y = y
                    room.water_list.append(water)
                elif col == "D":
                    room.door_x = x
                    room.door_y = y
                elif col == "B":
                    room.boss_start_x = x
                    room.boss_start_y = y
                elif col == "H":
                    healing_item = healingItem("images/healing_plant.png", SPRITE_SCALING  / 4, heal_amount =20)
                    healing_item.center_x = x
                    healing_item.center_y = y
                    room.item_list.append(healing_item)

        room.background = arcade.load_texture(room_data["background"])
        rooms.append(room)
    return rooms


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.player_attack_cooldown = 0.50
        self.last_attack_time = 0
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        self.current_room = 0
        self.rooms = None
        self.player_sprite = None
        self.player_list = None
        self.physics_engine = None
        self.player_health = 100
        self.max_health = 100
        self.is_game_over = False
        self.base_movement_speed = MOVEMENT_SPEED
        self.current_movement_speed = MOVEMENT_SPEED

    def player_attack(self):
        cur_time = time.time()
        if cur_time - self.last_attack_time >= self.player_attack_cooldown:
            self.last_attack_time = cur_time
            return True
        return False

    def perform_attack(self):
        if self.rooms[self.current_room].enemy_list:
            for enemy in self.rooms[self.current_room].enemy_list:
                if arcade.check_for_collision(self.player_sprite, enemy):
                    enemy.take_damage(10)
        else:
            print("No enemies in the room.")

    def setup(self):
        self.player_sprite = arcade.Sprite("images/knight4.png", SPRITE_SCALING)
        self.player_sprite.center_x = 100
        self.player_sprite.center_y = 100
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)
        self.rooms = load_rooms_from_json("levels.json")
        self.current_room = 0
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.rooms[self.current_room].wall_list)

    def change_room(self, next_room):
        if 0 <= next_room < len(self.rooms):
            self.current_room = next_room
            room = self.rooms[self.current_room]
            self.player_sprite.center_x = room.player_start_x
            self.player_sprite.center_y = room.player_start_y
            self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, room.wall_list)

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.rooms[self.current_room].background)
        self.rooms[self.current_room].wall_list.draw()
        self.rooms[self.current_room].lava_list.draw()
        self.rooms[self.current_room].water_list.draw()
        self.rooms[self.current_room].enemy_list.draw()
        self.rooms[self.current_room].projectile_list.draw()
        self.player_list.draw()
        self.rooms[self.current_room].item_list.draw()

        bar_width = 200
        bar_height = 20
        bar_x = 40
        bar_y = 10
        health_percentage = self.player_health / self.max_health
        arcade.draw_xywh_rectangle_filled(bar_x, bar_y, bar_width, bar_height, arcade.color.MAROON)
        arcade.draw_xywh_rectangle_filled(bar_x, bar_y, bar_width * health_percentage, bar_height, arcade.color.DARK_GREEN)
        arcade.draw_xywh_rectangle_outline(bar_x, bar_y, bar_width, bar_height, arcade.color.BLACK, border_width=2)
        if self.is_game_over:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.RED, 50, anchor_x="center")
            arcade.draw_text("Press 'R' to restart:", SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4, arcade.color.WHITE, 30, anchor_x="center")
            return

        for enemy in self.rooms[self.current_room].enemy_list:
            bar_width = 40
            bar_height = 5
            bar_x = enemy.center_x - bar_width // 2
            bar_y = enemy.center_y + 20
            health_percentage = max(enemy.health / 30, 0)
            arcade.draw_xywh_rectangle_filled(bar_x, bar_y, bar_width, bar_height, arcade.color.DARK_RED)
            arcade.draw_xywh_rectangle_filled(bar_x, bar_y, bar_width * health_percentage, bar_height, arcade.color.GREEN)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE and self.player_attack():
            self.perform_attack()
        if key == arcade.key.UP:
            self.player_sprite.change_y = self.current_movement_speed
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -self.current_movement_speed
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -self.current_movement_speed
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = self.current_movement_speed
        if self.is_game_over and key == arcade.key.R:
            self.setup()
            self.is_game_over = False
            self.player_health = 100

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when the mouse button is clicked """
        # Create a projectile
        projectile = arcade.Sprite(":resources:images/tiles/rock.png", SPRITE_SCALING_PROJECTILE)

        # Position the projectile at the player's current location
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        projectile.center_x = start_x
        projectile.center_y = start_y

        # Calculating the angle in radians between the start points
        # and end points. This is the angle the projectile will travel.
        x_diff = x - start_x
        y_diff = y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Angle the projectile sprite so it doesn't look like it's flying.
        projectile.angle = math.degrees(angle)
        print(f"Projectile angle: {projectile.angle:.2f}")

        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the projectile travels.
        projectile.change_x = math.cos(angle) * PROJECTILE_SPEED
        projectile.change_y = math.sin(angle) * PROJECTILE_SPEED

        # Add the projectile to the appropriate lists
        self.rooms[self.current_room].projectile_list.append(projectile)

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.current_movement_speed = self.base_movement_speed
        for lava in self.rooms[self.current_room].lava_list:
            if arcade.check_for_collision(self.player_sprite, lava):
                self.player_health -= lava.damage_per_second * delta_time
                if self.player_health <= 0:
                    self.is_game_over = True
                    return
        for water in self.rooms[self.current_room].water_list:
            if arcade.check_for_collision(self.player_sprite, water):
                water.apply_effect(self)

         # Check for room completion and spawn dragon in Cave 3
        current_room = self.rooms[self.current_room]
        if self.current_room == 2 and not current_room.dragon_spawned and len(current_room.enemy_list) == 0:  # All enemies defeated
                self.spawn_dragon(current_room)

        for enemy in self.rooms[self.current_room].enemy_list:
            enemy.chasing(self.player_sprite)
            if arcade.check_for_collision(self.player_sprite, enemy) and enemy.canIAtk():
                self.player_health -= 10
        # Check for Cave 3 and spawn dragon
        if self.current_room == 2 and not self.rooms[self.current_room].dragon_spawned:
            guards = [enemy for enemy in self.rooms[self.current_room].enemy_list if isinstance(enemy, Guard)]
            if len(guards) == 0:
                # All guards defeated, spawn the dragon
                dragon = Enemy("images/boss.png", SPRITE_SCALING * 0.35, speed=1.0)
                dragon.center_x = SCREEN_WIDTH // 2
                dragon.center_y = SCREEN_HEIGHT // 2
                dragon.health = 100  # Dragon has higher health
                self.rooms[self.current_room].enemy_list.append(dragon)
                self.rooms[self.current_room].dragon_spawned = True

        for item in self.rooms[self.current_room].item_list:
            if arcade.check_for_collision(self.player_sprite, item):
                self.player_health = min(self.max_health, self.player_health + item.heal_amount)
                item.kill()
        if self.is_game_over:
            return
        if self.player_health <= 0:
            self.is_game_over = True
        if self.player_sprite.center_x > SCREEN_WIDTH and self.current_room == 0:
            self.current_room = 1
            self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.rooms[self.current_room].wall_list)
            self.player_sprite.center_x = 0
        elif self.player_sprite.center_x < 0 and self.current_room == 1:
            self.current_room = 0
            self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.rooms[self.current_room].wall_list)
            self.player_sprite.center_x = SCREEN_WIDTH
        elif self.player_sprite.center_x > SCREEN_WIDTH and self.current_room == 1:
            self.current_room = 2
            self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.rooms[self.current_room].wall_list)
            self.player_sprite.center_x = 0
        elif self.player_sprite.center_x < 0 and self.current_room == 2:
            self.current_room = 1
            self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.rooms[self.current_room].wall_list)
            self.player_sprite.center_x = SCREEN_WIDTH
        
        # Call update on all sprites
        projectiles = self.rooms[self.current_room].projectile_list
        enemies = self.rooms[self.current_room].enemy_list

        projectiles.update()

        # Loop thru each projectile
        for projectile in projectiles:
            # Check this projectile to see if it hit an enemy
            hit_list = arcade.check_for_collision_with_list(projectile, enemies)

            # If it did, get rid of projectile
            if hit_list:
                projectile.remove_from_sprite_lists()
                for enemy in hit_list:
                    enemy.take_damage(10)

            # If the projectile flies off screen, remove it
            if (projectile.bottom > SCREEN_HEIGHT or projectile.top < 0
            or projectile.right < 0 or projectile.left > SCREEN_WIDTH):
                projectile.remove_from_sprite_lists()

    def spawn_dragon(self, room):
        dragon = Enemy("images/boss.png", SPRITE_SCALING * 0.5, speed=1.5)
        dragon.center_x = room.boss_start_x or SCREEN_WIDTH //2
        dragon.center_y = room.boss_start_y or SCREEN_HEIGHT //2
        dragon.health = 150  # Set a higher health for the dragon
        room.enemy_list.append(dragon)
        room.dragon_spawned = True
        print("Dragon has spawned!")

def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
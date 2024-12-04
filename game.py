import arcade
import os
import math
import random
import time
import json

SPRITE_SCALING = 0.4
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING)

SPRITE_SCALING_PROJECTILE = 0.3
PROJECTILE_SPEED = 5


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

class Room:
    def __init__(self):
        self.wall_list = arcade.SpriteList()
        self.background = None
        self.enemy_list = arcade.SpriteList()
        self.projectile_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()


def load_rooms_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    rooms = []
    for room_data in data["rooms"]:
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
                    enemy = Enemy(":resources:images/enemies/slimePurple.png", SPRITE_SCALING, speed=2)
                    enemy.center_x = x
                    enemy.center_y = y
                    room.enemy_list.append(enemy)
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
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", SPRITE_SCALING)
        self.player_sprite.center_x = 100
        self.player_sprite.center_y = 100
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        # Load rooms from JSON
        self.rooms = load_rooms_from_json("levels.json")
        self.current_room = 0
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.rooms[self.current_room].wall_list)

    def on_draw(self):
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.rooms[self.current_room].background)
        self.rooms[self.current_room].wall_list.draw()
        # Draw all the monsters in this room
        self.rooms[self.current_room].enemy_list.draw()
        # Draw projectiles for the room
        self.rooms[self.current_room].projectile_list.draw()

        #player stuff-health etc...
        self.player_list.draw()
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
            arcade.draw_text("Press 'r' to restart:", SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4, arcade.color.WHITE, 30, anchor_x="center")
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
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED
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
        for enemy in self.rooms[self.current_room].enemy_list:
            enemy.chasing(self.player_sprite)
            if arcade.check_for_collision(self.player_sprite, enemy) and enemy.canIAtk():
                self.player_health -= 10
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



def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()


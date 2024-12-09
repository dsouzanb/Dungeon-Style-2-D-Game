import arcade
import os
import math
import time

from player import Player
from rooms import load_rooms_from_json
from enemies import Enemy, Guard

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

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        self.current_room = 0
        self.rooms = None
        self.player = None
        self.player_list = None
        self.physics_engine = None
        self.is_game_over = False

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False


    def setup(self):
        self.player = Player("images/knight4.png", SPRITE_SCALING)
        self.player.center_x = 100
        self.player.center_y = 100
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.rooms = load_rooms_from_json("levels.json")
        self.current_room = 0
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.rooms[self.current_room].wall_list)

    def change_room(self, next_room):
        if 0 <= next_room < len(self.rooms):
            self.current_room = next_room
            room = self.rooms[self.current_room]
            self.player.center_x = room.player_start_x
            self.player.center_y = room.player_start_y
            self.physics_engine = arcade.PhysicsEngineSimple(self.player, room.wall_list)

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
        health_percentage = self.player.health / self.player.max_health
        arcade.draw_xywh_rectangle_filled(bar_x, bar_y, bar_width, bar_height, arcade.color.MAROON)
        arcade.draw_xywh_rectangle_filled(bar_x, bar_y, bar_width * health_percentage, bar_height, arcade.color.DARK_GREEN)
        arcade.draw_xywh_rectangle_outline(bar_x, bar_y, bar_width, bar_height, arcade.color.BLACK, border_width=2)
        if self.is_game_over:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.RED, 50, anchor_x="center")
            arcade.draw_text("Press 'R' to restart:", 520, SCREEN_HEIGHT / 4, arcade.color.WHITE, 30, anchor_x="center")
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
        if key == arcade.key.SPACE and self.player.can_attack():
            self.perform_attack()
        
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

        if self.is_game_over and key == arcade.key.R:
            self.setup()
            self.is_game_over = False
            # self.player_health = 100
            self.player.reset_health()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def perform_attack(self):
        # if self.rooms[self.current_room].enemy_list:
        for enemy in self.rooms[self.current_room].enemy_list:
            if arcade.check_for_collision(self.player, enemy):
                enemy.take_damage(10)

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when the mouse button is clicked """
        # Create a projectile
        projectile = arcade.Sprite(":resources:images/tiles/rock.png", SPRITE_SCALING_PROJECTILE)

        # Position the projectile at the player's current location
        start_x = self.player.center_x
        start_y = self.player.center_y
        projectile.center_x = start_x
        projectile.center_y = start_y

        # Calculating the angle in radians between the start points
        # and end points. This is the angle the projectile will travel.
        x_diff = x - start_x
        y_diff = y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Angle the projectile sprite so it doesn't look like it's flying.
        projectile.angle = math.degrees(angle)
       

        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the projectile travels.
        projectile.change_x = math.cos(angle) * PROJECTILE_SPEED
        projectile.change_y = math.sin(angle) * PROJECTILE_SPEED

        # Add the projectile to the appropriate lists
        self.rooms[self.current_room].projectile_list.append(projectile)
    
        
    def on_update(self, delta_time):
        self.physics_engine.update()
        self.player.current_movement_speed = self.player.base_movement_speed

        if self.is_game_over:
            return
        for lava in self.rooms[self.current_room].lava_list:
            if arcade.check_for_collision(self.player, lava):
                self.player.take_damage(lava.damage_per_second * delta_time)
                #self.player_health -= lava.damage_per_second * delta_time
                if self.player.health <= 0:
                    self.is_game_over = True
                    return
        for water in self.rooms[self.current_room].water_list:
            if arcade.check_for_collision(self.player, water):
                water.apply_effect(self.player)

        # update move character from key presses
        current_speed = self.player.current_movement_speed
        self.player.change_y, self.player.change_x = 0, 0
        if self.up_pressed and not self.down_pressed:
            self.player.change_y = current_speed
        elif self.down_pressed and not self.up_pressed:
            self.player.change_y = -current_speed
        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -current_speed
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = current_speed

         # Check for room completion and spawn dragon in Cave 3
        current_room = self.rooms[self.current_room]
        if self.current_room == 2 and not current_room.dragon_spawned and len(current_room.enemy_list) == 0:  # All enemies defeated
                self.spawn_dragon(current_room)
        
        # Update Projectiles
        projectiles = self.rooms[self.current_room].projectile_list
        walls = self.rooms[self.current_room].wall_list
        enemies = self.rooms[self.current_room].enemy_list
        projectiles.update()
        for projectile in projectiles:
            # Check if the projectile hit an enemy
            hit_list = arcade.check_for_collision_with_list(projectile, enemies)
            if hit_list:
                projectile.remove_from_sprite_lists()
                for enemy in hit_list:
                    enemy.take_damage(10)
            # Check if the projectile hit a wall
            if arcade.check_for_collision_with_list(projectile, walls):
               projectile.remove_from_sprite_lists()
            # Remove projectile if it flies off screen
            if (projectile.bottom > SCREEN_HEIGHT or projectile.top < 0 or
                    projectile.right < 0 or projectile.left > SCREEN_WIDTH):
                projectile.remove_from_sprite_lists()


            # Store enemy physics engines
        if not hasattr(self, "enemy_physics_engines"):
            self.enemy_physics_engines = {}

        for enemy in self.rooms[self.current_room].enemy_list:
            # If the enemy doesn't already have a physics engine, create one
            if enemy not in self.enemy_physics_engines:
                self.enemy_physics_engines[enemy] = arcade.PhysicsEngineSimple(enemy, self.rooms[self.current_room].wall_list)

            # Enemy chasing logic
            enemy.chasing(self.player)

            # Update the physics engine for the enemy
            self.enemy_physics_engines[enemy].update()

            # Check if the enemy collides with the player
            if arcade.check_for_collision(self.player, enemy) and enemy.canIAtk():
                self.player.health -= 10

        # Clean up physics engines for enemies no longer in the room
        self.enemy_physics_engines = {
            enemy: engine
            for enemy, engine in self.enemy_physics_engines.items()
            if enemy in self.rooms[self.current_room].enemy_list
        }


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
            if arcade.check_for_collision(self.player, item):
                self.player.health = min(self.player.max_health, self.player.health + item.heal_amount)
                item.kill()
        if self.is_game_over:
            return
        if self.player.health <= 0:
            self.is_game_over = True
        if self.player.center_x > SCREEN_WIDTH and self.current_room == 0:
            self.current_room = 1
            self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.rooms[self.current_room].wall_list)
            self.player.center_x = 0
        elif self.player.center_x < 0 and self.current_room == 1:
            self.current_room = 0
            self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.rooms[self.current_room].wall_list)
            self.player.center_x = SCREEN_WIDTH
        elif self.player.center_x > SCREEN_WIDTH and self.current_room == 1:
            self.current_room = 2
            self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.rooms[self.current_room].wall_list)
            self.player.center_x = 0
        elif self.player.center_x < 0 and self.current_room == 2:
            self.current_room = 1
            self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.rooms[self.current_room].wall_list)
            self.player.center_x = SCREEN_WIDTH
        
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
            or  projectile.right < 0 or projectile.left > SCREEN_WIDTH):
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
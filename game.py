import arcade
import os
import math
import random
import time

SPRITE_SCALING = 0.3
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING)


SCREEN_WIDTH = SPRITE_SIZE * 20
SCREEN_HEIGHT = SPRITE_SIZE * 14
SCREEN_TITLE = "Dungeon Game"

MOVEMENT_SPEED = 2
ENEMY_SPEED = 0.50

class Enemy(arcade.Sprite):
    def __init__(self, image, scaling, speed):
        super().__init__(image, scaling)
        self.speed = ENEMY_SPEED
        self.last_atk_time = 0
        self.atk_cooldown = 1.0

    def chasing(self, player_sprite):
        #distance calcs
        x_diff = player_sprite.center_x - self.center_x
        y_diff = player_sprite.center_y - self.center_y

        
        distance = (x_diff**2 + y_diff**2) ** 0.5

        #adjustment for engagement distance
        if distance < 100:  
            if distance > 5:  
                # Normalize the vector and scale by speed
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



class Room:
    def __init__(self):
        # You may want many lists. Lists for coins, monsters, etc.
        self.wall_list = None
        self.background = None
        self.enemy_list = None


def setup_room_1():
    level_data = [
        "WWWWWWWWWWWWWWWWWWWW",
        "W..................W",
        "W.......E..........W",
        "W.........W........W",
        "W..................W",
        "W....W.............W",
        "W.......E...WWWW...W",
        "W...........W......W",
        "WWWWWW......W.......",
        "W...........W.......",
        "W...........WWWWWWWW",
        "W.P..W......W..E..WW",
        "W....W............WW",
        "WWWWWWWWWWWWWWWWWWWW",

    ]
    room = Room()

    """ Set up the game and initialize the variables. """
    # Sprite lists
    room.wall_list = arcade.SpriteList()
    room.enemy_list = arcade.SpriteList()

    for row_index, row in enumerate(level_data):
        for col_index, col in enumerate(row):
           
            x = (col_index * SPRITE_SIZE ) + 20
            y = ((len(level_data) - row_index - 1) * SPRITE_SIZE) + 20

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
    


    # Load the background image for this level.
    room.background = arcade.load_texture("images/watercave.png")

    return room


def setup_room_2():
  
    level_data = [
        "WWWWWWWWWWWWWWWWWWWW",
        "W...................",
        "W.......E...........",
        "W.........W........W",
        "W..................W",
        "W....W.............W",
        "W.......E...WWWW...W",
        "W...........W......W",
        ".WWWWW......W......W",
        "............W......W",
        "W...........WWWWWWWW",
        "W....W......W..E..WW",
        "W....W............WW",
        "WWWWWWWWWWWWWWWWWWWW",

    ]
    room = Room()

    """ Set up the game and initialize the variables. """
    # Sprite lists
    room.wall_list = arcade.SpriteList()
    room.enemy_list = arcade.SpriteList()

    for row_index, row in enumerate(level_data):
        for col_index, col in enumerate(row):
           
            x = (col_index * SPRITE_SIZE ) + 20
            y = ((len(level_data) - row_index - 1) * SPRITE_SIZE) + 20

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
    


    # Load the background image for this level.
    room.background = arcade.load_texture("images/watercave.png")

    return room

def setup_room_3():
 
    level_data = [
        "WWWWWWWWWWWWWWWWWWWW",
        "..........W........W",
        ".........W.W.....E.W",
        "W.......W...W....E.W",
        "W......W.....W...E.W",
        "W......W..W..W...E.W",
        "W......W..W..W...E.W",
        "W.......W...W....E.W",
        "W......W..W..W...E.W",
        "W......W..W..W.....W",
        "W......W..W..W.....W",
        "W.......W...W......W",
        "W....,...W.W.......W",
        "WWWWWWWWWWWWWWWWWWWW",

    ]
    room = Room()

    """ Set up the game and initialize the variables. """
    # Sprite lists
    room.wall_list = arcade.SpriteList()
    room.enemy_list = arcade.SpriteList()

    for row_index, row in enumerate(level_data):
        for col_index, col in enumerate(row):
           
            x = (col_index * SPRITE_SIZE ) + 20
            y = ((len(level_data) - row_index - 1) * SPRITE_SIZE) + 20

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
    


    # Load the background image for this level.
    room.background = arcade.load_texture("images/watercave.png")

    return room




class MyGame(arcade.Window):


    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Sprite lists
        self.current_room = 0

        # Set up the player
        self.rooms = None
        self.player_sprite = None
        self.player_list = None
        self.physics_engine = None

        #player health
        self.player_health = 100
        self.max_health = 100

        self.is_game_over = False

       



    def setup(self):
        """ Set up the game and initialize the variables. """
        # Set up the player
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/"
                                           "femalePerson_idle.png", SPRITE_SCALING)
        self.player_sprite.center_x = 100
        self.player_sprite.center_y = 100
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        # Our list of rooms
        self.rooms = []

        # Create the rooms. Extend the pattern for each room.
        room = setup_room_1()
        self.rooms.append(room)

        room = setup_room_2()
        self.rooms.append(room)
        
        room = setup_room_3()
        self.rooms.append(room)

        # Our starting room number
        self.current_room = 0

        # Create a physics engine for this room
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,
                                                         self.rooms[self.current_room].wall_list)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()



        # Draw the background texture
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.rooms[self.current_room].background)

        # Draw all the walls in this room
        self.rooms[self.current_room].wall_list.draw()
        
        #monster draw
        self.rooms[self.current_room].enemy_list.draw()
        

        #player stuff-health etc...
        self.player_list.draw()
        bar_width = 200  
        bar_height = 20  
        bar_x = 40 
        bar_y = 10  
        health_percentage = self.player_health / self.max_health

        #health bar design
        arcade.draw_xywh_rectangle_filled(bar_x, bar_y, bar_width, bar_height, arcade.color.MAROON)
        arcade.draw_xywh_rectangle_filled(bar_x, bar_y, bar_width * health_percentage, bar_height, arcade.color.DARK_GREEN)
        arcade.draw_xywh_rectangle_outline(bar_x, bar_y, bar_width, bar_height, arcade.color.BLACK, border_width=2)

        if self.is_game_over:
            arcade.draw_text(
                "GAME OVER", SCREEN_WIDTH /2, SCREEN_HEIGHT/2,
                arcade.color.RED, 50, anchor_x="center"
            )
            arcade.draw_text("Press 'r' to restart:", SCREEN_WIDTH/4, SCREEN_HEIGHT/4,
                arcade.color.WHITE, 30, anchor_x="center"
                             
            )
            return



    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

        #gameover restart 
        if self.is_game_over and key == arcade.key.R:
            self.setup() 
            self.is_game_over = False
            self.player_health = 100

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()
        
        #for enemies:
        for enemy in self.rooms[self.current_room].enemy_list:
            enemy.chasing(self.player_sprite)
            if arcade.check_for_collision(self.player_sprite, enemy) and enemy.canIAtk():
                self.player_health -= 10

        

        if self.is_game_over:
            return
        #gameover check
        if self.player_health <= 0:
            self.is_game_over = True
            
        

        # Do some logic here to figure out what room we are in, and if we need to go
        # to a different room.
        if self.player_sprite.center_x > SCREEN_WIDTH and self.current_room == 0:
            self.current_room = 1
            self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,
                                                             self.rooms[self.current_room].wall_list)
            self.player_sprite.center_x = 0
        
        elif self.player_sprite.center_x < 0 and self.current_room == 1:
            self.current_room = 0
            self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,
                                                             self.rooms[self.current_room].wall_list)
            self.player_sprite.center_x = SCREEN_WIDTH

        elif self.player_sprite.center_x > SCREEN_WIDTH and self.current_room == 1:
            self.current_room = 2
            self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,
                                                             self.rooms[self.current_room].wall_list)
            self.player_sprite.center_x = 0
            
        elif self.player_sprite.center_x < 0 and self.current_room == 2:
            self.current_room = 1
            self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,
                                                             self.rooms[self.current_room].wall_list)
            self.player_sprite.center_x = SCREEN_WIDTH





def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()



import arcade
import json

from enemies import Enemy, Guard
from player import Player

SPRITE_SCALING = 0.4
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING)
SPRITE_SCALING_PROJECTILE = 0.2
PROJECTILE_SPEED = 4

MOVEMENT_SPEED = 3
ENEMY_SPEED = 0.75


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

    def apply_effect(self, player: Player):
        player.current_movement_speed = self.speed_modifier * player.base_movement_speed


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
                x = (col_index * SPRITE_SIZE) + 25 
                y = ((len(room_data["layout"]) - row_index - 1) * SPRITE_SIZE) + 25
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


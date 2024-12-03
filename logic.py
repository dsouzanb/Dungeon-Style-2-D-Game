import arcade

SPRITE_SCALING = 0.3
ROOMS = []
MOVEMENT_SPEED = 1  # Movement steps per command


class Room:
    """Holds room information."""
    def __init__(self, name, description, walls=None, enemies=None):
        self.name = name
        self.description = description
        self.walls = walls 
        self.enemies = enemies 

    def display(self):
        """Display the room information."""
        print(f"\nYou are in {self.name}.")
        print(self.description)
        if self.enemies:
            for enemy in self.enemies:
                print(f"You encounter a {enemy.name} (HP: {enemy.health}).")
        if self.walls:
            print("There are walls at these locations:")
            for wall in self.walls:
                print(f" - {wall}")


class Player:
    """Tracks player state."""
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.position = [1, 1]  # Starting position
        self.current_room = 0

    def move(self, direction):
        """Move the player."""
        x, y = self.position
        if direction == "UP":
            y += MOVEMENT_SPEED
        elif direction == "DOWN":
            y -= MOVEMENT_SPEED
        elif direction == "LEFT":
            x -= MOVEMENT_SPEED
        elif direction == "RIGHT":
            x += MOVEMENT_SPEED

        self.position = [x, y]
        print(f"{self.name} moves {direction} to {self.position}.")

    def attack(self, enemy):
        """Attack an enemy."""
        damage = 15
        enemy.health -= damage
        print(f"{self.name} attacks {enemy.name} for {damage} damage!")
        if enemy.health <= 0:
            print(f"{enemy.name} is defeated!")


class Goblin:
    def __init__(self):
        self.name = "Goblin"
        self.damage = 10
        self.health = 30


class Skeleton:
    def __init__(self):
        self.name = "Skeleton"
        self.damage = 15
        self.health = 40


class GameWindow(arcade.Window):
    """Main game window."""

    def __init__(self):
        super().__init__(800, 600, "Text Adventure Game")
        arcade.set_background_color(arcade.color.BLACK)
        self.player = Player(name="Hero")
        self.current_room = None
        create_rooms()
        self.update_room()

    def update_room(self):
        """Update the current room."""
        self.current_room = ROOMS[self.player.current_room]
        self.current_room.display()

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()
        arcade.draw_text(
            f"Player Health: {self.player.health}",
            10, 570, arcade.color.WHITE, 14
        )
        arcade.draw_text(
            f"Current Room: {self.current_room.name}",
            10, 550, arcade.color.WHITE, 14
        )
        arcade.draw_text(
            f"Player Position: {self.player.position}",
            10, 530, arcade.color.WHITE, 14
        )

    def on_key_press(self, key, modifiers):
        """Handle keyboard input."""
        if key == arcade.key.UP:
            self.player.move("UP")
        elif key == arcade.key.DOWN:
            self.player.move("DOWN")
        elif key == arcade.key.LEFT:
            self.player.move("LEFT")
        elif key == arcade.key.RIGHT:
            self.player.move("RIGHT")
        elif key == arcade.key.A:
            if self.current_room.enemies:
                self.player.attack(self.current_room.enemies[0])
                # Enemy retaliates if still alive
                if self.current_room.enemies[0].health > 0:
                    enemy = self.current_room.enemies[0]
                    self.player.health -= enemy.damage
                    print(f"{enemy.name} attacks back for {enemy.damage} damage!")
                else:
                    self.current_room.enemies.pop(0)
            else:
                print("No enemies to attack here.")
        elif key == arcade.key.Q:
            print("Exiting the game. Goodbye!")
            arcade.close_window()

        # Room transitions
        if self.player.position[1] > 5 and self.player.current_room == 0:
            print("You move to Room 2.")
            self.player.current_room = 1
            self.player.position = [1, 1]
            self.update_room()
        elif self.player.position[1] < 0 and self.player.current_room == 1:
            print("You move to Room 1.")
            self.player.current_room = 0
            self.player.position = [1, 1]
            self.update_room()

        # Check if the player is defeated
        if self.player.health <= 0:
            print("You have been defeated. Game Over.")
            arcade.close_window()


def create_rooms():
    """Set up rooms."""
    room1 = Room(
        name="Room 1",
        description="A dimly lit room with stone walls. There's an opening to the north.",
        walls=["East wall", "West wall"],
        enemies=[Goblin()]
    )
    room2 = Room(
        name="Room 2",
        description="A narrow hallway with flickering torches. You see a doorway to the south.",
        walls=["North wall", "South wall"],
        enemies=[Skeleton()]
    )
    ROOMS.extend([room1, room2])


if __name__ == "__main__":
    GameWindow()
    arcade.run()

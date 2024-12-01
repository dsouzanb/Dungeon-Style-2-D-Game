import time

SPRITE_SCALING = 0.3
ROOMS = []
MOVEMENT_SPEED = 1  # Movement steps per command


class Room:
    """Holds room information."""
    def __init__(self, name, description, walls=None, enemies=None):
        self.name = name
        self.description = description
        self.walls = walls or []
        self.enemies = enemies or []

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
        self.position = (1, 1)  # Starting position
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
        else:
            print("Invalid direction.")
            return

        self.position = (x, y)
        print(f"{self.name} moves {direction} to {self.position}.")

    def attack(self, enemy):
        """Attack an enemy."""
        damage = 15
        enemy.health -= damage
        print(f"{self.name} attacks {enemy.name} for {damage} damage!")
        if enemy.health <= 0:
            print(f"{enemy.name} is defeated!")


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


def game_loop():
    """Main game loop."""
    player = Player(name="Hero")
    create_rooms()

    while True:
        current_room = ROOMS[player.current_room]
        current_room.display()
        print(f"{player.name}'s health: {player.health}")

        if not current_room.enemies:
            print("No enemies here. Move to another room.")

        # Handle player actions
        action = input("Enter action (MOVE [UP/DOWN/LEFT/RIGHT], ATTACK, or QUIT): ").strip().upper()
        if action.startswith("MOVE"):
            direction = action.split()[1]
            player.move(direction)
        elif action == "ATTACK":
            if current_room.enemies:
                player.attack(current_room.enemies[0])
                # Enemy retaliates if still alive
                if current_room.enemies[0].health > 0:
                    enemy = current_room.enemies[0]
                    player.health -= enemy.damage
                    print(f"{enemy.name} attacks back for {enemy.damage} damage!")
                else:
                    current_room.enemies.pop(0)
            else:
                print("No enemies to attack here.")
        elif action == "QUIT":
            print("Exiting the game. Goodbye!")
            break
        else:
            print("Invalid action.")

        # Process room transitions
        if player.position[1] > 5 and player.current_room == 0:
            print("You move to Room 2.")
            player.current_room = 1
            player.position = (1, 1)
        elif player.position[1] < 0 and player.current_room == 1:
            print("You move to Room 1.")
            player.current_room = 0
            player.position = (1, 1)

        # Pause for readability
        time.sleep(1)

        # Check if the player is defeated
        if player.health <= 0:
            print("You have been defeated. Game Over.")
            break


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


if __name__ == "__main__":
    game_loop()

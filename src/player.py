"""Module containing the player class."""

import pygame
import pygame.locals as locals

from src.connections import CONNECTIONS
from src.maps import *  # noqa: F403
from src.room import Room


class Player:
    """Player class."""

    def __init__(self, x=100, y=100, screen=None, room=START_ROOM):
        """Initialize player class."""
        self.velocity = 5
        self.player_size = (50, 50)
        self.image_dir = "src/images/player"
        self.rect = pygame.Rect((0, 0), self.player_size)
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.player_frames = 0
        self.vel_tolerance = 0.1
        self.screen = screen
        self.current_room = Room(screen, room)
        self._load_images()

    def _load_images(self):
        n_images_walking = 5
        self.player_images_north = [
            pygame.image.load(f"{self.image_dir}/north_{i}.jpg").convert_alpha()
            for i in range(n_images_walking)
        ]
        self.player_images_south = [
            pygame.image.load(f"{self.image_dir}/south_{i}.jpg").convert_alpha()
            for i in range(n_images_walking)
        ]
        self.player_images_east = [
            pygame.image.load(f"{self.image_dir}/east_{i}.jpg").convert_alpha()
            for i in range(n_images_walking)
        ]
        self.player_images_west = [
            pygame.transform.flip(image, True, False)
            for image in self.player_images_east
        ]
        self.player_images_north_east = [
            pygame.image.load(f"{self.image_dir}/north_east_{i}.jpg").convert_alpha()
            for i in range(n_images_walking)
        ]
        self.player_images_south_east = [
            pygame.image.load(f"{self.image_dir}/south_east_{i}.jpg").convert_alpha()
            for i in range(n_images_walking)
        ]
        self.player_images_north_west = [
            pygame.transform.flip(pygame.transform.rotate(image, 180), False, True)
            for image in self.player_images_north_east
        ]
        self.player_images_south_west = [
            pygame.transform.flip(pygame.transform.rotate(image, 180), False, True)
            for image in self.player_images_south_east
        ]

    def _get_player_image_per_frame(self, player_images, state):
        if self.player_frames < 50:
            self.player_frames += 1
        if state == "walking":
            if self.player_frames >= 30:
                self.player_frames = 1
            if self.player_frames < 5:
                player_image = player_images[0]
            elif self.player_frames < 10:
                player_image = player_images[1]
            elif self.player_frames < 15:
                player_image = player_images[2]
            elif self.player_frames < 20:
                player_image = player_images[3]
            elif self.player_frames < 30:
                player_image = player_images[4]
        elif state == "standing":
            player_image = player_images[0]
        return player_image

    def apply_event(self, event):
        """Change the value of the direction variable according to event."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.direction = "E"
            elif event.key == pygame.K_LEFT:
                self.direction = "W"
            elif event.key == pygame.K_UP:
                self.direction = "N"
            elif event.key == pygame.K_DOWN:
                self.direction = "S"

    def move(self):
        """Move player around when pressing arrow keys."""
        # Storing the key pressed using key.get_pressed() method
        key_pressed_is = pygame.key.get_pressed()

        old_x, old_y = self.rect.x, self.rect.y
        self.vel_x = 0
        self.vel_y = 0
        self.facing_N = False
        self.facing_S = False
        self.facing_E = False
        self.facing_W = False
        self.facing_NE = False
        self.facing_NW = False
        self.facing_SE = False
        self.facing_SW = False

        # Changing the coordinates of the player
        if key_pressed_is[locals.K_LEFT] and not key_pressed_is[locals.K_RIGHT]:
            self.vel_x -= self.velocity
            self.facing_W = True
        if key_pressed_is[locals.K_RIGHT] and not key_pressed_is[locals.K_LEFT]:
            self.vel_x += self.velocity
            self.facing_E = True
        if key_pressed_is[locals.K_UP] and not key_pressed_is[locals.K_DOWN]:
            self.vel_y -= self.velocity
            self.facing_N = True
        if key_pressed_is[locals.K_DOWN] and not key_pressed_is[locals.K_UP]:
            self.vel_y += self.velocity
            self.facing_S = True

        # Update coordinates of the player
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Get 45 angle facing components
        if self.facing_N and self.facing_E:
            self.facing_NE = True
            self.facing_N = False
            self.facing_E = False
        if self.facing_N and self.facing_W:
            self.facing_NW = True
            self.facing_N = False
            self.facing_W = False
        if self.facing_S and self.facing_E:
            self.facing_SE = True
            self.facing_S = False
            self.facing_E = False
        if self.facing_S and self.facing_W:
            self.facing_SW = True
            self.facing_S = False
            self.facing_W = False

        # facing = [
        #     self.facing_N,
        #     self.facing_S,
        #     self.facing_E,
        #     self.facing_W,
        #     self.facing_NE,
        #     self.facing_NW,
        #     self.facing_SE,
        #     self.facing_SW,
        # ]
        # if sum([face == True for face in facing]) > 1:
        #     raise RuntimeError("Player is facing more than one direction at the same time.")

        # Check for illegal movements colliding with walls
        limit_is_x = False
        limit_is_y = False
        for wall in self.current_room.walls:
            if self.rect.colliderect(wall):
                self.rect.x -= self.vel_x
                if self.rect.colliderect(wall):
                    limit_is_y = True
                self.rect.x += self.vel_x
                self.rect.y -= self.vel_y
                if self.rect.colliderect(wall):
                    limit_is_x = True
                self.rect.y += self.vel_y
                if limit_is_x:
                    self.rect.x = old_x
                if limit_is_y:
                    self.rect.y = old_y
        for door in self.current_room.doors:
            if self.rect.colliderect(door[0]):
                if door[1] == "D00":
                    current_door = door
                elif door[1] == "D01":
                    current_door = door
                self.get_connection_door(current_door)

    def draw(self, canvas):
        """Draw player on canvas."""
        if (
            abs(self.vel_x) < self.vel_tolerance
            and abs(self.vel_y) < self.vel_tolerance
        ):
            state = "standing"
        else:
            state = "walking"

        facing = False
        if self.facing_NE:
            player_image = self._get_player_image_per_frame(
                self.player_images_north_east, state
            )
            facing = True
        if self.facing_NW:
            player_image = self._get_player_image_per_frame(
                self.player_images_north_west, state
            )
            facing = True
        if self.facing_SE:
            player_image = self._get_player_image_per_frame(
                self.player_images_south_east, state
            )
            facing = True
        if self.facing_SW:
            player_image = self._get_player_image_per_frame(
                self.player_images_south_west, state
            )
            facing = True
        if self.facing_N:
            player_image = self._get_player_image_per_frame(
                self.player_images_north, state
            )
            facing = True
        if self.facing_W:
            player_image = self._get_player_image_per_frame(
                self.player_images_west, state
            )
            facing = True
        if self.facing_E:
            player_image = self._get_player_image_per_frame(
                self.player_images_east, state
            )
            facing = True
        if self.facing_S:
            player_image = self._get_player_image_per_frame(
                self.player_images_south, state
            )

        if not facing:
            player_image = self._get_player_image_per_frame(
                self.player_images_south, state
            )

        canvas.blit(player_image, (self.rect.x, self.rect.y))

    def get_connection_door(self, door):
        """Find the connection for a certain door and redirect the player there."""
        door_name = door[1]

        for connection in CONNECTIONS:
            if connection[0] == door_name:
                next_door = connection[1]
                next_room = connection[3]
                self.current_room = Room(self.screen, globals()[next_room])
                for door in self.current_room.doors:
                    if door[1] == next_door:
                        self.rect.x, self.rect.y = (
                            door[0].x + connection[4],
                            door[0].y + connection[5],
                        )

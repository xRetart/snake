from copy import deepcopy
from enum import Enum
from typing_extensions import Self
from dataclasses import dataclass
from random import choice

import pygame
import numpy


class Event:
    ADVANCE = pygame.USEREVENT + 1

class Color:
    DARK = (19, 23, 21)
    LIGHT = (21, 30, 28)

    APPLE = (155, 23, 23)

    class Snake:
        TAIL = (19, 108, 19)
        HEAD = (23, 130, 23)


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    def opposite(self) -> Self:
        match self:
            case Direction.UP: return Direction.DOWN
            case Direction.DOWN: return Direction.UP
            case Direction.LEFT: return Direction.RIGHT
            case Direction.RIGHT: return Direction.LEFT

@dataclass
class Coordinate:
    x: int
    y: int

    def advance(self, direction: Direction):
        match direction:
            case Direction.UP: self.y -= 1
            case Direction.DOWN: self.y += 1
            case Direction.LEFT: self.x -= 1
            case Direction.RIGHT: self.x += 1


@dataclass
class Grid:
    width: int
    height: int

    def draw_tile(self, coordinate: Coordinate, color, surface: pygame.surface.Surface) -> None:
        tile_size = surface.get_size()[0] / self.width
        pygame.draw.rect(surface, color, pygame.Rect((coordinate.x * tile_size, coordinate.y * tile_size), (tile_size, tile_size)))

    def draw(self, surface: pygame.surface.Surface) -> None:
        for x in range(self.width):
            for y in range(self.width):
                if (x + y) % 2 == 0:
                    self.draw_tile(Coordinate(x, y), Color.LIGHT, surface)

    def in_bound(self, coordinate: Coordinate) -> bool:
        return \
            0 <= coordinate.x < self.width and \
            0 <= coordinate.y < self.height

class Snake:
    def __init__(self, grid: Grid) -> None:
        self.segments = [Coordinate(0, 2), Coordinate(0, 1), Coordinate(0, 0)]
        self.grid = grid
        self.direction = Direction.DOWN
        self.new_apple()

    def new_apple(self) -> None:
        coordinates = [Coordinate(coordinate[0], coordinate[1]) for coordinate in numpy.ndindex((self.grid.width, self.grid.height))]
        empty = [coordinate for coordinate in coordinates if coordinate not in self.segments]
        self.apple = choice(empty)

    def change_direction(self, new: Direction) -> None:
        if new is not self.direction.opposite():
            self.direction = new

    def advance(self) -> bool:
        new = deepcopy(self.segments[0])
        new.advance(self.direction)

        if not self.grid.in_bound(new) or new in self.segments:
            return False

        if new == self.apple:
            self.new_apple()
        else:
            del self.segments[-1]

        self.segments.insert(0, new)
        return True

    def draw(self, surface) -> None:
        head, *tail = self.segments
        draw = lambda coordinate, color: self.grid.draw_tile(coordinate, color, surface)

        draw(head, Color.Snake.HEAD)
        for segment in tail:
            draw(segment, Color.Snake.TAIL)

        draw(self.apple, Color.APPLE)

class Window:
    def __init__(self, dimensions) -> None:
        self.surface = pygame.display.set_mode(dimensions)

    def draw(self, snake: Snake):
        self.surface.fill(Color.DARK)

        snake.grid.draw(self.surface)
        snake.draw(self.surface)

        pygame.display.update()

def controls(key, snake: Snake) -> None:
    change_direction = lambda new: snake.change_direction(new)

    match key:
        case pygame.K_UP: change_direction(Direction.UP)
        case pygame.K_DOWN: change_direction(Direction.DOWN)
        case pygame.K_LEFT: change_direction(Direction.LEFT)
        case pygame.K_RIGHT: change_direction(Direction.RIGHT)


# constants
FPS = 60


def main():
    run = True
    clock = pygame.time.Clock()
    win = Window((500, 500))
    snake = Snake(Grid(10, 10))

    pygame.time.set_timer(Event.ADVANCE, 250)

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT: run = False
                case pygame.KEYDOWN: controls(event.key, snake)
                case Event.ADVANCE: run = snake.advance()

        win.draw(snake)

    pygame.quit()

if __name__ == "__main__":
    main()

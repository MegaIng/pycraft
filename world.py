from collections import namedtuple
from typing import List, Dict, Tuple, Set

import pygame

from CONFIGURATION import SCALE
from block import Block
from generator import Generator
from object import Object
from util import Vec2d, Rect, LimitedSizeDict

force = pos = Tuple[int, int]

State = namedtuple("state", "img scroll blocks")


class World:
    def __init__(self, generator: Generator, gravity: force):

        self._generator = generator
        self.gravity = Vec2d(gravity)
        self._blocks: Dict[int, List[Block]] = {}
        self._objects: Set[Object] = set()
        self._last_states: Dict[Tuple[pos, pos], State] = LimitedSizeDict(size_limit=100)

    def add(self, obj):
        self._objects.add(obj)

    def get_column(self, item: int):
        if item not in self._blocks:
            self._blocks[item] = self._generator(item)
        return self._blocks[item]

    def get_block(self, item: pos):
        return self.get_column(item[0])[item[1]]

    def update(self, dt):
        # print(1 / dt)
        for obj in self._objects:
            obj.pos += obj.velocity * dt
            x1, y1 = obj.rect.topleft
            x2, y2 = obj.rect.bottomright
            x1 = round(x1)
            x2 = round(x2)
            y1 = round(y1)
            y2 = round(y2)
            points = [(x, y) for x in range(x1 - 2, x2 + 2) for y in range(y1 - 2, y2 + 2)]
            obj.one_ground = False
            for r in list(obj.rect.collidelistall([tuple(self.get_block(p).rect) for p in points if self.get_block(p).has_collision])):
                r: Rect = Rect(r)
                n = obj.pos - r.center
                n = n.unit

                if n.x > 0.5:
                    obj.rect.left = r.right + 0.05
                    obj.velocity.x = 0
                    obj.one_wall = True
                elif n.x < -0.5:
                    obj.rect.right = r.left - 0.05
                    obj.velocity.x = 0
                    obj.one_wall = True
                else:
                    if n.y > 0:
                        obj.rect.top = r.bottom
                        obj.velocity.y = 0
                        obj.one_ground = True
                    elif n.y < 0:
                        obj.rect.bottom = r.top
                        obj.velocity.y = 0
                        obj.one_ground = False
            obj.velocity += self.gravity * dt

    def get_blocks(self, x_range: pos, y_range: pos) -> pygame.Surface:
        if (tuple(x_range), tuple(y_range)) in self._last_states:
            state = self._last_states[(tuple(x_range), tuple(y_range))]
        else:
            size = ((x_range[1] - x_range[0]) * SCALE, (y_range[1] - y_range[0]) * SCALE)
            state = State(pygame.Surface(size, pygame.SRCALPHA), (tuple(x_range), tuple(y_range)), {})
            state.img.fill((0, 0, 0, 0))
            self._last_states[(tuple(x_range), tuple(y_range))] = state

        for x in range(0, x_range[1] - x_range[0]):
            for y in range(0, y_range[1] - y_range[0] + 1):
                b = self.get_column(x_range[0] + x)[y_range[0] + y]
                if (x, y) not in state.blocks or state.blocks[(x, y)] is not b:
                    state.blocks[(x, y)] = b
                    xo, yo = b.draw_offset
                    state.img.blit(b.image, ((x * SCALE) - xo, state.img.get_height() - (y * SCALE) - yo))
        return state.img

    def image(self, x_range: pos, y_range: pos) -> Tuple[pygame.Surface, List[Tuple[pygame.Surface, pos]]]:
        x_range = sorted(x_range)
        y_range = sorted(max(min(y, 255), 0) for y in y_range)
        sur = self.get_blocks(x_range, y_range)
        objs_to_draw = []
        for obj in (obj for obj in self._objects):
            p = obj.pos
            if x_range[0] < p.x < x_range[1] and y_range[0] < p.y < y_range[1]:
                img = obj.image
                off_x, off_y = obj.draw_offset
                rel_pos = int((p.x - x_range[0]) * SCALE) + off_x, sur.get_height() - int((p.y - y_range[0]) * SCALE) + off_y
                objs_to_draw.append((img, rel_pos))
        return sur, objs_to_draw

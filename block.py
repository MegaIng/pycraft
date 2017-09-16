from typing import Dict, Any

import pygame

from util import Vec2d, Rect


class Block:
    image_paths = {}
    allowed_data = {}
    has_collision = True

    def __init__(self, pos, data=None):
        self.images = {}
        for n, p in self.image_paths.items():
            self.images[n] = pygame.image.load(p)
        self.pos: Vec2d = Vec2d(pos)
        self._data: Dict[str, Any] = None
        self._hash = None
        self._image = None
        self._rect = None
        self._draw_offset = None
        self.data = data or {}

    def __str__(self):
        return f"{self.id} {self.data} ({self.pos})"

    def _get_hash(self):
        return (self.__class__.__name__,) + tuple(sorted(self._data.items())) + (self.pos.x, self.pos.x)

    def __eq__(self, other):
        return isinstance(other, Block) and self._get_hash() == other._get_hash()

    def __ne__(self, other):
        return not isinstance(other, Block) or self._get_hash() != other._get_hash()

    @property
    def data(self) -> Dict[str, Any]:
        return self._data

    @data.setter
    def data(self, value: Dict[str, Any]):
        self._data = {}
        for n in self.allowed_data:
            if n in value:
                if value[n] not in self.allowed_data[n]:
                    raise ValueError(f"Field '{n}' of class '{self.__class__.__name__}' can not have value '{value[n]}'")
                self._data[n] = value.pop(n)
            else:
                self.data[n] = self.allowed_data[n][0]
        if len(value) > 0:
            raise ValueError(f"Fields '{tuple(value.keys())} ar not allowed for block '{self.__class__.__name__}''")

    def _render(self):
        raise NotImplementedError

    def _render_rect(self):
        raise NotImplementedError

    @property
    def image(self) -> pygame.Surface:
        if self._hash != self._get_hash():
            self._render()
            self._render_rect()
            self._hash = self._get_hash()
        return self._image

    @property
    def draw_offset(self):
        if self._hash != self._get_hash():
            self._render()
            self._render_rect()
            self._hash = self._get_hash()
        return self._draw_offset

    @property
    def rect(self) -> Rect:
        if self._hash != self._get_hash():
            self._render()
            self._render_rect()
            self._hash = self._get_hash()
        return self._rect

    @property
    def id(self):
        return self.__module__.replace("mods.", "") + ":" + self.__class__.__name__

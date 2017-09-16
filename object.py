from typing import Dict, Any, Tuple

import pygame

from util import Vec2d, Rect


def rotate_image(img, rotation) -> Tuple[pygame.Surface, Tuple[int, int]]:
    rotated_image = pygame.transform.rotate(img, rotation)
    return rotated_image,


class BodyPart:
    def __init__(self, image: pygame.Surface, size):
        w1 = size
        w2 = image.get_width() / 2 - w1
        h1 = size
        h2 = image.get_height() - h1
        self.top = RotationSurface(image.subsurface((w1, 0, w2, h1)))
        self.bottom = RotationSurface(image.subsurface((w1 + w2, 0, w2, h1)))
        self.right = RotationSurface(image.subsurface((0, h1, w1, h2)))
        self.left = RotationSurface(image.subsurface((w1 + w2, h1, w1, h2)))
        self.front = RotationSurface(image.subsurface((w1, h1, w2, h2)))
        self.back = RotationSurface(image.subsurface((w1 * 2 + w2, h1, w2, h2)))


class RotationSurface(pygame.Surface):
    def __init__(self, sur: pygame.Surface, rotation_point=None):
        self._sur = sur
        super(RotationSurface, self).__init__((sur.get_width() * 2, sur.get_height() * 2), pygame.SRCALPHA)
        self._rotation_point = None
        self.rotation_point = rotation_point if rotation_point is not None else sur.get_rect().center
        self._cache = {}

    @property
    def rotation_point(self):
        return self._rotation_point

    @rotation_point.setter
    def rotation_point(self, value):
        self._rotation_point = value
        self.fill((0, 0, 0, 0))
        self._cache = {}
        self.blit(self._sur, (self._sur.get_width() - value[0], self._sur.get_height() - value[1]))

    def blit_onto(self, screen, rotation, center_pos):
        rotation = round(rotation)
        if rotation in self._cache:
            img = self._cache[rotation]
        else:
            print("create")
            img = pygame.transform.rotate(self, rotation)
            self._cache[rotation] = img
        r = img.get_rect(center=center_pos)
        screen.blit(img, r)


class Object:
    size = (1, 1)
    image_paths = {}
    allowed_data = {}
    image_parts: Dict[str, Tuple[str, Tuple[int, int, int, int], int]]
    has_shape = True

    def __init__(self, pos, data=None):
        self.base_images = {}
        for n, p in self.image_paths.items():
            self.base_images[n] = pygame.image.load(p)
        self._velocity: Vec2d = Vec2d((0, 0))
        self.images: Dict[str, BodyPart] = {}
        for n, v in self.image_parts.items():
            self.images[n] = BodyPart(self.base_images[v[0]].subsurface(v[1]), v[2])
        self._data: Dict[str, Any] = None
        self._hash = None
        self._image = None
        self._rect = Rect(pos, self.size)
        self._draw_offset = None
        self.data = data or {}
        self.one_ground = False
        self.setup()

    def __str__(self):
        return f"{self.id} {self.data}"

    def _get_hash(self):
        return hash(tuple(self._data.items()))

    def setup(self):
        pass

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
                v = self.allowed_data[n][0]
                if isinstance(v, type):
                    v = v()
                self.data[n] = v
        if len(value) > 0:
            raise ValueError(f"Fields '{tuple(value.keys())} are not allowed for block '{self.__class__.__name__}''")

    @property
    def pos(self) -> Vec2d:
        return Vec2d(self._rect.center)

    @pos.setter
    def pos(self, value):
        self._rect.center = tuple(value)

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        self._velocity = Vec2d(value)

    def _render(self):
        raise NotImplementedError

    @property
    def image(self) -> pygame.Surface:
        if self._hash != self._get_hash():
            self._render()
            self._hash = self._get_hash()
        return self._image

    @property
    def draw_offset(self):
        if self._hash != self._get_hash():
            self._render()
            self._hash = self._get_hash()
        return self._draw_offset

    @property
    def rect(self) -> Rect:
        if self._hash != self._get_hash():
            self._render()
            self._hash = self._get_hash()
        return self._rect

    @property
    def mass(self):
        return self.rect.w * self.rect.h

    @property
    def id(self):
        return self.__module__.replace("mods.", "") + ":" + self.__class__.__name__

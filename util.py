from collections import OrderedDict
from math import cos, sin, radians, atan2, degrees, sqrt

import pygame


def is_pressed(key):
    return pygame.key.get_pressed()[key]


def get_mod_item(mods, item):
    item = item.split(":")
    x = mods[item[0]]
    for n in item[1:]:
        x = getattr(x, n)
    return x


def rotPoint(point, axis, ang):
    """ Orbit. calcs the new loc for a point that rotates a given num of degrees around an axis point,
    +clockwise, -anticlockwise -> tuple x,y
    """
    x, y = point[0] - axis[0], point[1] - axis[1]
    radius = sqrt(x * x + y * y)  # get the distance between points

    ang = radians(ang)  # convert ang to radians.

    h = axis[0] + (radius * cos(ang))
    v = axis[1] + (radius * sin(ang))

    return h, v


class Vec2d(list):
    def __init__(self, x, y=None):
        super().__init__()
        if y is None:
            x, y = x
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vec2d({self.x}, {self.y})"

    def __add__(self, other):
        return Vec2d(self.x + other[0], self.y + other[1])

    def __iadd__(self, other):
        self[0] += other[0]
        self[1] += other[1]
        return self

    def __sub__(self, other):
        return Vec2d(self.x - other[0], self.y - other[1])

    def __isub__(self, other):
        self[0] -= other[0]
        self[1] -= other[1]
        return self

    def __mul__(self, other):
        return Vec2d(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self * other

    def __imul__(self, other):
        self[0] *= other
        self[1] *= other
        return self

    def __truediv__(self, other):
        return Vec2d(self.x / other, self.y / other)

    def __itruediv__(self, other):
        self[0] /= other
        self[1] /= other
        return self

    def __iter__(self):
        yield self.x
        yield self.y

    @property
    def magnitude(self):
        return (self.x * self.x + self.y * self.y) ** 0.5

    @property
    def rotation(self):
        return degrees(atan2(self.x, self.y))

    @property
    def unit(self):
        return Vec2d(self.x / self.magnitude, self.y / self.magnitude)

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError

    def dot(self, other):
        return self.x * other[0] + self.y * other[1]

    def rotate(self, angle, other=(0, 0)):
        angle = radians(angle)
        new = self - other
        return Vec2d(new.x * cos(angle) - new.y * sin(angle),
                     new.y * cos(angle) + new.x * sin(angle)) + other

    @classmethod
    def from_rotation(cls, angle, magnitude=1):
        return cls(cos(angle), sin(angle)) * magnitude


class Rect:
    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        if len(args) == 2:
            (x, y), (w, h) = args
        else:
            x, y, w, h = args
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __repr__(self):
        return "Rect" + repr((self.x, self.y, self.w, self.h))

    @property
    def bottom(self):
        return self.y + self.h

    @bottom.setter
    def bottom(self, value):
        self.y = value - self.h

    @property
    def right(self):
        return self.x + self.w

    @right.setter
    def right(self, value):
        self.x = value - self.w

    @property
    def min(self):
        return Vec2d(self.x, self.y)

    @min.setter
    def min(self, value):
        self.x, self.y = value

    @property
    def max(self):
        return Vec2d(self.x + self.w, self.y + self.h)

    @max.setter
    def max(self, value):
        self.x = value[0] - self.w
        self.y = value[1] - self.h

    @property
    def left(self):
        return self.x

    @left.setter
    def left(self, value):
        self.x = value

    @property
    def top(self):
        return self.y

    @top.setter
    def top(self, value):
        self.y = value

    @property
    def topleft(self):
        return self.x, self.y

    @topleft.setter
    def topleft(self, value):
        self.x, self.y = value

    @property
    def bottomright(self):
        return self.x + self.w, self.y + self.h

    @bottomright.setter
    def bottomright(self, value):
        self.x = value[0] - self.w
        self.y = value[1] - self.h

    @property
    def center(self):
        return self.x + self.w / 2, self.y + self.h / 2

    @center.setter
    def center(self, value):
        self.x = value[0] - self.w / 2
        self.y = value[1] - self.h / 2

    @property
    def centerleft(self):
        return self.x, self.y + self.h / 2

    @centerleft.setter
    def centerleft(self, value):
        self.x = value[0]
        self.y = value[1] - self.h / 2

    def collide(self, other):
        other = Rect(other)
        return ((other.left <= self.left <= other.right or other.left <= self.right <= other.right) and
                (other.top <= self.top <= other.bottom or other.top <= self.bottom <= other.bottom)) or \
               ((self.left <= other.left <= self.right or self.left <= other.right <= self.right) and
                (self.top <= other.top <= self.bottom or self.top <= other.bottom <= self.bottom))

    def collidedictall(self, d: dict):
        for r, i in d.items():
            if self.collide(r):
                yield r, i

    def collidelistall(self, l: list):
        for r in l:
            if self.collide(r):
                yield r

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.w
        yield self.h


class LimitedSizeDict(OrderedDict):
    def __init__(self, *args, **kwds):
        self.size_limit = kwds.pop("size_limit", None)
        OrderedDict.__init__(self, *args, **kwds)
        self._check_size_limit()

    def __setitem__(self, key, value, *args, **kwargs):
        OrderedDict.__setitem__(self, key, value, *args, **kwargs)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)

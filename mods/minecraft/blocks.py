import pygame

from block import Block
from util import Rect


class StateBlock(Block):
    default = None

    def __init_subclass__(cls, **kwargs):
        cls.allowed_data = {"state": list(cls.image_paths.keys())}
        if cls.default is not None:
            cls.allowed_data["state"].remove(cls.default)
            cls.allowed_data["state"].insert(0, cls.default)

    def _render(self):
        self._image = self.images[self.data["state"]]
        self._draw_offset = 0, 0

    def _render_rect(self):
        self._rect = Rect(tuple(self.pos), (self._image.get_size()[0] / 16, self._image.get_size()[1] / 16))


class Air(StateBlock):
    has_collision = False
    image_paths = {"empty": "assets/minecraft/textures/blocks/empty.png"}


class Dirt(StateBlock):
    image_paths = {
        "coarse": "assets/minecraft/textures/blocks/coarse_dirt.png",
        "normal": "assets/minecraft/textures/blocks/dirt.png"
    }
    default = "normal"


class Stone(StateBlock):
    image_paths = {
        "normal": "assets/minecraft/textures/blocks/stone.png"
    }


class Grass(StateBlock):
    image_paths = {
        "normal": "assets/minecraft/textures/blocks/grass_side.png"
    }
    # def add_to(self, space, position):
    #     super(Grass, self).add_to(space,position)
    #     print(self.shape.get_vertices())

from importlib import import_module
from typing import Tuple, List, Dict, Any

import pygame
from ezpygame import Scene

from control_handler import ControlHandler
# from object import Object
from object import Object
from util import get_mod_item
from world import World


class PlayScene(Scene):
    def __init__(self, title="Minecraft 2d", resolution=(640, 480), frame_rate=60):
        super().__init__(title, resolution, frame_rate)
        self.world: World = None
        self.mods = None
        self.modpack = None
        self.controller = None
        self.player = None
        self.scroll: Tuple[int, int] = [0, 1600]
        self.dt = 0

    def on_enter(self, previous_scene):
        super(PlayScene, self).on_enter(previous_scene)
        if not hasattr(previous_scene, "mods"):
            raise TypeError("Previous scene does not have mods")
        if not hasattr(previous_scene, "selected_modpack"):
            raise TypeError("Previous scene does not have modpack")
        self.modpack: Dict[str:Any] = previous_scene.selected_modpack
        self.mods: Dict[str:module] = previous_scene.mods
        self.mods.update({n: import_module("mods.{}".format(n)) for n in self.modpack["mods"] if n not in self.mods})

        self.world: World = World(get_mod_item(self.mods, self.modpack["generator"])(), self.modpack["gravity"])
        self.controller: List[ControlHandler] = [get_mod_item(self.mods, c)(self) for c in self.modpack["controller"]]
        self.player: Object = get_mod_item(self.mods, self.modpack["player"][0])((0, 0))
        self.player.pos = self.modpack["player"][1]
        self.world.add(self.player)
        self.i = 0

    def handle_event(self, event):
        for con in self.controller:
            con.handle(event)

    def update(self, dt):
        self.i += 1
        dt *= 0.001
        self.world.update(dt)
        self.dt += dt
        for con in self.controller:
            con.update(dt)

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 136, 255))
        img, l = self.world.image((int(self.scroll[0] // 16), int((self.scroll[0] + self.application.resolution[0]) // 16 + 2)),
                                  (int(self.scroll[1] // 16), int((self.scroll[1] + self.application.resolution[1]) // 16 + 2)))
        offx, offy = -(self.scroll[0] % 16), -32 + (self.scroll[1] % 16)
        screen.blit(img, (offx, offy))
        for img, (x, y) in l:
            screen.blit(img, (x + offx, y + offy))

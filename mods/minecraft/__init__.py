import pygame
from noise import pnoise1 as noise

from control_handler import ControlHandler
from generator import Generator
from mods.minecraft import blocks
from object import Object
from util import is_pressed, Vec2d


class SimpleGenerator(Generator):
    def _generate(self, x: int):
        l = []
        y = 0
        for _ in range(round((noise(x * 0.01) + 1) * 50) + 50):
            l.append(blocks.Stone((x, y)))
            y += 1
        for _ in range(3):
            l.append(blocks.Dirt((x, y)))
            y += 1
        l.append(blocks.Grass((x, y)))
        y += 1
        for _ in range(5):
            l.append(blocks.Air((x, y)))
            y += 1
        for _ in range(255 - len(l)):
            l.append(blocks.Air((x, y)))
            y += 1
        self._generated[x] = l


class Player(Object):
    allowed_data = {
        "head_rotation": (float, -80, 80),
        "look_direction": (1, -1),
        "foot_step": (float, (-45, 45)),
    }
    image_paths = {
        "steve": "assets/minecraft/textures/entity/steve.png"
    }
    image_parts = {
        "head": ("steve", (0, 0, 32, 16), 8),
        "body": ("steve", (16, 16, 24, 16), 4),
        "right_leg": ("steve", (0, 16, 16, 16), 4),
        "left_leg": ("steve", (16, 48, 16, 16), 4),
        "right_arm": ("steve", (40, 16, 16, 16), 4),
        "left_arm": ("steve", (32, 48, 16, 16), 4)
    }
    size = (0.75, 2)

    def _render(self):
        self._image = pygame.Surface((32, 64), pygame.SRCALPHA)
        head_rotation = self.data["head_rotation"]
        foot_step = self.data["foot_step"]
        if 90 > self.data["head_rotation"] > -90:
            self.images["left_arm"].right.blit_onto(self._image, foot_step * 0.75, (16, 26))
            self.images["body"].right.blit_onto(self._image, 0, (16, 30))
            self.images["head"].right.blit_onto(self._image, head_rotation, (16, 24))
            self.images["left_leg"].right.blit_onto(self._image, foot_step, (16, 36))
            self.images["right_leg"].right.blit_onto(self._image, -foot_step, (16, 36))
            self.images["right_arm"].right.blit_onto(self._image, -foot_step * 0.75, (16, 26))
        else:
            head_rotation += 180
            self.images["left_arm"].left.blit_onto(self._image, foot_step * 0.75, (16, 26))
            self.images["body"].left.blit_onto(self._image, 0, (16, 30))
            self.images["head"].left.blit_onto(self._image, head_rotation, (16, 24))
            self.images["right_leg"].left.blit_onto(self._image, -foot_step, (16, 36))
            self.images["left_leg"].left.blit_onto(self._image, foot_step, (16, 36))
            self.images["right_arm"].left.blit_onto(self._image, -foot_step * 0.75, (16, 26))

        self._draw_offset = (-16, -16)

    def setup(self):
        self.images["head"].right.rotation_point = (4, 8)
        self.images["head"].left.rotation_point = (4, 8)
        self.images["right_leg"].right.rotation_point = (2, 0)
        self.images["right_leg"].left.rotation_point = (2, 0)
        self.images["left_leg"].right.rotation_point = (2, 0)
        self.images["left_leg"].left.rotation_point = (2, 0)
        self.images["right_arm"].right.rotation_point = (2, 2)
        self.images["right_arm"].left.rotation_point = (2, 2)
        self.images["left_arm"].right.rotation_point = (2, 2)
        self.images["left_arm"].left.rotation_point = (2, 2)


class ExploreGravityControl(ControlHandler):
    repeat_args = (1, 1)
    s = 0.75

    def update(self, dt):
        v = self.scene.player.velocity
        if is_pressed(pygame.K_LEFT):
            v.x = -200 * dt
            self.scene.player.data["look_direction"] = "left"
        elif is_pressed(pygame.K_RIGHT):
            v.x = 200 * dt
            self.scene.player.data["look_direction"] = "right"
        else:
            v.x = 0
            self.scene.player.data["foot_step"] = 0
        self.scene.player.velocity = v
        p = self.scene.player.pos
        r = self.scene.application.resolution
        self.scene.scroll = [p.x * 16 - r[0] / 2 + 16, p.y * 16 - r[1] / 2]
        self.scene.player.data["foot_step"] += v.x * self.s
        if -45 > self.scene.player.data["foot_step"]:
            self.s *= -1
            self.scene.player.data["foot_step"] = -45
        if 45 < self.scene.player.data["foot_step"]:
            self.s *= -1
            self.scene.player.data["foot_step"] = 45
        self.scene.player.data["head_rotation"] = (Vec2d(pygame.mouse.get_pos()) - (r[0] / 2 - 16, r[1] / 2)).rotation - 90

    def handle(self, event: pygame.event.EventType):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.scene.player.one_ground:
                    self.scene.player.velocity += (0, 7)

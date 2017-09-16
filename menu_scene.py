from ezpygame import Scene

from world_scene import PlayScene


class MenuScene(Scene):
    def __init__(self, modpack, title="Minecraft 2d", resolution=(640, 480), frame_rate=60):
        self.selected_modpack = modpack
        self.mods = {}
        super().__init__(title, resolution, frame_rate)

    def update(self, dt):
        self.application.change_scene(PlayScene())

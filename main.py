from ezpygame import Application

from menu_scene import MenuScene

mod_pack = {
    "mods": ["minecraft"],
    "generator": "minecraft:SimpleGenerator",
    "controller": ["minecraft:ExploreGravityControl"],
    "player": ("minecraft:Player", (-5, 110)),
    "gravity": (0, -20)
}

app = Application("", (1, 1), 0)
app.run(MenuScene(mod_pack))

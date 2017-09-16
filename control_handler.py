import pygame


class ControlHandler:
    repeat_args = ()

    def __init__(self, scene):
        pygame.key.set_repeat(*self.repeat_args)
        self.scene = scene

    def handle(self, event: pygame.event.EventType):
        pass

    def update(self, dt):
        pass

from time import sleep
from typing import Union
from threading import Thread
from phue import Bridge, Light
from colors import Color

from utils import flatten, strvals

class LightUpdate:
    def __init__(self, lights: Union[Light, list[Light]], color: Color = None, transition: float = None):
        if not isinstance(lights, list):
            lights = [lights]
        self.lights = flatten(lights)
        self.color = color
        self.transition = transition
    
    def get_cmd(self):
        return {"on": True, "hsb": self.color, "transitiontime": int(self.transition * 10)}

    def __str__(self):
        return f"{strvals(self.lights)}, {self.get_cmd()}"

class LightUpdateManager:

    def __init__(self, bridge):
        self.__updates: list[LightUpdate] = []
        self.__bridge: Bridge = bridge
        self.__running = True
        self.__thread: Thread = Thread(target=self.process_requests)
        self.__thread.start()

    def add_update(self, update):
        self.__updates.append(update)

    def process_requests(self):
        while self.__running:
            if self.__updates:
                update = self.__updates.pop(0)
                self.__bridge.set_light(update.lights, update.get_cmd())
            sleep(0.2)
    
    def stop(self):
        self.__running = False
        self.__thread.join()

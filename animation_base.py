from collections import defaultdict
from threading import Thread
from time import sleep

from phue import Light
from colors import *
from utils import *

class Animation():
    counter = defaultdict(int)
    global_brightness = 1
    bridge = None

    def __init__(self, duration: float = None, name: str = None, silent: bool = True):
        self.duration = duration
        self.silent = silent
        self.name = self.make_name(name)
        self.running = False
    
    def make_name(self, name):
        if name:
            return name
        class_name = self.__class__.__name__
        count = Animation.counter[class_name]
        Animation.counter[class_name] += 1
        return f"{class_name} {count}"

    def log(self, msg = ""):
        if not self.silent:
            light_names =strvals(flatten(self.lights))
            print(f"{self.name} | {self.duration} | {light_names}\n\t{msg}")

    def __str__(self):
        return self.name

    def animate(self, lights, duration = None, silent = True):
        if not isinstance(lights, list):
            lights = [lights]
        self.duration = self.duration or duration
        if not self.duration:
            raise Exception(f"{self.name}: duration not be set")
        self.lights = lights
        self.silent = silent and self.silent
        self.running = True
        self.log()

    def stop(self):
        self.running = False
        if hasattr(self, "animation"):
            self.animation.stop()
        if hasattr(self, "animations"):
            for animation in self.animations:
                animation.stop() 
    
    def threaded(self, lights, **kwargs):
        thread = Thread(target=self.animate, args=(lights,), kwargs=kwargs)
        thread.start()
        return thread

    def wait(self, time: float, steps: int = 1000):
        for _ in range(steps):
            if not self.running:
                return
            sleep(time / steps)
    
    def set_lights(self, lights: list[Light], hsb: Color, time: float = 0):
        if not Animation.bridge:
            raise Exception("No bridge set")
        if not self.running:
            self.silent or print(f"{self.name}: tried to set lights while not running")
            return
        hsb = set_brightness(hsb, hsb.brightness * Animation.global_brightness)
        cmd = {"on": True, "hsb": hsb, "transitiontime": int(time * 10)}
        Animation.bridge.set_light(lights, cmd)
        self.wait(self.duration)
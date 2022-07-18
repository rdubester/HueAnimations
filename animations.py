import threading
from time import sleep
import logging
from collections import defaultdict
from typing import Callable, List
from xmlrpc.client import Boolean
from phue import Light, Bridge
from util import *

class AnimationManager:
    def __init__(self):
        self.bridge = None

    def set_lights(self, *args, **kwargs):
        if not self.bridge:
            raise Exception("Bridge not set")
        logging.info("Setting light:", args, kwargs)
        self.bridge.set_light(*args, **kwargs)


class AnimationThread():

    manager = AnimationManager()

    def __init__(self, name: str, runtime: float, loop: bool, func: Callable, *args, **kwargs):
        self.name = name
        self.runtime = runtime
        self.loop = loop
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
        self.thread = threading.Thread(target=self.run)
        self.timer = threading.Timer(self.runtime, self.stop)

    def __str__(self):
        return self.name

    def start(self, blocking, silent):
        self.thread.start()
        self.timer.start()
        if blocking:
            silent or print(f"{self}: Blocking")
            self.timer.join()
    
    def run(self):
        self.running = True
        while self.running:
            self.func(*self.args, **self.kwargs)
            if not self.loop:
                break

    def stop(self):
        self.running = False

    def set_lights(self, lights: List[Light], command: dict, *args, **kwargs):
        if not self.running:
            print(f"{self}: Can't set lights while not running")
            return
        ids = [l.light_id for l in lights]
        AnimationThread.manager.set_lights(ids, command, *args, **kwargs)


# a list of animations that play concurrently
class AnimationGroup():

    counter = defaultdict(int)

    def __init__(self,
                animations = [],
                duration: float = None,
                loop: bool = True,
                stagger: int = 0,
                sequence: bool = False,
                name: str = '',
                silent: bool = True):
        AnimationGroup.counter[self.__class__.__name__] += 1
        self.animations = animations
        self.duration = duration
        self.loop = loop
        self.sequence = sequence
        self.stagger = stagger
        self.name = self.make_name(name)
        self.silent = silent
        self.anim_thread = None

    # TODO: make a setter modify animation lights dyamically?
    def get_lights(self):
        lights = set()
        for animation in self.animations:
            lights.update(animation.lights)
        return lights
    
    def make_name(self, name):
        class_name = self.__class__.__name__
        count = AnimationGroup.counter[class_name]
        return f"{class_name} {name} {count}"

    def __str__(self):
        return f"{self.name}"

    def play(self, runtime = None, blocking = True, silent = True):
        self.runtime = runtime
        self.calculate_timing()
        self.blocking = blocking
        self.silent = silent and self.silent
        if self.anim_thread:
            self.anim_thread.stop()
        self.anim_thread = AnimationThread(f'Thread: {self.name}', self.runtime, self.loop, self.animate)
        self.anim_thread.start(blocking, self.silent)
        return self

    def stop(self):
        self.silent or print(f"Animation interrupted: {self}")
        for animation in self.animations:
            animation.stop()
        self.anim_thread.stop()
    
    def animate(self):
        if not self.silent:
            print(f"{self}: {self.duration=}, {self.runtime=}, {self.loop=}, {self.sequence=}, {self.stagger=}")
        for animation in self.animations:
            runtime = animation.duration if self.sequence else self.duration
            animation.play(runtime, blocking=self.sequence, silent=self.silent)
            sleep(self.stagger)
        
    def set_lights(self, dict, *args, **kwargs):
        if self.anim_thread is None:
            raise Exception(f"{self}: No animation thread to set lights")
        self.anim_thread.set_lights(self.lights, dict, *args, **kwargs)
    
    def calculate_timing(self):
        # compute duration from subanimation durations if possible 
        if self.duration is None:
            if self.animations and all(a.duration is not None for a in self.animations):
                op = sum if self.sequence else max
                self.duration = op([animation.duration for animation in self.animations])

        # apply runtime / duration laws
        if self.runtime is None and self.duration is None:
            raise Exception(f"{self}: No animation timing specified")
        if self.runtime is None:
            self.runtime = self.duration
        if self.duration is None:
            self.duration = self.runtime

class Animation(AnimationGroup):
    def __init__(self, lights = set(), *args, **kwargs):
        self.lights = as_set(lights)
        super().__init__(*args, **kwargs)

    def get_lights(self):
        return self.lights
    
class Wait(Animation):
    def animate(self):
        pass


class Fade(Animation):

    def __init__(self, target, *args, **kwargs):
        self.target = target
        super().__init__(*args, **kwargs)

    def animate(self):
        self.silent or print(f"{self}: Fading {[str(light) for light in self.lights]} to {self.target}")
        transitiontime = int(self.duration * 10)
        self.set_lights({"on": True, "hsb": self.target, "transitiontime": transitiontime})
        sleep(self.duration)

class FadeFrom(Fade):
    def __init__(self, source, target, *args, **kwargs):
        self.source = source
        super().__init__(target, *args, **kwargs)
        
    def animate(self):
        # snap to source color
        self.silent or print(f"{self}: Setting {[str(light) for light in self.lights]} to {self.source}")
        self.set_lights({"on": True, "hsb": self.source, "transitiontime": 0})
        # fade to target color
        super().animate()

class Wave(Animation):
    def __init__(self, colors, frequency, shape = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        interval = frequency /  len(colors)

        if shape is None:
           shape = [1] * len(colors)
        if self.stagger is None:
            self.stagger = len(colors)/len(self.lights) * frequency

        weights = [x * len(colors) / sum(shape) for x in shape]
        if len(colors) != len(shape):
            raise Exception("Colors and shape must be the same length")

        self.animations = []
        for light in self.get_lights():
            f = AnimationGroup(
                [Fade(color, light, duration = interval * weight) for color, weight in zip(colors, weights)],
                sequence=True)
            self.animations.append(f)
        
        
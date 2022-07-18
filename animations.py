import threading
from time import sleep
import logging
from collections import defaultdict
from typing import List
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

    def __init__(self, name, runtime, loop, func, *args, **kwargs):
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

    def set_lights(self, lights, dict, *args, **kwargs):
        if not self.running:
            print(f"{self}: Can't set lights while not running")
            return
        ids = [l.light_id for l in lights]
        AnimationThread.manager.set_lights(ids, dict, *args, **kwargs)


class Animation:

    counter = defaultdict(int)

    def __init__(self, lights, duration=None, loop = None, name=None):
        self.lights = as_list(lights)
        self.duration = duration
        self.loop = loop
        self.name = name or self.default_name()
        self.silent = True
        self.anim_thread = None
        Animation.counter[self.__class__.__name__] += 1
                
    def __str__(self):
        return f"{self.name}"

    def default_name(self):
        return f"{self.__class__.__name__} {Animation.counter[self.__class__.__name__]}"

    # TODO: automatically override instance variables with kwargs
    def play(self, runtime=None, loop = False, blocking=True, silent = True, **kwargs):
        self.set_timing(runtime)
        if self.loop is None:
            self.loop = loop
        self.blocking = blocking
        self.silent = silent
        silent or self.print_info(False)

        if self.anim_thread:
            self.anim_thread.stop()
        self.anim_thread = AnimationThread(f'Thread: {self.name}', self.runtime, self.loop, self.animate)
        self.anim_thread.start(blocking, silent)

        return self

    def print_info(self, full=False):
        print(f'{self}, {self.runtime=}, {self.blocking=}')
        full and print(f'attributes: {self.__dict__}')

    def animate(self):
        logging.error(f"{self}: No animate() method defined")

    def stop(self):
        self.silent or print(f"Animation interrupted: {self}")
        self.anim_thread.stop()

    def set_timing(self, runtime):
        if runtime is None and self.duration is None:
            raise Exception(f"{self}: No animation timing specified")
        if runtime is None:
            runtime = self.duration
        if self.duration is None:
            self.duration = runtime
        self.runtime = runtime

    def set_lights(self, dict, *args, **kwargs):
        if self.anim_thread is None:
            raise Exception(f"{self}: No animation thread to set lights")
        self.anim_thread.set_lights(self.lights, dict, *args, **kwargs)

# a list of animations that play concurrently
class AGroup(Animation):
    def __init__(self, *animations: Animation, sequence=False, stagger = 0, **kwargs):
        self.animations = animations
        lights = set()
        for animation in animations:
            for light in animation.lights:
                lights.add(light)
        self.sequence = sequence
        self.stagger = stagger
        super().__init__(list(lights), **kwargs)

    def stop(self,):
        for animation in self.animations:
            animation.stop()
        super().stop()

    def animate(self):
        self.silent or print(f"{self}: animating {[str(a) for a in self.animations]}, {self.sequence=}")
        for animation in self.animations:
            if self.anim_thread.running:
                delay   = animation.duration if self.sequence else self.stagger
                runtime = animation.duration if self.sequence else self.duration
                animation.play(runtime, blocking=False, silent=self.silent)
                sleep(delay)
        if not self.sequence:
            sleep(self.duration)
        for animation in self.animations:
            animation.stop()
        
    def set_timing(self, runtime):
        if runtime is None:
            if any([animation.duration is None for animation in self.animations]):
                raise Exception(f"{self}: Runtime is not set, all animations must have a duration")
            op = sum if self.sequence else max
            runtime = op([animation.duration for animation in self.animations])
        super().set_timing(runtime)

        
class Wait(Animation):
    def __init__(self, runtime=0):
        super().__init__([], runtime)

    def animate(self):
        self.silent or print(f"{self}: Waiting {self.runtime} seconds")
        sleep(self.runtime)

class Fade(Animation):
    def __init__(self, lights, target, **kwargs):
        self.target = target
        super().__init__(lights, **kwargs)

    def animate(self):
        self.silent or print(f"{self}: Fading {[str(light) for light in self.lights]} to {self.target}")
        transitiontime = int(self.duration * 10)
        self.set_lights({"on": True, "hsb": self.target, "transitiontime": transitiontime})
        sleep(self.duration)


class FadeFrom(Fade):
    def __init__(self, lights, source, target, **kwargs):
        self.source = source
        super().__init__(lights, target, **kwargs)
        

    def animate(self):
        # snap to source color
        self.silent or print(f"{self}: Fading {[str(light) for light in self.lights]} from {self.source} to {self.target}")
        self.set_lights({"on": True, "hsb": self.source, "transitiontime": 0})
        # fade to target color
        super().animate()
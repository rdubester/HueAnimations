from collections import defaultdict
from copy import deepcopy
import itertools
import random
from threading import Thread, Timer
from time import sleep, time
from colors import *
from phue import Light

from utils import flatten, normalize

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
        self.silent or print(f"duration: {self.duration}", end=" ")
    
    def threaded(self, lights, **kwargs):
        thread = Thread(target=self.animate, args=(lights,), kwargs=kwargs)
        thread.start()
        return thread

    def stop(self):
        self.running = False

    def wait(self, time: float, steps: int = 100):
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

class Wait(Animation):
    def __init__(self, delay: float = None, **kwargs):
        super().__init__(**kwargs)
        self.delay = delay
    
    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        self.silent or print(f"{self.name}: waiting")
        if self.delay is not None:
            self.wait(self.delay)
        else: 
            self.wait(self.duration)

class FadeFromTo(Animation):
    def __init__(self, source: Color, target: Color, ratio: float = 0, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.target = target
        if 0 <= ratio <= 1:
            self.alpha = ratio
        else:
            raise ValueError(f"{self}: ratio must be between 0 and 1, was {ratio}")
    
    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        self.silent or print(f"{self}: {[str(light) for light in self.lights]} from {self.source} to {self.target}")
        t1 = self.duration * self.alpha
        t2 = self.duration - t1
        self.set_lights(self.lights, self.source, t1)
        self.set_lights(self.lights, self.target, t2)


class Fade(Animation):
    def __init__(self, target: Color, **kwargs):
        super().__init__(**kwargs)
        self.target = target
    
    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        self.silent or print(f"{self}: {[str(light) for light in self.lights]} to {self.target}")
        self.set_lights(self.lights, self.target, self.duration)


class Loop(Animation):
    def __init__(self, animation: Animation, max_iters: int = None, **kwargs):
        super().__init__(**kwargs)
        self.animation = animation
        self.max_iters = max_iters
        if self.max_iters is not None:
            self.duration = self.duration or float('inf')

    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        self.silent or print(f"{self}: {self.animation}")
        iters = 0
        starttime = time()
        while not (self.max_iters and iters >= self.max_iters):
            self.animation.animate(lights, **kwargs)
            iters += 1
            if time() - starttime > self.duration:
                break

class Strict(Animation):
    def __init__(self, animation: Animation, **kwargs):
        super().__init__(**kwargs)
        self.animation = animation
    
    def animate(self, lights, **kwargs):
        start = time()
        super().animate(lights, **kwargs)
        self.silent or print(f"{self}: {self.animation}")
        dur = self.duration - (time() - start)
        print(dur)
        self.timer = Timer(dur, self.stop)
        self.timer.start()
        self.animation.animate(lights, **kwargs)
        print(lights)
        print("elapsed: ", time() - start)
        self.timer.join()
        print("elapsed: ", time() - start)


class Sequence(Animation):
    def __init__(self, animations: list[Animation], **kwargs):
        super().__init__(**kwargs)
        self.animations = animations

    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        self.silent or print(f"{self}: {[str(animation) for animation in self.animations]}")
        for animation in self.animations:
            animation.animate(lights, **kwargs)
    
    def stop(self):
        super().stop()
        for animation in self.animations:
            animation.stop()

class RandomPool(Animation):
    def __init__(self, animations: list[Animation], weights: list[float] = None, **kwargs):
        super().__init__(**kwargs)
        self.animations = animations
        self.weights = normalize(weights or [1] * len(animations))

    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        self.silent or print(f"{self}: {[str(animation) for animation in self.animations]}")
        animation = random.choices(self.animations, weights=self.weights)[0]
        animation.animate(lights, **kwargs)

class Distribute(Animation):
    def __init__(self, animation: Animation, delay: float = 0, **kwargs):
        super().__init__(**kwargs)
        self.animation = animation
        self.delay = delay
    
    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        self.silent or print(f"{self}: {self.animation}")
        self.threads = []
        self.animations = []
        for idx, light in enumerate(lights):
            anim = deepcopy(self.animation)
            self.animations.append(anim)
            self.threads.append(anim.threaded([light], **kwargs))
            self.wait(self.delay)
        for thread in self.threads:
            thread.join()

    def stop(self):
        super().stop()
        self.animation.stop()
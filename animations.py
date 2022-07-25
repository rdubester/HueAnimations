import random
import threading
from time import sleep, time
import logging
from collections import defaultdict
from typing import Callable, List
from phue import Light
from colors import Color


class AnimationManager:
    def __init__(self):
        self.bridge = None

    def set_lights(self, lights, *args, **kwargs):
        if not self.bridge:
            raise Exception("Bridge not set")
        logging.info("Setting light:", args, kwargs)
        ids = [l.light_id for l in lights]
        self.bridge.set_light(ids, *args, **kwargs)


class AnimationThread():

    manager = AnimationManager()

    def __init__(self, name: str, runtime: float, loop: bool, func: Callable, *args, **kwargs):
        self.name = name
        self.runtime = runtime
        self.loop = loop
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.running = False
        self.thread = threading.Thread(target=self.run)
        self.timer = threading.Timer(self.runtime, self.stop)

    def __str__(self):
        return self.name

    def set_lights(self, lights: List[Light], command: dict, *args, **kwargs):
        if not self.running:
            print(f"{self}: Can't set lights while not running")
            return
        AnimationThread.manager.set_lights(lights, command, *args, **kwargs)

    def start(self, blocking, silent):
        self.thread.start()
        self.timer.start()
        if blocking:
            silent or print(f"{self}: Blocking")
            self.timer.join()

    def stop(self):
        self.timer.cancel()
        self.running = False
        self.thread.join()

    def run(self):
        self.running = True
        while self.running:
            self.func(*self.args, **self.kwargs)
            if not self.loop:
                break


# a list of animations that play concurrently
class AnimationGroup():

    counter = defaultdict(int)

    def __init__(self,
                animations = [],
                duration: float = None,
                loop: bool = True,
                name: str = None,
                silent: bool = True):
        self.animations = animations
        self.duration = duration
        self.loop = loop
        self.name = self.make_name(name)
        self.silent = silent
        self.anim_thread = None

    def __str__(self):
        return f"{self.name}"
    
    def sleep(self, seconds, increments=100):
        for i in range(0, increments):
            sleep(seconds / increments)
            if not self.running():
                return
        

    def make_name(self, name):
        class_name = self.__class__.__name__
        count = AnimationGroup.counter[class_name]
        AnimationGroup.counter[class_name] += 1
        name = " " + name if name else ''
        return f"{class_name}{name} {count}"

    # TODO: make a setter modify animation lights dyamically?
    def get_lights(self):
        lights = set()
        for animation in self.animations:
            lights.update(animation.lights)
        return lights

    def play(self, runtime = None, blocking = True, silent = True):
        self.runtime = runtime
        self.blocking = blocking
        self.silent = silent and self.silent
        self.calculate_timing()
        if self.anim_thread:
            self.anim_thread.stop()
        self.anim_thread = AnimationThread(f'Thread: {self.name}', self.runtime, self.loop, self.animate)
        self.anim_thread.start(blocking, self.silent)
        return self

    def calculate_timing(self):
        # apply runtime / duration laws
        if self.runtime is None and self.duration is None:
            raise Exception(f"{self}: No animation timing specified")
        self.runtime = self.runtime or self.duration
        self.duration = self.duration or self.runtime

    def running(self):
        return self.anim_thread and self.anim_thread.running

    def stop(self):
        self.silent or print(f"Animation interrupted: {self}")
        self.anim_thread.stop()
        for animation in self.animations:
            animation.stop()
    
    def set_lights(self, dict, *args, **kwargs):
        if self.anim_thread is None:
            raise Exception(f"{self}: No animation thread to set lights")
        self.anim_thread.set_lights(self.lights, dict, *args, **kwargs)
    
    def animate(self):
        raise Exception(f"{self}: No animation function specified")
            

class Parallel(AnimationGroup):
    def __init__(self, animations, stagger = 0, **kwargs):
        self.stagger = stagger
        super().__init__(animations, **kwargs)

    def calculate_timing(self):
        if self.animations and all(a.duration is not None for a in self.animations):
            self.duration = self.duration or max([animation.duration for animation in self.animations])
        super().calculate_timing()
    
    def animate(self):
        self.silent or print(f"{self}: Playing {[str(animation) for animation in self.animations]}")
        for animation in self.animations:
            animation.play(self.duration, blocking=False, silent=self.silent)
            self.sleep(self.stagger)
        

class Sequence(AnimationGroup):
    def calculate_timing(self):
        if self.duration is None:
            if self.animations and all(a.duration is not None for a in self.animations):
                self.duration = sum([animation.duration for animation in self.animations])
        super().calculate_timing()

    def animate(self):
        self.silent or print(f"{self}: Playing {[str(animation) for animation in self.animations]}")
        for animation in self.animations:
            animation.play(animation.duration, blocking=True, silent=self.silent)

class Stochastic(AnimationGroup):
    def __init__(self, animations, mean=0, sd=1, **kwargs):
        self.mean = mean
        self.sd = sd
        super().__init__(animations, **kwargs)
    
    def animate(self):
        # pick a random delay from the distribution
        delay = max(0, random.normalvariate(self.mean, self.sd))
        # play a random animation from the list that is not already running
        idle = [a for a in self.animations if not a.running()]
        if idle:
            animation = random.choice(idle)
            self.silent or print(f"{self}:  playing {str(animation)} for {delay} seconds")
            animation.play(blocking = True, silent = self.silent, runtime = delay)


class Animation(AnimationGroup):
    def __init__(self, lights = set(), **kwargs):
        self.lights = as_set(lights)
        super().__init__(**kwargs)

    def get_lights(self):
        return self.lights


class Wait(Animation):
    def animate(self):
        pass


class Fade(Animation):
    def __init__(self, lights, target, **kwargs):
        self.target = target
        super().__init__(lights = lights, **kwargs)

    def animate(self):
        self.silent or print(f"{self}: Fading {[str(light) for light in self.lights]} to {self.target}")
        transitiontime = int(self.duration * 10)
        self.set_lights({"on": True, "hsb": self.target, "transitiontime": transitiontime})
        self.sleep(self.duration)


class FadeFrom(Fade):
    def __init__(self, lights, source, target, **kwargs):
        self.source = source
        super().__init__(lights, target, **kwargs)
        
    def animate(self):
        # snap to source color
        self.silent or print(f"{self}: Setting {[str(light) for light in self.lights]} to {self.source}")
        self.set_lights({"on": True, "hsb": self.source, "transitiontime": 0})
        # fade to target color
        super().animate()


class Blink(Animation):
    def __init__(self, lights, target, smooth = False, **kwargs):
        self.target = target
        self.smooth = smooth
        super().__init__(lights = lights, **kwargs)

    def animate(self):
        self.silent or print(f"{self}: Blinking {[str(light) for light in self.lights]} to {self.target}")
        transitiontime = int(self.duration * 10)
        self.set_lights({"on": True, "hsb":self.target, "transitiontime": transitiontime})


class Wave(Parallel):
    def __init__(self, lights, colors, frequency, shape = None, alpha = 1, **kwargs):
        lights = set(lights)
        if not (0 < alpha <= 1):
            raise ValueError(f"{self}: Invalid alpha value: {alpha}")
        stagger = frequency * alpha / len(lights)
        animations = [ShapedFade(light, colors, shape, frequency) for light in lights]
        super().__init__(animations, stagger, **kwargs)


class Flicker(Parallel):
    def __init__(self, lights, colors, transition, mean, sd=1, **kwargs):
        self.colors = colors
        self.transition = transition
        self.mean = mean
        self.sd = sd
        animations = []
        for light in set(lights):
            s = Stochastic([Fade(light, color, duration=transition) for color in colors], mean, sd)
            animations.append(s)
        super().__init__(animations, loop=False, **kwargs)
                

class StochasticPool(Parallel):
    def __init__(self, lights, func, mean=1, sd=1, **kwargs):
        self.mean = mean
        self.sd = sd
        animations = []
        for light in set(lights):
            s = Stochastic(func(light), mean, sd)
            animations.append(s)
        super().__init__(animations, loop=False, **kwargs)


class ShapedFade(Sequence):
    def __init__(self, lights, colors, shape=None, duration = None, **kwargs):
        self.shape = shape or [1] * len(colors)
        duration = duration or sum(self.shape)
        if len(colors) != len(self.shape):
            raise Exception("Colors and shape must be the same length")
        
        self.weights = [x / sum(self.shape) for x in self.shape]
        self.times = [x * duration for x in self.weights]
        animations = [Fade(lights, color, duration = time) for color, time in zip(colors, self.times)]
        super().__init__(animations, **kwargs)


class Firework(ShapedFade):
    def __init__(self, lights, color, duration = None, initial_speed = 0, steps=10, **kwargs):
        brightness_vals = [1 - easeOutExpo(x/steps) for x in range(steps)]
        brightness_vals = [int(x * 254) for x in brightness_vals]
        colors = [Color(color.hue, brightness=int(b)) for b in brightness_vals]
        shape = [1] * len(brightness_vals)
        shape[0] = initial_speed
        return super().__init__(lights, colors, shape=shape, duration=duration)

def as_set(x):
    if isinstance(x, set):
        return x
    if isinstance(x, list):
        return set(x)
    return {x}

def thunk(constructor, *args, **kwargs):
    def inner(lights):
        return constructor(lights, *args, **kwargs)
    return inner

def easeOutExpo(x):
    return 1 if x == 1 else 1 - pow(2, -10 * x)

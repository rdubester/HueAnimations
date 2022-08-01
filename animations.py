from copy import deepcopy
from re import M
from time import time
import random

from animation_base import Animation
from colors import *
from utils import *


class Wait(Animation):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        self.wait(self.duration)


class Fade(Animation):
    def __init__(self, target: Color, **kwargs):
        super().__init__(**kwargs)
        self.target = target

    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        self.set_lights(self.lights, self.target, self.duration)

    def log(self):
        super().log(f"to {self.target}")


class FadeFromTo(Animation):
    def __init__(self, source: Color, target: Color, ratio: float = 0, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.target = target
        if 0 <= ratio <= 1:
            self.ratio = ratio
        else:
            raise ValueError(f"{self}: ratio must be between 0 and 1, was {ratio}")

    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        t1 = self.duration * self.ratio
        t2 = self.duration - t1
        self.set_lights(self.lights, self.source, t1)
        self.set_lights(self.lights, self.target, t2)

    def log(self):
        super().log(f"from {self.source} to {self.target}, {self.ratio=}")


class Loop(Animation):
    def __init__(self, animation: Animation, max_iters: int = None, **kwargs):
        super().__init__(**kwargs)
        self.animation = animation
        self.max_iters = max_iters
        if self.max_iters is not None:
            self.duration = self.duration or float("inf")

    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        iters = 0
        starttime = time()
        while not (self.max_iters and iters >= self.max_iters):
            self.animation.animate(lights, **kwargs)
            iters += 1
            if time() - starttime > self.duration:
                break

    def log(self):
        super().log(f"{self.animation}, {self.max_iters=}")


class Sequence(Animation):
    def __init__(self, animations: list[Animation], **kwargs):
        super().__init__(**kwargs)
        self.animations = animations

    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        for animation in self.animations:
            animation.animate(lights, **kwargs)

    def log(self):
        super().log(strvals(self.animations))


class RandomPool(Animation):
    def __init__(
        self, animations: list[Animation], weights: list[float] = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.animations = animations
        self.weights = normalize(weights or [1] * len(animations))

    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        animation = random.choices(self.animations, weights=self.weights)[0]
        animation.animate(lights, **kwargs)

    def log(self):
        super().log(f"{strvals(self.animations)}, {self.weights=}")


class Map(Animation):
    def __init__(self, animations: list[Animation], delay: float = 0, **kwargs):
        super().__init__(**kwargs)
        self.animations = animations
        self.delay = delay

    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        self.threads = []
        for anim, light in zip(self.animations, lights):
            self.threads.append(anim.threaded([light], **kwargs))
            self.wait(self.delay)
        for thread in self.threads:
            thread.join()

    def log(self):
        super().log(f"{strvals(self.animations)}, {self.delay=}")


class Distribute(Map):
    def __init__(self, animation: Animation, delay: float = 0, **kwargs):
        super().__init__([animation], delay, **kwargs)

    def animate(self, lights, **kwargs):
        anim = self.animations[0]
        self.animations = [deepcopy(anim) for _ in lights]
        super().animate(lights, **kwargs)


class Swirl(Animation):
    def __init__(self, colors: list[Color], freq: float, max_iters = None, **kwargs):
        super().__init__(**kwargs)
        self.colors = colors
        self.freq = freq
        self.max_iters = max_iters

    def animate(self, lights, **kwargs):
        num_colors = len(self.colors)
        fade_duration = self.freq / num_colors
        fades = [Fade(color, duration=fade_duration) for color in self.colors]
        anims = []
        for i in range(num_colors):
            rotated = fades[-i:] + fades[:-i]
            anims.append(Sequence(rotated, name=f"swirl: {i}"))
        Loop(Map(anims), self.max_iters).animate(lights, **kwargs)

    def log(self):
        super().log(f"{strvals(self.colors)}, {self.freq=}")


class ShapedSequence(Animation):
    def __init__(self, animations: list[Animation], weights: list[float] = None, **kwargs):
        super().__init__(animations, **kwargs)
        self.weights = normalize(weights or [1] * len(animations))
        if len(self.weights) != len(animations):
            raise ValueError(f"{self}: animations and weights must be the same length")
    
    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        for animation, weight in zip(self.animations, self.weights):
            animation.animate(lights, speed = weight, **kwargs)

    def log(self):
        super().log(strvals(self.animations))

class ShapedFade(Animation):
    def __init__(self, colors: list[Color], weights: list[float], **kwargs):
        super().__init__(**kwargs)
        self.colors = colors
        self.weights = normalize(weights or [1] * len(colors))
        if len(self.weights) != len(self.colors):
            raise ValueError(f"{self}: weights must be the same length as colors")
    
    def animate(self, lights, **kwargs):
        super().animate(lights, **kwargs)
        fades = []
        for color, weight in zip(self.colors, self.weights):
            fades.append(Fade(color, self.duration * weight))
        Sequence(fades).animate(lights, **kwargs)
        
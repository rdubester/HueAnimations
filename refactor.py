import math
from collections import defaultdict
import random
import threading
from time import sleep
from typing import Callable, List
from phue import Light
from colors import *


class AnimationThread():
    def __init__(self, animation, runtime):
        self.animation = animation
        self.runtime = runtime
        self.running = False
        self.thread = threading.Thread(target=self.run)
        self.timer = threading.Timer(self.runtime, self.stop)

    def start(self):
        self.thread.start()
        self.timer.start()
        if self.blocking:
            self.silent or print(f"{self}: Blocking")
            self.timer.join()

    def stop(self):
        self.timer.cancel()
        self.running = False
        self.thread.join()

    def run(self):
        self.running = True
        self.func(*self.args, **self.kwargs)
    
    def wait(self, time, steps=100):
        for _ in range(steps):
            if not self.running:
                return
            sleep(time / steps)

bridge = None
def set_lights(lights, command):
    if not bridge:
        raise Exception("No bridge set")
    ids = [l.light_id for l in lights]
    bridge.set_light(ids, command)

def validate_weights(animations: List[Callable], weights: List[float]):
    if weights is None:
        weights = [1] * len(animations)
    if len(weights) != len(animations):
        raise Exception("Weights must have same length as animations")
    return weights

def wait(duration: float):
    def animate(lights):
        wait(duration)
    return animate

def fade(target: Color, duration: float = None):
    def animate(lights):
        transitiontime = int(duration * 10)
        set_lights(lights, {"on": True, "hsb": target, "transitiontime": transitiontime})
        wait(duration)()
    return animate
    
def sequence(*animations: Callable, weights: List[float] = None, duration: float = None):
    weights = validate_weights(animations, weights)
    weights = [w / sum(weights) for w in weights] 
    def animate(lights):
        for animation, weight in zip(animations, weights):
            animation(lights, duration * weight)
    return animate

def times(animation: Callable, N: int, duration: float = None):
    def animate(lights):
        for _ in range(N):
            animation(lights, duration / N)
    return animate

def pool(*animations: Callable, weights: List[float] = None, duration: int = None):
    weights = validate_weights(animations, weights)
    def animate(lights):
        animation = random.choices(animations, weights, k=1)
        animation[0](lights, duration)
    return animate
            
def functionWeights(func: Callable, animation_producer: Callable):
    def producer(animations, *args, **kwargs):
        weights = [func(idx) for idx in range(len(animations))]
        return animation_producer(animations, *args, weights=weights, **kwargs)
    return producer

def WeightedFade(colors: List[Color], weights: List[float] = None):
    fades = [fade(c) for c in colors]
    return sequence(fades, weights)

def firework(colors: List[Color], c = 1, alpha = 0.5):
    return functionWeights(expdecay(c, alpha), WeightedFade)(colors)

def expdecay(c, alpha):
    return lambda i: c * math.e ** (-alpha * i)

def play(animation: Callable, lights: List[Light], runtime: float = None, mode: str = "sync"):
    if runtime is None:
        runtime = 10e6
    match mode:
        case "sync":
            thread = AnimationThread(animation, lights, runtime)
            thread.start()
            return thread
        case "async":
            threads = []
            for light in lights:
                thread = AnimationThread(animation, light, runtime)
                thread.start()
                threads.append(thread)
            return threads
        case _:
            raise Exception(f"Unknown mode: {mode}")

lights = None
firework_colors = [
    [white, yellow, orange, red, blue],
    [white, red, violet, blue],
    [white, green, teal, blue],
]

bluePulse = sequence(fade(blue), fade(darkblue))
fireworks = pool(firework(colors) for colors in firework_colors)
mix = pool(bluePulse, fireworks, weights = [5,1])
threads = play(mix, lights, mode='independent')
import math
import numpy as np
from setup import *
from colors import *
import threading

lights = [round_light, table_light, square_light]
runtime = 300000
c1 =  RED * (1 - 0.6) + ORANGE * 0.6
c2 = RED
c3 = VIOLET  * (1 - 0.9) + MAX_HUE * 0.9
print(c1, c2, c3)
colors = [
    Color(c1, saturation=254, brightness=200),
    Color(c1 * 0.8, saturation=254, brightness=200),
    Color(c2, brightness = 160),
    Color(c3, brightness = 160)]

# frequency = 8
# shape = [1.8,6,3.8, 2.4]
# wait = 2
# group = Wave(lights, colors, frequency, shape)
# group.play(runtime=300000)

# colors = [green, teal, blue, violet, red]
# frequency = 8
# shape = [2,1,1,1,1]
# group = Wave(colors, frequency, shape, bedroom_lights, stagger=None)
# group.play(runtime=300000)


# co/xlors = [Color(c, brightness=254) for c in [TEAL, BLUE, VIOLET]]
# colors = [Color(c, brightness=254) for c in [ORANGE, TEAL, BLUE]]
colors = [Color(c, brightness=254) for c in [BLUE, VIOLET, BLUE]]
shape = [2,3,4]
# colors = [ 
#     Color((BLUE+VIOLET) / 2, brightness=120),
#     Color(BLUE, brightness=150),
#     Color((BLUE + TEAL) / 2, brightness=120),
#     Color(BLUE, brightness=150)]
    #   Color(ORANGE, brightness=160),
          
shape = [1,1,1]
frequency = 10
wave = Wave(bedroom_lights, colors, frequency, shape, alpha=0.2)
wave.play(runtime=300000, blocking=False)

# while(True):
#     print("Active Threads: ", threading.active_count())
#     for thread in threading.enumerate():
#         print(thread.name)
#     sleep(5)


# anim = Parallel(
#     [Stochastic([Fade(light, color, loop=False, duration=0.5) for color in rainbow], mean=2, sd=1)
#     for light in lights], loop=False)
# flicker = Flicker(lights, rainbow, 0.8, 3)
# flicker.play(runtime=300000, blocking=False)

# def StochasticPool(func, lights, mean, sd, **kwargs):
#     animations = []
#     for light in lights:
#         s = Stochastic(func(light), mean, sd, **kwargs)
#         animations.append(s)
#     return Parallel(animations, loop=False)

# def firework_(colors, duration, initial_speed, steps):
#     def inner(lights):
#         return [Firework(lights, color, duration, initial_speed, steps) for color in colors]
#     return inner

# def distribute(func, lights, **kwargs):
#     animations = []
#     for light in lights:
#         animations.append(func(light, **kwargs))
#     return Parallel(animations, **kwargs)

# def fireworks(colors, duration, initial_speed, steps):
#     def inner(light):
#         return [Firework(light, color, duration, initial_speed, steps) for color in colors]
#     return inner


# fireworks = [Firework(light, c, 8, initial_speed=0.4) for light in lights for c in rainbow]
# anim = StochasticPool(thunk(Firework, ), lights, mean=2, sd=1)
# anim = Parallel(fireworks, lights, mean=2, sd=1)
# anim.play(runtime=300000, blocking=False)

# anim = Stochastic(fireworks, mean=3, sd=1)
# anim.play(runtime=300000, blocking=False)

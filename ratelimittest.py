from setup import *
from colors import *
import threading


while True:
        for color in rainbow:
            bridge.set_light([light.light_id for light in bedroom_lights], {'hsb': color, 'transitiontime': 0})
            sleep(0.0)
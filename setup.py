from animations import *
from phue import Bridge
import logging
import sys

LEFT_RIGHT = [3, 1, 2]
bridge = Bridge('10.0.0.51')
AnimationThread.manager.bridge = bridge

def get_bedroom_lights(order=LEFT_RIGHT):
    lights = bridge.get_light_objects('id')
    return list(map(lambda x: lights[x], order))

bedroom_lights = get_bedroom_lights()
round_light, table_light, square_light = bedroom_lights
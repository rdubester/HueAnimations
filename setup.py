# from animations import *
from phue import Bridge
from UpdateManager import LightUpdateManager
from animation_base import Animation

bridge = Bridge('10.0.0.51')
updateManager = LightUpdateManager(bridge)
Animation.updateManager = updateManager

all_lights = bridge.get_light_objects('id')
for key, value in all_lights.items():
    print(key, value.name)

table_lamp = all_lights[1]
square_lamp = all_lights[2]
round_lamp = all_lights[3]
tri_mid = all_lights[4]
tri_bottom = all_lights[5]
tri_top = all_lights[6]
small_lamp = all_lights[7]

tri_lamp = [tri_bottom, tri_mid, tri_top]
bedroom_lights = [round_lamp, table_lamp, square_lamp]
living_room_lights = [small_lamp, tri_lamp]

test_group = [tri_lamp, round_lamp, small_lamp, square_lamp]


# AnimationThread.manager.bridge = bridg

# def get_bedroom_lights(order=BEDROOM_LEFT_RIGHT):
#     lights = bridge.get_light_objects('id')
#     return list(map(lambda x: lights[x], order))

# def get_living_room_lights(order=LIVINGROOM_LEFT_RIGHT):
#     lights = bridge.get_light_objects('id')
#     return list(map(lambda x: lights[x], order))

# bedroom_lights = get_bedroom_lights()
# lights = bedroom_lights
# round_light, table_light, square_light = bedroom_lights
from setup import *
from colors import *
import threading

def wave(lights, runtime, colors, frequency, shape=None, wait = None):
    interval = frequency /  len(colors)
    if shape is None:
        shape = [1] * len(colors)
    if wait is None:
        wait = len(colors)/len(bedroom_lights) * frequency

    weights = [x * len(colors) / sum(shape) for x in shape]
    if len(colors) != len(shape):
        raise Exception("Colors and shape must be the same length")

    print(weights)

    if shape is None:
        shape = [1/len(colors) for _ in range(len(colors))]

    anims = []
    for light in lights:
        g = AGroup(
            *[Fade(light, color, duration = interval * weight) for color, weight in zip(colors, weights)],
            sequence=True, loop=True
        )
        anims.append(g)
    g = AGroup(*anims, sequence=False, stagger = wait, loop=True)
    g.play(runtime=runtime, loop=True, blocking=False)
    return g
    #     )
    # groups = []
    # for light in lights:
    #     g = AGroup(
    #         *[Fade(light, color, duration = interval * weight) for color, weight in zip(colors, weights)],
    #         stagger=wait
    #     ).play(runtime = runtime, sequence = True, loop=True, blocking=False)
    #     groups.append(g)
    #     # sleep(wait)
    # return groups

groups = globals().get('groups', [])
for group in groups:
    group.stop()
groups.clear()

for thread in threading.enumerate(): 
    print(thread.name)

lights = [round_light, table_light, square_light]
runtime = 300000
# colors = [Color(ORANGE, saturation=128), red, Color(VIOLET, brightness=150), darkblue]
# shape = [1,2.5,1.4, 0.8]
c1 =  RED * (1 - 0.6) + ORANGE * 0.6
c2 = RED
c3 = VIOLET  * (1 - 0.9) + MAX_HUE * 0.9
print(c1, c2, c3)
colors = [
    Color(c1, saturation=254, brightness=200),
    Color(0.8 * c1, saturation=254, brightness=200),
    Color(RED, brightness = 160),
    Color(c3, brightness = 160)]
    #, Color(SANGRIA, brightness=80)]
shape = [1.8,6,3.8, 2.4]
frequency = 8
# wait = 0.15
wait = 0.5
# wait = golden = (1 + 5 ** 0.5) / 2
frequency = 6


# groups = wave(lights, runtime, colors, frequency, shape, wait)
group = wave(bedroom_lights, runtime, colors, frequency, shape, wait)
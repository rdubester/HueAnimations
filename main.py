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
# group = Wave(colors, frequency, shape, lights, stagger=wait)
# group.play(runtime=300000)s

# colors = [green, teal, blue, violet, red]
# frequency = 8
# shape = [2,1,1,1,1]
# group = Wave(colors, frequency, shape, bedroom_lights, stagger=None)
# group.play(runtime=300000)


colors = [Color(c, brightness=128) for c in [TEAL, BLUE, VIOLET]]
frequency = 8
shape = [1,1,1]
group = Wave(colors, frequency, shape, bedroom_lights, stagger= 8 / 3)
group.play(runtime=300000)
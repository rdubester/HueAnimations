from setup import *
from colors import *
from animations import *
import cProfile

# for light, color in zip(lights, [red, green, blue]):
#     Loop(
#         FadeFromTo(yellow, color, duration=3), max_iters=10
#     ).threaded(light)

# def firework(color):
#     return Sequence([
#         FadeFromTo(white, color, ratio = 0.2, duration=1),
#         Fade(Color(color.hue, brightness=0), duration = 4)], name = f"firework: {color}")
# fireworks = [firework(color) for color in rainbow]
# fireworkPool = RandomPool(fireworks, name = "fireworkPool")
# fill = Wait(duration=3)
# pool = RandomPool([fireworkPool, fill], weights=[1, 5])
# Distribute(Loop(pool)).animate(lights, duration=100)

def lavalamp(duration):
    speed = 2

    bgs = RandomPool(
        [FadeFromTo(set_brightness(red, 60), set_brightness(red, 100), ratio = r, duration = speed * d)
            for r in [0.2, 0.4, 0.6, 0.8, 1]
            for d in [1, 2, 3, 4, 5]])

    redShades = [set_brightness(red, int(254 * 1 / i)) for i in range(3, 6)]
    orangeShades = [set_brightness(orange, int(254 * 1 / i)) for i in range(3, 6)]
    purpleShades = [set_brightness(violet, int(254 * 1 / i)) for i in range(3, 6)]
    shades = redShades + orangeShades + purpleShades

    lavas = RandomPool([FadeFromTo(c1, c2, ratio = r, duration = speed * d) 
        for c1 in shades 
        for c2 in shades 
        for r in [0.2, 0.4, 0.6, 0.8]
        for d in range(1, 6)])

    anim = RandomPool([lavas, bgs], weights=[5, 5])
    Distribute(Loop(anim)).animate(test_group, duration=duration)

def dancing():
    Animation.global_brightness = 0.7
    dur = 20
    while True:
        n = random.randint(0, 6)
        match n:
            case 0: lavalamp(dur)
            #case 1: swirl(rainbow, 30, dur)
            #case 2: swirl([green, teal, blue], 20, dur)
            case 2: swirl([orange, red, violet], 20, dur)
            case 3: swirl([orange, red, violet], 20, dur)
            case 4: Fade(red).animate(test_group, duration=dur/2)
            case 1: Fade(red).animate(test_group, duration=dur/2)
            case 5: Fade(orange).animate(test_group, duration=dur/2)
            case 6: Fade(violet).animate(test_group, duration=dur/2)
            ##case 7: Fade(green).animate(test_group, duration=dur/2)
            # case 8: Fade(teal).animate(test_group, duration=dur/2)
            # case 9: Fade(blue).animate(test_group, duration=dur/2)

# swirl(rainbow, 10, 2000)

def swirl1():
    Animation.global_brightness = 1
    lamps = [tri_top, round_lamp, small_lamp, square_lamp]
    colors = [red, violet, blue, green]
    # shape = [1,2,3,4]
    shape = None
    Swirl(colors, freq=8, weights=shape).animate(lamps, duration=2000)

def swirl2():
    Animation.global_brightness = 1
    colors = [blue, violet, red,  violet]
    shape = [3,2,1,1]
    return Swirl(colors, freq=4, weights=shape)

# swirl2()
# Fade(orange).animate(test_group, duration=10)
# cProfile.run('MultiFade(rainbow).animate(test_group, duration = 4)', sort='tottime')
# s = swirl2()
# lamps = [tri_lamp, round_lamp, small_lamp, square_lamp]
# cProfile.run('s.animate(lamps, duration=10)', sort='tottime')
swirl1()

# f = Fade(orange)
# # start = time()
# cProfile.run('f.animate(test_group, duration=3)')
# print(time() - start)

updateManager.stop()
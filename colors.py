class Color():

    def __init__(self, hue, saturation=254, brightness=254, name=None):
        if not (0 <= hue <= MAX_HUE):
            raise ValueError("hue must be in [0,65535]")
        if not (0 <= saturation <= 254):
            raise ValueError("saturation must be in [0,254]")
        if not (0 <= brightness <= 254):
            raise ValueError("brightness must be in [0,254]")

        self.hue = int(hue)
        self.saturation = int(saturation)
        self.brightness = int(brightness)
        self.name = name

    def __str__(self):
        return self.name or f"{self.hue}:{self.saturation}:{self.brightness}"


def lerp(start, end, t):
    h = (start.hue + (end.hue - start.hue) * t) % MAX_HUE
    s = (start.saturation + (end.saturation - start.saturation) * t) % MAX_SATURATION
    b = (start.brightness + (end.brightness - start.brightness) * t) % MAX_BRIGHTNESS
    return Color(h, s, b)


MAX_HUE = 65535
MAX_SATURATION = 254
MAX_BRIGHTNESS = 254

RAINBOW = [MAX_HUE * (x / 6) for x in range(6)]
RED, YELLOW, GREEN, TEAL, BLUE, VIOLET = RAINBOW
ORANGE = (RED + YELLOW) / 2
SANGRIA = VIOLET + RED / 2

def set_hue(color, hue):
    return Color(hue, color.saturation, color.brightness, color.name)

def set_saturation(color, saturation):
    return Color(color.hue, saturation, color.brightness, color.name)

def set_brightness(color, brightness):
    return Color(color.hue, color.saturation, brightness, color.name)


red = Color(RED, name='red')
orange = Color(ORANGE, name='orange')
yellow = Color(YELLOW, name='yellow')
green = Color(GREEN, name='green')
teal = Color(TEAL, name='teal')
blue = Color(BLUE, name='blue')
violet = Color(VIOLET, name='violet')

sangria = Color(SANGRIA, name='sangria')
rainbow = [violet, red, orange, yellow, green, teal, blue]

darkblue = Color(BLUE, brightness=128, name='darkblue')
darkpurple = Color(VIOLET, brightness=128, name='darkpurple')
white = Color(MAX_HUE, 0, MAX_BRIGHTNESS, name='white')
black = Color(0, 0, 0, name = 'black')
from threading import Thread, Timer
from typing import List


class AnimationManager:
    def __init__(self):
        self.bridge = None

    def set_lights(self, lights, *args, **kwargs):
        if not self.bridge:
            raise Exception("Bridge not set")
        ids = [l.light_id for l in lights]
        self.bridge.set_light(ids, *args, **kwargs)


class AnimationThread():

    manager = AnimationManager()

    def __init__(self, runtime, loop, func, *args, **kwargs):
        self.runtime = runtime
        self.loop = loop
        self.func = func
        self.args = args
        self.kwargs = kwargs

        self.thread = Thread(target=self.run)
        self.timer = Timer(self.runtime, self.stop)

    def run(self):
        while self.running:
            self.func(self.callback, *self.args, **self.kwargs)
            if not self.loop:
                break

    def start(self, blocking=False):
        self.running = True
        self.timer.start()
        self.thread.start()
        if blocking:
            self.timer.join()
    
    def stop(self):
        self.running = False

    def interrupt(self):
        self.timer.cancel()
        self.stop()

    def callback(self, *args, **kwargs):
        if not self.running:
            print(f"{self}: Can't set lights while not running")
            return
        AnimationThread.manager.set_lights(*args, **kwargs)

class AnimationThreadPool():
    def __init__(self, threads: List[AnimationThread]):
        self.threads = threads

    def start(self, sequence, blocking=False):
        for thread in self.threads:
            thread.start(sequence)
        if blocking:
            for thread in self.threads:
                thread.join()

    def stop(self):
        for thread in self.threads:
            thread.stop()

    def interrupt(self):
        for thread in self.threads:
            thread.interrupt()

class Animation():

    def play(self, runtime, loop, blocking, *args, **kwargs):
        thread = AnimationThread(runtime, loop, self.animate, *args, **kwargs)
        thread.start(blocking=blocking)
        return thread

    def animate(self, callback, *args, **kwargs):
        raise NotImplementedError()


class AGroup(Animation):

    def __init__(self, animations: List[Animation]):
        self.animations = animations

    def play(self, runtime, loop, blocking, sequence, *args, **kwargs):
        thread = AnimationThreadPool(
            [AnimationThread(runtime, loop, animation.animate, *args, **kwargs) for animation in self.animations])
        thread.start(blocking=sequence)
        return thread
        

    def animate(self, callback, *args, **kwargs):
        for animation in self.animations:
            animation.play()
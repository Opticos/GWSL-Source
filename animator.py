"""
import sys
import pygame as pg
import pygame.gfxdraw
"""


class animation:
    def __init__(self, pos, identifier):
        self.pos = pos
        self.new_pos = pos
        self.id = identifier
        self.vel = []

    def get(self):
        pos = [round(self.pos[0]), round(self.pos[1])]
        return self.pos

    def update(self, func, clock):
        axes = len(self.pos)
        vel = []
        bounce = 0
        FPS = clock.get_fps()
        scale = (FPS / 60.0) * 2.0

        if scale <= 0.2:
            scale = 3

        for axis in range(axes):
            vel.append(0)
            if self.pos[axis] != self.new_pos[axis]:
                if func == "ease":
                    if self.pos[axis] < self.new_pos[axis] - (((self.new_pos[axis] - self.pos[axis]) / (2 * scale))):
                        vel[axis] = (self.new_pos[axis] - self.pos[axis]) / (2 * scale)

                    elif self.pos[axis] > self.new_pos[axis] + (((self.pos[axis] - self.new_pos[axis]) / (2 * scale))):
                        vel[axis] = -1 * (self.pos[axis] - self.new_pos[axis]) / (2 * scale)
                elif func == "old":
                    if self.pos[axis] < self.new_pos[axis]:
                        vel[axis] = 1 * scale

                    elif self.pos[axis] > self.new_pos[axis]:
                        vel[axis] = -1 * scale

                elif func == "pop":
                    self.pos[axis] = self.new_pos[axis]

                self.vel = vel
                self.pos[axis] += vel[axis]
                if self.pos[axis] < 0:
                    self.pos[axis] = 0
                diff = self.new_pos[axis] - self.pos[axis]
                if diff < 0:
                    diff *= -1
                if diff < 1:
                    self.pos[axis] = self.new_pos[axis]
                    # self.vel[axis] = 0

            # bounce
            """
            if self.get()[axis] == self.new_pos[axis]:
                self.new_pos[axis] = self.pos[axis]
                self.pos[axis] += 10"""

    def animate(self, new_pos):
        self.new_pos = new_pos

    def pop(self, new_pos):
        self.new_pos = new_pos
        self.pos = new_pos


class animator:
    def __init__(self, fpsClock):
        self.animations = set()
        self.func = "ease"
        self.clock = fpsClock

    def register(self, identifier, init_pos):
        animation_object = animation(init_pos, identifier)
        self.animations.add(animation_object)

    def update(self):
        for anim in self.animations:
            anim.update(self.func, self.clock)

    def animate(self, identifier, new_pos):
        for anim in self.animations:
            if anim.id == identifier:
                return anim.animate(new_pos)

    def get(self, identifier):
        for anim in self.animations:
            if anim.id == identifier:
                return anim.get()

    def pop(self, identifier, new_pos):
        for anim in self.animations:
            if anim.id == identifier:
                return anim.pop(new_pos)

    def set_func(self, anim_type):
        self.func = anim_type


"""
FPS = 60
fpsClock = pg.time.Clock()

canvas = pg.display.set_mode([500, 500])

ma = animator(fpsClock)

ma.register("test", [100, 100])
pg.font.init()
eras = pg.font.Font("assets/fonts/osl.ttf", 20)
new_pos = [0, 0]

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            new_pos = event.pos
            ma.animate("test", list(event.pos))

    canvas.fill([255, 255, 255])
    poser = ma.get("test")
    pg.draw.circle(canvas, [int((poser[0]/ 500) * 255), int((poser[0]/ 500) * 255), int((poser[1]/ 500) * 255)], poser, 20)
    #pg.gfxdraw.circle(canvas, int(poser[0]), int(poser[1]), 20, [255, 0, 0])
    pos = eras.render(str(new_pos) + " " + str(poser), True, [0, 0, 0])
    #canvas.blit(pos, poser)
    ma.update()
    fpsClock.tick(FPS)
    pg.display.update()
   
"""

import pygame
import sys
import blur

pygame.init()

canvas = pygame.display.set_mode([400, 400], pygame.NOFRAME)

HWND = pygame.display.get_wm_info()["window"]

blur.blur(HWND)

while True:
    pygame.display.update()
    canvas.fill([0, 0, 0])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen = pygame.Surface([400, 400])

    # pygame.display.

    pygame.draw.circle(screen, [255, 0, 0], [100, 100], 50)

    canvas.blit(screen, [0, 0], special_flags=(pygame.BLEND_RGBA_ADD))


import pygame
from Tile import Tile

pygame.init()


t = Tile(23)
t.image


screen = pygame.display.set_mode((500, 500))

image = pygame.image.load(t.image)
meeple = pygame.image.load('meeple_images/blue.png')

merged = image.copy()

merged.blit(meeple, (0,0))


while True:  
    screen.fill(pygame.color.Color('white'))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    screen.blit(merged, (0, 0))
    pygame.display.flip()
import pygame
import sys

pygame.init()
# Ecran de 1080x1920 (portrait)
screen = pygame.display.set_mode((1080, 1920))
screen.fill((0, 0, 0))

pygame.draw.circle(screen, (255, 0, 0), (540, 960), 40)  # Cercle rouge au centre
pygame.draw.rect(screen, (0, 255, 0), (100, 100, 200, 100))  # Rectangle vert

pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()

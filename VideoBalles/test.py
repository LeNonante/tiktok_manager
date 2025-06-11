import pygame
import sys
import os
import numpy as np

from assets.image_to_video import create_video_from_images
from assets.classes import Balle


total_frame=60*61
vitesse_max = 10.0
centre=0

# Empêche  mise à l'échelle DPI automatique
os.environ['SDL_VIDEO_ALLOW_HIGHDPI'] = '0'  
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'  # Centrer la fenêtre

pygame.init()

#Calcul taille fenetre
info = pygame.display.Info()
screen_width, screen_height= info.current_w, info.current_h
ratio = 9 / 16

width = int(screen_height * ratio)
height = screen_height

centre=np.array([width//2,height//2]).astype(float) #Permet d'avoir la position du centre de l'écran





# Ecran de en 16/9 (portrait)




# Boucle principale pour dessiner et capturer chaque frame
balle = Balle(width // 2, height // 2, 20, (255, 0, 0))

for frame in range(total_frame):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))
    balle.update_position()
    balle.draw(screen)

    #Cercle blanc
    pygame.draw.circle(screen, (255, 255, 255), (width // 2, height // 2), 200, width=3)

    pygame.display.flip()

    # Capture d'écran de la fenêtre pygame à chaque frame
    screenshot = pygame.Surface((width, height))
    screenshot.blit(screen, (0, 0))
    pygame.image.save(screenshot, f"VideoBalles/assets/screen/capture_ecran_{frame:04d}.png")

pygame.quit()
sys.exit()

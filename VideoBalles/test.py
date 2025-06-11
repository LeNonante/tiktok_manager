import pygame
import sys
import os
import numpy as np

from assets.image_to_video import create_video_from_images
from assets.classes import Balle
from assets.classes import Partie


total_frame=60*61
vitesse_max = 10.0


# Empêche  mise à l'échelle DPI automatique
os.environ['SDL_VIDEO_ALLOW_HIGHDPI'] = '0'  
os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'  # Centrer la fenêtre

pygame.init()

#Calcul taille fenetre, centre, etc
info = pygame.display.Info()
screen_width, screen_height= info.current_w, info.current_h
ratio = 9 / 16

width = int(screen_height * ratio)
height = screen_height

centre=np.array([width//2,height//2]).astype(float) #Permet d'avoir la position du centre de l'écran

#Création de la fenêtre
partie = Partie(width, height, bg=(0, 0, 0), vitesse_max_balle=vitesse_max)

#Ajout des balles
partie.addBalle(width // 2, height // 2, 20, (255, 0, 0))

#Boucle des frames
print("Création des images :")
for frame in range(total_frame):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    partie.setPartie(centre)
    partie.Afficher()

    screen = partie.makeScreenshot(frame)


pygame.quit()
print("Création de la vidéo : ")
create_video_from_images("VideoBalles/assets/screen", "VideoBalles/resultat.mp4")

sys.exit()


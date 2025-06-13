import pygame
import sys
import os
import numpy as np
import pygame.midi
from collections import deque
from assets.image_to_video import create_video_from_images
from assets.classes import Balle
from assets.classes import Partie
from assets.classes import MidiController
from random import randint
import mido

#A faire :
# - Randomiser départ balle
# - enlever rotation arc de partie et le mettre dans arc
# - passer les arcs en full class

total_frame=60*61
vitesse_max = 10.0
fichier_midi = "VideoBalles/assets/midi/Eiffel_65_I_m_Blue.mid" #chemin vide si pas de musique
fond_fenetre = (0, 0, 0)  # Couleur de fond de la fenêtre
rayon_min_arc = 100
reduction_arc=0.1



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

#Chargement de la musique si le fichier existe
if fichier_midi!="":
    midi_controller = MidiController(fichier_midi)  

#Création de la fenêtre
partie = Partie(width, height, fond_fenetre, vitesse_max, 0.2, reduction_arc, rayon_min_arc)




#PARTIE AJUSTABLE ---------------------------------------------------------------------------------------

#Ajout des balles



couleur_balle = (255, 0, 0)  # Couleur des balles
rayon_balle = 20  # Taille des balles
couleur_interieur_balle = (0, 0, 0)  # Couleur intérieure des balles
taille_contour = 5  # Taille du contour des balles
taille_trainee = 10  # Taille de la traînée des balles

partie.addBalle(width // 2, height // 2, rayon_balle, couleur_balle, taille_trainee, couleur_interieur_balle, taille_contour) #





for i in range (1000) :
    angle2 = randint(0, 360)
    angle=(angle2+60)%360
    partie.addArc((width // 2, height // 2), 200 + i*16, angle, angle2 , (255, 255, 255))

#Boucle des frames
print("Création des images :")
for frame in range(total_frame):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    isRebond=partie.setPartie(centre)
    
    partie.Afficher()

    if fichier_midi != "":
        if isRebond:
            midi_controller.play_next_note()

    screen = partie.makeScreenshot(frame)

midi_controller.cleanup()
pygame.quit()
print("Création de la vidéo : ")
create_video_from_images("VideoBalles/assets/screen", "VideoBalles/resultat.mp4")

sys.exit()


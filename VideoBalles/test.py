import pygame
import sys
import os
import numpy as np
import pygame.midi
import pygame.mixer
from collections import deque
from assets.image_to_video import create_video_from_images
from assets.classes import Balle
from assets.classes import Partie
from assets.classes import MidiController
from random import randint
import random
import math
import mido

#A faire :
# - Ajouter des particules
# - Ajouter des sons quand les arcs sont détruits
# - Ajouter des images
pygame.mixer.init()

total_frame=60*61
vitesse_max = 10.0
fichier_midi = "VideoBalles/assets/midi/Eiffel_65_I_m_Blue.mid" #chemin vide si pas de musique
fichier_son_destruction = "VideoBalles/assets/midi/test.mp3" #chemin vide si pas de son
fond_fenetre = (0, 0, 0)  # Couleur de fond de la fenêtre
rayon_min_arc = 100
taille_premier_arc_debut=200
reduction_arc=1
limite_affichage_arc=532

largeur_rectangle_score = 100  # Largeur du rectangle de score
hauteur_rectangle_score = 50  # Hauteur du rectangle de score
y_rectangle_score = 250  # Position Y du rectangle de score
intervalle_x_rectangle_score = 10  # Espace entre les rectangles de score

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
partie = Partie(width, height, fond_fenetre, vitesse_max, reduction_arc, rayon_min_arc, limite_affichage_arc, largeur_rectangle_score, hauteur_rectangle_score, y_rectangle_score, intervalle_x_rectangle_score, 60, total_frame, fichier_son_destruction)




#PARTIE AJUSTABLE ---------------------------------------------------------------------------------------

#Ajout des balles



couleur_balle = (255, 0, 0)  # Couleur des balles
rayon_balle = 20  # Taille des balles
couleur_interieur_balle = (0, 0, 0)  # Couleur intérieure des balles
taille_contour = 2  # Taille du contour des balles
taille_trainee = 10  # Taille de la traînée des balles
text = "ALL"
afficher_text = False  # Afficher le texte sur les balles
taille_font = 25
couleur_texte = (255, 255, 255)  # Couleur du texte
image="VideoBalles/assets/images/allemagne.png"  # Chemin de l'image de la balle
couleur_rectangle_score = (185, 0, 0)
couleur_texte_score = (255, 255, 255)

# Position aléatoire de la balle dans un carré centré dans le premier arc
#retire / rajoute le rayon de la balle pour éviter que la balle ne soit à cheval sur l'arc
# On ajoute 1 pour éviter que la balle ne soit collée au bord
x = randint((width // 2) - (taille_premier_arc_debut // 2) + rayon_balle + 1, (width // 2) + (taille_premier_arc_debut // 2) - rayon_balle - 1)
y = randint((height // 2) - (taille_premier_arc_debut // 2) + rayon_balle + 1, (height // 2) + (taille_premier_arc_debut // 2) - rayon_balle - 1)

partie.addBalle(x, y, rayon_balle, couleur_balle, taille_trainee, couleur_interieur_balle, taille_contour, text, taille_font, couleur_texte, afficher_text, image, couleur_rectangle_score, couleur_texte_score) #

couleur_balle = (0, 0, 255)  # Couleur des balles
rayon_balle = 20  # Taille des balles
couleur_interieur_balle = (0, 0, 0)  # Couleur intérieure des balles
taille_contour = 2  # Taille du contour des balles
taille_trainee = 10  # Taille de la traînée des balles
couleur_rectangle_score = (0, 0, 185)
couleur_texte_score = (255, 255, 255)
# Position aléatoire de la balle dans un carré centré dans le premier arc
#retire / rajoute le rayon de la balle pour éviter que la balle ne soit à cheval sur l'arc
# On ajoute 1 pour éviter que la balle ne soit collée au bord
text = "FRA"
afficher_text = False  # Afficher le texte sur les balles
taille_font = 25
couleur_texte = (255, 255, 255)  # Couleur du texte
image="VideoBalles/assets/images/1.jpg"  # Chemin de l'image de la balle
x = randint((width // 2) - (taille_premier_arc_debut // 2) + rayon_balle + 1, (width // 2) + (taille_premier_arc_debut // 2) - rayon_balle - 1)
y = randint((height // 2) - (taille_premier_arc_debut // 2) + rayon_balle + 1, (height // 2) + (taille_premier_arc_debut // 2) - rayon_balle - 1)

partie.addBalle(x, y, rayon_balle, couleur_balle, taille_trainee, couleur_interieur_balle, taille_contour, text, taille_font, couleur_texte, afficher_text,  image, couleur_rectangle_score, couleur_texte_score) #



for i in range (1000) :
    angle2 = randint(0, 360)
    #angle2 = 300+ i*7
    angle=(angle2+45)%360
    rotation=0.5
    partie.addArc((width // 2, height // 2), taille_premier_arc_debut + i*16, angle, angle2 , (255, 255, 255), rotation)

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
create_video_from_images("VideoBalles/assets/screen", "VideoBalles/assets/videos/resultat.mp4")

sys.exit()


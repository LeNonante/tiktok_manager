import pygame
import sys
import os
import numpy as np
import pandas as pd
import pygame.midi
import pygame.mixer
from collections import deque
from assets.image_to_video import combine_video_audio, create_video_from_images, boucler_midi
from assets.classes import Balle
from assets.classes import Partie
from assets.classes import MidiController
from assets.classes import MidiToAudioGenerator
from random import randint
import random
import math
import mido

#A faire :
#    - Ajouter les son de destructions 
#   - Ajouter l'écran de fin
#   - Ajouter le titre

pygame.mixer.init()


#PARTIE AJUSTABLE POUR LES PARTICULES ---------------------------------------------------------------------------------------

nb_particules=170

#PARTIE AJUSTABLE POUR LA PARTIE ---------------------------------------------------------------------------------------

total_frame=60*61
vitesse_max = 8.0
fichier_midi = "VideoBalles/assets/midi/Gravity Falls - Made Me Realize.mid" #chemin vide si pas de musique
fichier_son_destruction = "VideoBalles/assets/midi/test.mp3" #chemin vide si pas de son
titre = "Qui va gagner la finale|de la Coupe du Monde|des clubs ?"  #Separer avec | pour faire plusieurs lignes
                                                                    #Mettre "" si pas de titre
couleur_font_titre = (0, 0, 0)  # Couleur du texte du titre
couleur_fond_titre = (255, 255, 255)  # Couleur de fond du titre
fond_fenetre = (0, 0, 0)  # Couleur de fond de la fenêtre
rayon_min_arc = 100
taille_premier_arc_debut=200
reduction_arc=2
limite_affichage_arc=532


largeur_rectangle_score = 100  # Largeur du rectangle de score
hauteur_rectangle_score = 50  # Hauteur du rectangle de score
y_rectangle_score = 150  # Position Y du rectangle de score
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

#boucler et Charger de la musique si le fichier existe
if fichier_midi!="":
    if os.path.exists(fichier_midi[:-4] + "_looped.mid") :
        reponse=str(input("Fichier MIDI déja utilisé, voulez vous le réutiliser ? (O/N)"))
        reponse = reponse.strip().upper()
        if reponse == "N": #Si l'utilisateur ne veut pas réutiliser le fichier
            sys.exit() #Arrêter le programme

    boucler_midi(fichier_midi, fichier_midi[:-4] + "_looped.mid")
    fichier_midi = fichier_midi[:-4] + "_looped.mid"
    midi_controller = MidiController(fichier_midi)  

#Création de la fenêtre
partie = Partie(width, height, fond_fenetre, vitesse_max, reduction_arc, rayon_min_arc, limite_affichage_arc, largeur_rectangle_score, hauteur_rectangle_score, y_rectangle_score, intervalle_x_rectangle_score, 60, total_frame, fichier_son_destruction, nb_particules, titre, couleur_font_titre, couleur_fond_titre)

#CHARGEMENT DES BALLES

df = pd.read_excel("VideoBalles/ListeBalles.xlsx", engine="openpyxl")
df = df[df['Afficher'] == True]  # Garder seulement les lignes où 'Afficher' est True
df = df.reset_index(drop=True) #refaire les indexes des lignes
df["Image"] = df["Image"].fillna("")  # Remplacer les NaN par des chaînes vides
df["Image"] = df["Image"].apply(lambda x: "VideoBalles/assets/images/" + str(x) if x!="" else x)  # Ajouter le début des chemins d'acces des images
df["Rayon Balle"] = df["Rayon Balle"].astype(int)
df["Taille Trainee"] = df["Taille Trainee"].astype(int)
#Ajout des balles

for i in range(len(df)):
    couleur_balle = eval(df.loc[i, "Couleur Balle"])  # Couleur des balles
    rayon_balle = df.loc[i, "Rayon Balle"]  # Taille des balles
    couleur_interieur_balle = eval(df.loc[i, "Couleur Interieur Balle"])  # Couleur intérieure des balles
    taille_contour = int(df.loc[i, "Taille Contour"])  # Taille du contour des balles
    taille_trainee = df.loc[i, "Taille Trainee"]  # Taille de la traînée des balles
    taille_trainee = int(taille_trainee)
    text = df.loc[i, "Texte"]  # Texte à afficher sur les balles
    afficher_text = df.loc[i, "Afficher Texte"]  # Afficher le texte sur les balles
    taille_font = int(df.loc[i, "Taille Font"])  # Taille de la police du texte
    couleur_texte = eval(df.loc[i, "Couleur Texte"])  # Couleur du texte
    image= df.loc[i, "Image"]  # Chemin de l'image de la balle
    couleur_rectangle_score = eval(df.loc[i, "Couleur Rectangle Score"])  # Couleur du rectangle de score
    couleur_texte_score = eval(df.loc[i, "Couleur Texte Score"])  # Couleur du texte de score
    acceleration= float(df.loc[i, "Acceleration"])  # Accélération de la balle

    # Position aléatoire de la balle dans un carré centré dans le premier arc
    #retire / rajoute le rayon de la balle pour éviter que la balle ne soit à cheval sur l'arc
    # On ajoute 1 pour éviter que la balle ne soit collée au bord
    x = randint((width // 2) - (taille_premier_arc_debut // 2) + rayon_balle + 1, (width // 2) + (taille_premier_arc_debut // 2) - rayon_balle - 1)
    y = randint((height // 2) - (taille_premier_arc_debut // 2) + rayon_balle + 1, (height // 2) + (taille_premier_arc_debut // 2) - rayon_balle - 1)

    partie.addBalle(x, y, rayon_balle, couleur_balle, taille_trainee, couleur_interieur_balle, taille_contour, text, taille_font, couleur_texte, afficher_text, image, couleur_rectangle_score, couleur_texte_score, acceleration) #

#PARTIE AJUSTABLE POUR LES ARCS ---------------------------------------------------------------------------------------
for i in range (1000) :
    #angle2 = randint(0, 360)
    angle2 = (300 + i * 6) % 360
    angle = (angle2 + 45) % 360

    effet_hypnotique=False

    color= (255,255,255) #[(255, 0, 0), (0, 0, 255)][i%2]  # Couleur de l'arc

    # Éviter les arcs trop larges (surface solide > 300°) sinon l'arc est mal affiché
    etendue = (angle - angle2) % 360
    if etendue > 300:
        i=i-1
        continue  # on saute cet arc
    rotation=0.5
    partie.addArc((width // 2, height // 2), taille_premier_arc_debut + i*12, angle, angle2 , color, rotation, effet_hypnotique)

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

frames_rebond=partie.getListeFramesRebonds() #On recupere les frames avec des rebonds
print(frames_rebond)
print("Génération de l'audio synchronisé...")
if fichier_midi != "" and frames_rebond:
    audio_generator = MidiToAudioGenerator(fichier_midi, fps=60)
    audio_generator.generate_audio_from_frames(
        frames_rebond,
        "VideoBalles/assets/videos/audio_sync.wav",
        note_duration=0.5
    )
    print(f"Audio généré avec {len(frames_rebond)} notes aux frames : {frames_rebond}")
else:
    print("Aucun fichier MIDI ou aucun rebond détecté")



print("Création de la vidéo : ")
create_video_from_images("VideoBalles/assets/screen", "VideoBalles/assets/videos/resultat.mp4")

print("Ajout de l'audio : ")
combine_video_audio("VideoBalles/assets/videos/resultat.mp4", "VideoBalles/assets/videos/audio_sync.wav", "VideoBalles/assets/videos/resultat_final.mp4")

sys.exit()


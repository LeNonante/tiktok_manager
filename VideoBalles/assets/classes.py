import pygame
import numpy as np
import pygame.midi
import mido
from collections import deque
import random
import math

class Partie:
    def __init__(self, width, height, bg, vitesse_max_balle, reduction_arc, limite_rayon_arc,limite_affichage_arc, largeur_rectangle_score, hauteur_rectangle_score, y_rectangle_score, intervalle_x_rectangle_score, fps, total_frame, fichier_son_destruction, nb_particules, titre, couleur_font_titre, couleur_fond_titre, titreImage):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.bg = bg
        self.liste_balles = []
        self.vitesse_max_balle = vitesse_max_balle
        self.musique = False
        self.liste_arcs = []
        self.reduction_arc = reduction_arc
        self.rayon_premier_arc = None  # Rayon du premier arc
        self.limite_rayon_arc = limite_rayon_arc  # Limite de réduction du rayon de l'arc
        self.limite_affichage_arc=limite_affichage_arc
        self.largeur_rectangle_score = largeur_rectangle_score  # Largeur du rectangle de score
        self.hauteur_rectangle_score = hauteur_rectangle_score  # Hauteur du rectangle de score
        self.y_rectangle_score = y_rectangle_score 
        self.intervalle_x_rectangle_score = intervalle_x_rectangle_score  # Espace entre les rectangles de score
        self.frame = 0  # Compteur de frames
        self.fps = fps  # Frames par seconde
        self.total_frame = total_frame  # Nombre total de frames pour la vidéo

        self.titre=titre
        self.couleur_font_titre = couleur_font_titre
        self.coueleur_fond_titre = couleur_fond_titre
        self.titreImage = titreImage  # Chemin de l'image du titre

        self.nb_particules=nb_particules
        self.systeme_particules = SystemeParticules(self.nb_particules)

        self.liste_frames_rebonds=[]

        # Charger le son de destruction
        self.son_destruction = None
        if fichier_son_destruction and fichier_son_destruction != "":
            try:
                self.son_destruction = pygame.mixer.Sound(fichier_son_destruction)
            except pygame.error as e:
                print(f"Impossible de charger le son : {e}")
                self.son_destruction = None

    def jouer_son_destruction(self):
        """Joue le son de destruction d'arc"""
        if self.son_destruction:
            self.son_destruction.play()



    def addBalle(self, x, y, radius, color, trainee_length, couleur_interieur, taille_contour, text, taille_font, couleur_texte, afficher_text, image, couleur_rectangle_score, couleur_texte_score, acceleration, taille_font_score):
        """
        Ajoute une nouvelle balle à la liste des balles.
        Paramètres :
            x (float) : La position horizontale de la balle.
            y (float) : La position verticale de la balle.
            radius (float) : Le rayon de la balle.
            color (tuple ou str) : La couleur de la balle.
        Retour :
            None
        """
        balle = Balle(self, x, y, radius, color, trainee_length, couleur_interieur, taille_contour, text, taille_font, couleur_texte, afficher_text, image, couleur_rectangle_score, couleur_texte_score, acceleration, taille_font_score)
        self.liste_balles.append(balle)
    
    def addArc(self, centre, rayon, angle_debut, angle_fin, couleur, angle_rotation_arc, effet_hypnotique):
        """
        Ajoute un arc de cercle à la liste des arcs.
        Paramètres :
            centre (tuple ou list) : Le centre de l'arc de cercle.
            rayon (float) : Le rayon de l'arc de cercle.
            angle_debut (float) : L'angle de début de l'arc en degrés.
            angle_fin (float) : L'angle de fin de l'arc en degrés.
            couleur (tuple ou str) : La couleur de l'arc.
        Retour :
            None
        """
        arc = ArcCercle(centre, rayon, angle_debut, angle_fin, couleur, angle_rotation_arc, effet_hypnotique)
        self.liste_arcs.append(arc)

    def setPartie(self, centre):
        """
        Met à jour l'état de la partie en dessinant les balles etc
        Paramètres :
            centre (numpy.array) : Le centre du cercle autour duquel les balles se déplacent.
        Retour :
            None
        """
        self.centre = centre
        self.screen.fill(self.bg)
        self.rayon_premier_arc = self.liste_arcs[0].rayon if self.liste_arcs else None

        # Stocker les arcs à supprimer
        arcs_to_remove = []

        nombre_rebond=0 #Permet de palier au fait que le bolleen est reset a chaque balle (on perd l'info du rebon de la balle 1 si la balle  2 le remplace par True)
        for i in range(len(self.liste_balles)):
            b=self.liste_balles[i]
            if i==0 :
                rebond, arc_touche = b.update_position(centre, self.vitesse_max_balle, self.liste_arcs)
                # Si un arc a été touché, le marquer pour suppression
                if arc_touche is not None:
                    b.add_Point()
                    arcs_to_remove.append(arc_touche)
                elif rebond :
                    nombre_rebond+=1
            else:
                rebond, arc_touche = b.update_position(centre, self.vitesse_max_balle, self.liste_arcs)
                # Si un arc a été touché, le marquer pour suppression
                if arc_touche is not None:
                    b.add_Point()
                    arcs_to_remove.append(arc_touche)
                elif rebond :
                    nombre_rebond+=1
            print(f"Balle {i+1} - Position: {b.position}, Vitesse: {b.vitesse}, Score: {b.score}")
            b.draw(self.screen)

        # Supprimer les arcs touchés
        for arc in arcs_to_remove:
            if arc in self.liste_arcs:
                self.jouer_son_destruction()  # Jouer le son de destruction
                # Créer une explosion de particules
                self.systeme_particules.creer_explosion_arc(arc)
                self.liste_arcs.remove(arc)

        # Mettre à jour et dessiner les particules
        self.systeme_particules.update()

        for arc in self.liste_arcs:
            arc.tourner()
            if self.rayon_premier_arc is not None:
                if self.rayon_premier_arc > self.limite_rayon_arc :
                    arc.reduire_rayon(self.reduction_arc)
            if arc.rayon <= self.limite_affichage_arc:
                arc.draw(self.screen)

        # NOUVEAU : Dessiner les particules par-dessus les arcs
        self.systeme_particules.draw(self.screen)

        self.frame += 1
        #Affichage des scores
        for i in range(len(self.liste_balles)):
            b=self.liste_balles[i]

            x1 = (self.width - self.largeur_rectangle_score*len(self.liste_balles) - self.intervalle_x_rectangle_score*(len(self.liste_balles)-1)) /2 + i*(self.largeur_rectangle_score+self.intervalle_x_rectangle_score)  # Position x du rectangle de score
            y1 = self.y_rectangle_score
            largeur = self.largeur_rectangle_score
            hauteur = self.hauteur_rectangle_score

            couleur_rectangle = b.couleur_rectangle_score
            couleur_score = b.couleur_texte_score
            text = b.text
            score = b.score

            pygame.draw.rect(self.screen, couleur_rectangle, [x1, y1, largeur, hauteur])  # rectangle
            font_score = pygame.font.Font(None, b.taille_font_score)  # Taille de la police du texte de score
            score_surface = font_score.render(f"{text}: {score}", True, couleur_score)  # Utiliser la couleur du texte du score
            score_rect = score_surface.get_rect(center=(x1 + largeur/2, y1 + hauteur/2))
            self.screen.blit(score_surface, score_rect)

        # Affichage du temps restant
        largeur_rectangle_temps = self.largeur_rectangle_score+30
        pygame.draw.rect(self.screen, (255, 255, 255), [(self.width - largeur_rectangle_temps) / 2, y1+self.hauteur_rectangle_score + self.intervalle_x_rectangle_score, largeur_rectangle_temps, hauteur])  # rectangle
        time_surface = font_score.render(f"Time left: { (self.total_frame - self.frame) / self.fps:.0f}", True, (0, 0, 0))
        time_rect = time_surface.get_rect(center=(self.width / 2, y1+self.hauteur_rectangle_score + self.intervalle_x_rectangle_score + hauteur / 2))
        self.screen.blit(time_surface, time_rect)
        

        # Affichage de l'image du titre
        if self.titreImage != "":
            image_titre = pygame.image.load(self.titreImage).convert_alpha()
            # Enregistrer le ratio de l'image du titre
            ratio_image_titre = image_titre.get_width() / image_titre.get_height()
            largeur_image_titre = self.width / 1.7  # Largeur de l'image du titre
            hauteur_image_titre = largeur_image_titre / ratio_image_titre  # Hauteur de l'image du titre
            y_titre = self.y_rectangle_score - self.intervalle_x_rectangle_score - hauteur_image_titre/2  # Position y de l'image du titre
            taille_image = (largeur_image_titre, hauteur_image_titre)
            image_titre = pygame.transform.smoothscale(image_titre, taille_image)
            image_rect = image_titre.get_rect(center=(self.width / 2, y_titre))
            self.screen.blit(image_titre, image_rect)


        # Affichage du titre
        elif self.titre != "":
                font_titre = pygame.font.Font(None, 30)

                liste_lignes_titre = self.titre.split("|")  # Séparer le titre en lignes

                y_titre = self.y_rectangle_score - self.intervalle_x_rectangle_score - len(liste_lignes_titre) * 30  # Position y du titre

                pygame.draw.rect(self.screen, self.coueleur_fond_titre, [(self.width-(self.width/1.7))/2, y_titre, self.width/1.7, len(liste_lignes_titre)*30])  # rectangle de fond du titre
                for i, ligne in enumerate(liste_lignes_titre):
                    titre_surface = font_titre.render(ligne, True, self.couleur_font_titre)
                    titre_rect = titre_surface.get_rect(center=(self.width / 2, y_titre + 15 + i * 30))
                    self.screen.blit(titre_surface, titre_rect)

        rebond = nombre_rebond>0

        if rebond :
            self.addRebondToFramesList()

        return rebond

    # def isRebond(self):
    #     """
    #     Vérifie si une balle a rebondi contre le bord de l'écran.
    #     Retourne True si une balle a rebondi, sinon False.
    #     """
    #     self.rayon_premier_arc = self.liste_arcs[0].rayon if self.liste_arcs else None
    #     for b in self.liste_balles:
    #         if b.is_Rebond(self.centre, self.rayon_premier_arc):
    #             return True
    #     return False

    def Afficher(self):
        """
        Affiche la partie en mettant à jour l'écran.
        """
        pygame.display.flip()

    def AfficherEcranFinal(self):
        """
        Affiche l'écran final avec le message de fin de partie.
        """
        #Affichage du gagnant
        self.screen.fill(self.bg)
        font = pygame.font.Font(None, 40)
        score_max=0
        winner=""
        couleur_fond_titre = (255, 255, 255)  # Couleur de fond du titre
        couleur_font = (255, 255, 255)  # Couleur du texte du titre
        for i in self.liste_balles:
            if i.score > score_max:
                score_max = i.score
                winner = i.text
                couleur_fond_titre = i.couleur_rectangle_score
                couleur_font=i.couleur_texte_score
                chemin_image=i.cheminImage    


        self.screen.fill(couleur_fond_titre)
        if chemin_image == "":
            text_surface = font.render(f"Winner : {winner}", True, couleur_font)
            text_rect = text_surface.get_rect(center=(self.width / 2, 400))
            self.screen.blit(text_surface, text_rect)
        else:
            text_surface = font.render(f"Winner : {winner}", True, couleur_font)
            text_rect = text_surface.get_rect(center=(self.width / 2, 250))
            self.screen.blit(text_surface, text_rect)

            image = pygame.image.load(chemin_image).convert_alpha() if chemin_image!="" else None
            # Redimensionner l'image de la balle
            image_rond = pygame.transform.smoothscale(image, (250, 250))
            # Créer un masque circulaire
            mask = pygame.Surface((250, 250), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (125, 125), 125)
            # Appliquer le masque à l'image
            image_rond.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            image = image_rond

            image_rect = image.get_rect(center=(self.width / 2, 450))
            self.screen.blit(image, image_rect)

        # Affichage du titre
        if self.titre != "":
            font_titre = pygame.font.Font(None, 50)

            liste_lignes_titre = self.titre.split("|")  # Séparer le titre en lignes

            y_titre = 100  # Position y du titre
            for i, ligne in enumerate(liste_lignes_titre):
                titre_surface = font_titre.render(ligne, True, self.couleur_font_titre)
                titre_rect = titre_surface.get_rect(center=(self.width / 2, y_titre + 15 + i * 30))
                self.screen.blit(titre_surface, titre_rect)

        pygame.display.flip()

    def getScreen(self):
        """
        Retourne la surface d'affichage principale.
        """
        return self.screen

    def makeScreenshot(self, frame):
        """
        Prend une capture d'écran de la fenêtre et l'enregistre dans un fichier.
        """
        screenshot = pygame.Surface((self.width, self.height))
        screenshot.blit(self.screen, (0, 0))
        pygame.image.save(screenshot, f"VideoBalles/assets/screen/capture_ecran_{frame:04d}.png")

    def addRebondToFramesList (self):
        """
        Ajoute la frame actuelle dans la liste des frames qui ont des rebonds
        """
        self.liste_frames_rebonds.append(self.frame)

    def getListeFramesRebonds(self):
        return self.liste_frames_rebonds

class Balle:
    def __init__(self, partie, x, y, radius, color, trainee_length, couleur_interieur, taille_contour, text, taille_font, couleur_texte, afficher_text, image, couleur_rectangle_score, couleur_texte_score, acceleration, taille_font_score):
        self.score= 0
        self.position=np.array([x+10,y]).astype(float)
        self.vitesse=np.array([0,0]).astype(float)
        self.radius = radius
        self.color = color
        self.couleur_interieur = couleur_interieur  # Couleur intérieure de la balle
        self.taille_contour = taille_contour  # Taille du contour de la balle
        # Pour la traînée
        self.trainee_length = trainee_length  # Nombre de positions à garder en mémoire
        self.positions_precedentes = deque(maxlen=trainee_length)
        self.positions_precedentes.append(self.position.copy())
        self.text = text  
        self.taille_font = taille_font  # Taille de la police pour le texte
        self.couleur_texte = couleur_texte  # Couleur du texte
        self.afficher_text = afficher_text  # Indique si le texte doit être affiché
        self.cheminImage= image  # Chemin de l'image de la balle
        self.image = pygame.image.load(image).convert_alpha() if image!="" else None  # Charger l'image de la balle
        self.couleur_rectangle_score = couleur_rectangle_score  # Couleur du rectangle de score
        self.taille_font_score = taille_font_score
        self.couleur_texte_score = couleur_texte_score  # Couleur du texte du score
        self.acceleration=acceleration
        self.partie=partie


    def draw(self, surface):
        """
        Dessine la balle sur la surface donnée.
        """
        # Dessiner la traînée
        self.draw_trainee(surface)

        if self.image is not None: #si il y a une image
            # Redimensionner l'image de la balle pour qu'elle corresponde au rayon
            image_rond = pygame.transform.smoothscale(self.image, (self.radius * 2, self.radius * 2))
            # Créer un masque circulaire
            mask = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (self.radius, self.radius), self.radius)
            # Appliquer le masque à l'image
            image_rond.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.image = image_rond
            # Positionner l'image au centre de la balle
            image_rect = self.image.get_rect(center=self.position)
            surface.blit(self.image, image_rect)
            pygame.draw.circle(surface, self.color, self.position, self.radius, self.taille_contour)  # Dessiner le contour de la balle
        
        else:  # Si pas d'image, dessiner un cercle
            #Contours
            pygame.draw.circle(surface, self.color, self.position, self.radius)
            # Dessiner le cercle intérieur par-dessus l'image
            pygame.draw.circle(surface, self.couleur_interieur, self.position, self.radius-self.taille_contour)
        
        # ecrire le texte au centre de la balle
        if self.afficher_text:
            font = pygame.font.Font(None, self.taille_font)
            text_surface = font.render(self.text, True, self.couleur_texte)
            text_rect = text_surface.get_rect(center=self.position)
            surface.blit(text_surface, text_rect)
        
        

    def add_Point(self):
        """
        Ajoute un point au score de la balle.
        """
        self.score += 1

    def draw_trainee(self, surface):
        """
        Dessine la traînée de la balle avec une opacité décroissante.
        """
        if len(self.positions_precedentes) < 2:
            return
            
        for i, pos in enumerate(self.positions_precedentes):
            if i == len(self.positions_precedentes) - 1:
                continue  # Skip la position actuelle
                
            # Calculer l'opacité (plus ancien = plus transparent)
            alpha = int(255 * (i / len(self.positions_precedentes)))
            
            # Calculer la taille (plus ancien = plus petit)
            taille = max(1, int(self.radius * (i / len(self.positions_precedentes))))
            
            # Créer une couleur avec transparence
            color_avec_alpha = (*self.color, alpha)
            
            # Créer une surface temporaire pour la transparence
            temp_surface = pygame.Surface((taille * 2, taille * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color_avec_alpha, (taille, taille), taille)
            
            # Dessiner sur la surface principale
            surface.blit(temp_surface, (pos[0] - taille, pos[1] - taille))

    def update_vitesse(self, vitesse_max_balle):
        # Accelerer vers le bas
        self.vitesse[1] += self.acceleration  # Ajouter une accélération vers le bas
        speed = np.linalg.norm(self.vitesse)
        if speed > vitesse_max_balle:
            self.vitesse = (self.vitesse / speed) * vitesse_max_balle

    def est_dans_trou_arc(self, centre, arc):

        """
        Vérifie si la balle est dans le "trou" de l'arc (pas sur la partie solide)
        """
        # Calculer l'angle de la position de la balle par rapport au centre
        direction = self.position - centre
        angle_balle = np.degrees(np.arctan2(-direction[1], direction[0])) #je mets - car pygame à 0 en bas et nunpy en haut
        
        # Normaliser l'angle entre 0 et 360
        if angle_balle < 0:
            angle_balle += 360
            
        # Normaliser les angles de l'arc
        angle_debut_norm = arc.angle_debut % 360
        angle_fin_norm = arc.angle_fin % 360
        
        # Vérifier si l'angle de la balle est sur la partie SOLIDE de l'arc
        # La partie solide est ENTRE angle_debut et angle_fin
        is_on_solid_part = False
        
        if angle_debut_norm <= angle_fin_norm:
            # Cas normal (pas de passage par 0°)
            is_on_solid_part = angle_debut_norm <= angle_balle <= angle_fin_norm
        else:
            # Cas où l'arc passe par 0° (ex: de 350° à 10°)
            is_on_solid_part = angle_balle >= angle_debut_norm or angle_balle <= angle_fin_norm
        
        # Retourner True si la balle est dans le TROU (pas sur la partie solide)
        return not is_on_solid_part
    
    def update_position(self, centre, vitesse_max_balle, liste_arcs):
        """
        Met à jour la position avec gestion des collisions avec les arcs
        """
        rebond = False
        arc_touche = None
        
        self.update_vitesse(vitesse_max_balle)
        direction = self.position - centre
        distance = np.linalg.norm(direction)
        
        # Vérifier collision avec le premier arc (le plus grand)
        if liste_arcs:
            premier_arc = liste_arcs[0]
            rayon_cercle = premier_arc.rayon
            
            if distance > rayon_cercle - self.radius:
                if distance != 0:
                    # Vérifier si la balle est dans le "trou" de l'arc
                    if self.est_dans_trou_arc(centre, premier_arc):
                        # La balle passe dans le trou : détruire l'arc
                        arc_touche = premier_arc
                        print(f"Arc détruit ! Angle balle: {np.degrees(np.arctan2(direction[1], direction[0]))} Arc: {premier_arc.angle_debut:.1f}° à {premier_arc.angle_fin:.1f}°")
                    else:
                        # Collision normale avec l'arc : rebond
                        direction_normale = direction / distance
                        self.vitesse = self.vitesse - 2 * np.dot(self.vitesse, direction_normale) * direction_normale
                        self.position = centre + direction_normale * (rayon_cercle - self.radius - 2)
                        rebond = True
        
        # Sauvegarder la position actuelle avant de la mettre à jour
        self.positions_precedentes.append(self.position.copy())
        self.position += self.vitesse
        
        return rebond, arc_touche
    


class ArcCercle:
    def __init__(self, centre, rayon, angle_debut, angle_fin, couleur, angle_rotation_arc, effet_hypnotique):
        self.centre = np.array(centre).astype(float)
        self.rayonInitial = rayon
        self.rayon= rayon
        self.angle_debut = angle_debut
        self.angle_fin = angle_fin
        self.couleur = couleur
        self.angle_rotation_arc = angle_rotation_arc  # Angle de rotation de l'arc
        self.effet_hypnotique = effet_hypnotique

    def draw(self, surface):
        """
        Dessine l'arc de cercle sur la surface donnée.
        """
        pygame.draw.arc(surface, self.couleur, (self.centre[0] - self.rayon, self.centre[1] - self.rayon, 2 * self.rayon, 2 * self.rayon), np.deg2rad(self.angle_debut), np.deg2rad(self.angle_fin), 1)

    def tourner(self):
        """
        Tourne l'arc de cercle d'un certain angle.
        """
        if self.effet_hypnotique:
            self.angle_debut += self.angle_rotation_arc + self.rayon * 0.005  # Ajouter un petit mouvement de rotation
            self.angle_fin += self.angle_rotation_arc + self.rayon * 0.005
        else :
            self.angle_debut += self.angle_rotation_arc
            self.angle_fin += self.angle_rotation_arc

    def reduire_rayon(self, reduction):
        """
        Réduit le rayon de l'arc de cercle.
        """
        self.rayon = max(0, self.rayon - reduction)
    
    



class MidiController:
    def __init__(self, midi_file):
        pygame.midi.init()
        self.midi_file = mido.MidiFile(midi_file)
        self.notes = []
        self._extract_notes()
        self.current_note_index = 0
        
        # Garder trace de toutes les notes en cours
        self.playing_notes = []
        
        self.midi_out = pygame.midi.Output(0)
    
    def _extract_notes(self):
        for track in self.midi_file.tracks:
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    self.notes.append({
                        'note': msg.note,
                        'velocity': msg.velocity,
                        'channel': msg.channel
                    })
    
    def play_next_note(self):
        # Arrêter toutes les notes en cours
        self.stop_all_notes()
        
        if self.current_note_index < len(self.notes):
            note = self.notes[self.current_note_index]
            
            # Jouer la nouvelle note
            self.midi_out.note_on(note['note'], note['velocity'], note['channel'])
            
            # Ajouter à la liste des notes en cours
            self.playing_notes.append(note)
            
            self.current_note_index += 1
            return True
        return False
    
    def stop_all_notes(self):
        """Arrêter toutes les notes en cours"""
        for note in self.playing_notes:
            self.midi_out.note_off(note['note'], note['channel'])
        self.playing_notes.clear()
    
    def cleanup(self):
        self.stop_all_notes()
        self.midi_out.close()
        pygame.midi.quit()


class Particule:
    def __init__(self, x, y, vx, vy, couleur, taille, duree_vie):
        self.position = np.array([x, y]).astype(float)
        self.vitesse = np.array([vx, vy]).astype(float)
        self.couleur = couleur
        self.taille_initiale = taille
        self.taille = taille
        self.duree_vie_max = duree_vie
        self.duree_vie = duree_vie
        self.alpha = 255
        
    def update(self):
        """Met à jour la position et les propriétés de la particule"""
        # Mise à jour de la position
        self.position += self.vitesse
        
        # Gravité légère
        self.vitesse[1] += 0.1
        
        # Friction
        self.vitesse *= 0.98
        
        # Diminution de la durée de vie
        self.duree_vie -= 1
        
        # Calcul de l'alpha et de la taille en fonction de la durée de vie restante
        ratio_vie = max(0, self.duree_vie / self.duree_vie_max)
        self.alpha = int(255 * ratio_vie)
        self.taille = self.taille_initiale * ratio_vie
        
        return self.duree_vie > 0
    
    def draw(self, surface):
        """Dessine la particule avec transparence"""
        if self.taille > 0.5:
            # Créer une surface temporaire pour la transparence
            temp_surface = pygame.Surface((int(self.taille * 2), int(self.taille * 2)), pygame.SRCALPHA)
            couleur_avec_alpha = (*self.couleur[:3], self.alpha)
            pygame.draw.circle(temp_surface, couleur_avec_alpha, (int(self.taille), int(self.taille)), int(self.taille))
            surface.blit(temp_surface, (self.position[0] - self.taille, self.position[1] - self.taille))

class SystemeParticules:
    def __init__(self, nb_particules):
        self.particules = []
        self.nb_particules = nb_particules

    def creer_explosion_arc(self, arc):
        """Crée une explosion de particules le long de l'arc détruit"""
        centre = arc.centre
        rayon = arc.rayon
        angle_debut_rad = np.deg2rad(arc.angle_debut)
        angle_fin_rad = np.deg2rad(arc.angle_fin)
        
        # Calculer l'étendue angulaire de l'arc
        if arc.angle_fin > arc.angle_debut:
            etendue_angulaire = arc.angle_fin - arc.angle_debut
        else:
            etendue_angulaire = (360 - arc.angle_debut) + arc.angle_fin
        
        # Générer des particules le long de l'arc
        for i in range(self.nb_particules):
            # Position aléatoire le long de l'arc
            if arc.angle_fin > arc.angle_debut:
                angle = random.uniform(arc.angle_debut, arc.angle_fin)
            else:
                # Cas où l'arc traverse 0°
                if random.random() < 0.5:
                    angle = random.uniform(arc.angle_debut, 360)
                else:
                    angle = random.uniform(0, arc.angle_fin)
            
            angle_rad = np.deg2rad(angle)
            
            # Position de la particule sur l'arc
            x = centre[0] + rayon * np.cos(angle_rad)
            y = centre[1] + rayon * np.sin(angle_rad)
            
            # Vitesse initiale : vers l'extérieur avec un peu d'aléatoire
            vitesse_radiale = random.uniform(2, 6)
            angle_vitesse = angle_rad + random.uniform(-0.3, 0.3)  # Petit angle aléatoire
            
            vx = vitesse_radiale * np.cos(angle_vitesse)
            vy = vitesse_radiale * np.sin(angle_vitesse)
            
            # Propriétés de la particule
            couleur = arc.couleur
            taille = random.uniform(1, 3)
            duree_vie = random.randint(30, 80)  # frames
            
            particule = Particule(x, y, vx, vy, couleur, taille, duree_vie)
            self.particules.append(particule)
    
    def update(self):
        """Met à jour toutes les particules et supprime celles qui sont mortes"""
        particules_vivantes = []
        for particule in self.particules:
            if particule.update():
                particules_vivantes.append(particule)
        self.particules = particules_vivantes
    
    def draw(self, surface):
        """Dessine toutes les particules"""
        for particule in self.particules:
            particule.draw(surface)
    
    def get_nombre_particules(self):
        """Retourne le nombre de particules actives"""
        return len(self.particules)
    



import mido
import numpy as np
from scipy.io import wavfile
import pygame
import pygame.midi
import time
import threading
import queue

class MidiToAudioGenerator:
    def __init__(self, midi_file, fps=60, sample_rate=44100):
        """
        Initialise le générateur audio MIDI
        
        Args:
            midi_file (str): Chemin vers le fichier MIDI
            fps (int): Frames par seconde de la vidéo
            sample_rate (int): Taux d'échantillonnage audio
        """
        self.midi_file = mido.MidiFile(midi_file)
        self.fps = fps
        self.sample_rate = sample_rate
        self.frame_duration = 1.0 / fps  # Durée d'une frame en secondes
        self.notes = []
        self._extract_notes()
        
        # Initialiser pygame MIDI
        pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
        pygame.midi.init()
        
    def _extract_notes(self):
        """Extrait les notes du fichier MIDI"""
        for track in self.midi_file.tracks:
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    self.notes.append({
                        'note': msg.note,
                        'velocity': msg.velocity,
                        'channel': msg.channel
                    })
    
    def generate_audio_from_frames(self, frame_list, output_file="output_audio.wav", note_duration=0.5):
        """
        Génère un fichier audio en jouant les notes aux frames spécifiées
        
        Args:
            frame_list (list): Liste des numéros de frames où jouer les notes
            output_file (str): Nom du fichier audio de sortie
            note_duration (float): Durée de chaque note en secondes
        """
        if not frame_list:
            print("Aucune frame spécifiée")
            return
        
        # Calculer la durée totale nécessaire
        max_frame = max(frame_list)
        total_duration = (max_frame + 1) * self.frame_duration + note_duration
        total_samples = int(total_duration * self.sample_rate)
        
        # Créer un tableau audio vide (stéréo)
        audio_data = np.zeros((total_samples, 2), dtype=np.float32)
        
        print(f"Génération audio pour {len(frame_list)} notes...")
        
        # Générer chaque note
        for i, frame_num in enumerate(frame_list):
            if i >= len(self.notes):
                break
                
            note_info = self.notes[i]
            
            # Calculer le temps de début de la note
            start_time = frame_num * self.frame_duration
            start_sample = int(start_time * self.sample_rate)
            
            # Générer la note
            note_samples = self._generate_note_samples(
                note_info['note'], 
                note_info['velocity'], 
                note_duration
            )
            
            # Ajouter la note au tableau audio
            end_sample = min(start_sample + len(note_samples), total_samples)
            if start_sample < total_samples:
                audio_data[start_sample:end_sample] += note_samples[:end_sample-start_sample]
        
        # Normaliser l'audio pour éviter la saturation
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val * 0.8
        
        # Convertir en format 16-bit pour l'enregistrement
        audio_16bit = (audio_data * 32767).astype(np.int16)
        
        # Enregistrer le fichier audio
        wavfile.write(output_file, self.sample_rate, audio_16bit)
        print(f"Audio généré : {output_file}")
    
    def _generate_note_samples(self, note_number, velocity, duration):
        """
        Génère les échantillons audio pour une note donnée
        
        Args:
            note_number (int): Numéro de la note MIDI (0-127)
            velocity (int): Vélocité de la note (0-127)
            duration (float): Durée de la note en secondes
        
        Returns:
            np.array: Échantillons audio stéréo
        """
        # Convertir le numéro de note MIDI en fréquence
        frequency = 440.0 * (2 ** ((note_number - 69) / 12.0))
        
        # Générer les échantillons
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)
        
        # Créer une forme d'onde simple (onde sinusoïdale avec harmoniques)
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)  # Harmonique
        wave += 0.1 * np.sin(2 * np.pi * frequency * 3 * t)  # Harmonique
        
        # Appliquer l'enveloppe ADSR simple
        envelope = self._create_envelope(num_samples, velocity)
        wave *= envelope
        
        # Créer un signal stéréo
        stereo_wave = np.column_stack((wave, wave))
        
        return stereo_wave
    
    def _create_envelope(self, num_samples, velocity):
        """
        Crée une enveloppe ADSR simple pour la note
        
        Args:
            num_samples (int): Nombre d'échantillons
            velocity (int): Vélocité de la note
        
        Returns:
            np.array: Enveloppe d'amplitude
        """
        # Normaliser la vélocité
        amplitude = velocity / 127.0
        
        # Paramètres d'enveloppe
        attack_samples = int(0.01 * self.sample_rate)  # 10ms d'attaque
        decay_samples = int(0.05 * self.sample_rate)   # 50ms de decay
        sustain_level = 0.7 * amplitude
        release_samples = int(0.2 * self.sample_rate)  # 200ms de release
        
        envelope = np.ones(num_samples)
        
        # Attaque
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, amplitude, attack_samples)
        
        # Decay
        if decay_samples > 0 and attack_samples + decay_samples < num_samples:
            envelope[attack_samples:attack_samples + decay_samples] = np.linspace(
                amplitude, sustain_level, decay_samples
            )
        
        # Sustain
        sustain_start = attack_samples + decay_samples
        sustain_end = max(sustain_start, num_samples - release_samples)
        if sustain_start < sustain_end:
            envelope[sustain_start:sustain_end] = sustain_level
        
        # Release
        if release_samples > 0 and sustain_end < num_samples:
            envelope[sustain_end:] = np.linspace(
                sustain_level, 0, num_samples - sustain_end
            )
        
        return envelope

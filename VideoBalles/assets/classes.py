import pygame
import numpy as np
import pygame.midi
import mido
from collections import deque

class Partie:
    def __init__(self, width, height, bg=(0, 0, 0), vitesse_max_balle=10.0, angle_rotation_arc=0.2, reduction_arc=0.1, limite_rayon_arc=110):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.bg = bg
        self.liste_balles = []
        self.vitesse_max_balle = vitesse_max_balle
        self.musique = False
        self.angle_rotation_arc = angle_rotation_arc
        self.liste_arcs = []
        self.reduction_arc = reduction_arc
        self.rayon_premier_arc = None  # Rayon du premier arc
        self.limite_rayon_arc = limite_rayon_arc  # Limite de réduction du rayon de l'arc

    def addBalle(self, x, y, radius, color):
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
        balle = Balle(x, y, radius, color)
        self.liste_balles.append(balle)
    
    def addArc(self, centre, rayon, angle_debut, angle_fin, couleur):
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
        arc = ArcCercle(centre, rayon, angle_debut, angle_fin, couleur)
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

        for i in range(len(self.liste_balles)):
            b=self.liste_balles[i]
            if i==0 :
                rebond, arc_touche = b.update_position(centre, self.vitesse_max_balle, self.liste_arcs)
                # Si un arc a été touché, le marquer pour suppression
                if arc_touche is not None:
                    arcs_to_remove.append(arc_touche)
            else:
                b.update_position(centre, self.vitesse_max_balle, self.rayon_premier_arc)
            b.draw(self.screen)

        # Supprimer les arcs touchés
        for arc in arcs_to_remove:
            if arc in self.liste_arcs:
                self.liste_arcs.remove(arc)
        
        for arc in self.liste_arcs:
            arc.tourner(self.angle_rotation_arc)
            if self.rayon_premier_arc is not None:
                if self.rayon_premier_arc > self.limite_rayon_arc :
                    arc.reduire_rayon(self.reduction_arc)
            if arc.rayon <= 232:
                arc.draw(self.screen)
        
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


class Balle:
    def __init__(self, x, y, radius, color, trainee_length=10):
        self.position=np.array([x+10,y]).astype(float)
        self.vitesse=np.array([0,0]).astype(float)
        self.radius = radius
        self.color = color
        # Pour la traînée
        self.trainee_length = trainee_length  # Nombre de positions à garder en mémoire
        self.positions_precedentes = deque(maxlen=trainee_length)
        self.positions_precedentes.append(self.position.copy())
        self.f=0

    def draw(self, surface):
        """
        Dessine la balle sur la surface donnée.
        """
        # Dessiner la traînée
        self.draw_trainee(surface)
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        pygame.draw.circle(surface, (0,0,0), self.position, self.radius-5)
        self.f+=1

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
        self.vitesse[1] += 0.3  # Ajouter une accélération vers le bas
        speed = np.linalg.norm(self.vitesse)
        if speed > vitesse_max_balle:
            self.vitesse = (self.vitesse / speed) * vitesse_max_balle
        print(self.vitesse)

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
                        print(f"Arc détruit ! Angle balle: {np.degrees(np.arctan2(direction[1], direction[0]))} Arc: {premier_arc.angle_debut:.1f}° à {premier_arc.angle_fin:.1f}° / {self.f}")
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
    def __init__(self, centre, rayon, angle_debut, angle_fin, couleur):
        self.centre = np.array(centre).astype(float)
        self.rayonInitial = rayon
        self.rayon= rayon
        self.angle_debut = angle_debut
        self.angle_fin = angle_fin
        self.couleur = couleur

    def draw(self, surface):
        """
        Dessine l'arc de cercle sur la surface donnée.
        """
        pygame.draw.arc(surface, self.couleur, (self.centre[0] - self.rayon, self.centre[1] - self.rayon, 2 * self.rayon, 2 * self.rayon), np.deg2rad(self.angle_debut), np.deg2rad(self.angle_fin), 3)

    def tourner(self, angle):
        """
        Tourne l'arc de cercle d'un certain angle.
        """
        self.angle_debut += 3
        self.angle_fin += 3
    
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
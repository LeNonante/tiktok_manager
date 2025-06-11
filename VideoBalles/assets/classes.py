import pygame
import numpy as np

class Partie:
    def __init__(self, width, height, bg=(0, 0, 0), vitesse_max_balle=10.0):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.bg = bg
        self.liste_balles = []
        self.vitesse_max_balle = vitesse_max_balle

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

    def setPartie(self, centre):
        """
        Met à jour l'état de la partie en dessinant les balles etc
        Paramètres :
            centre (numpy.array) : Le centre du cercle autour duquel les balles se déplacent.
        Retour :
            None
        """
        self.screen.fill(self.bg)
        for b in self.liste_balles:
            b.update_position(centre, self.vitesse_max_balle)
            b.draw(self.screen)

        pygame.draw.circle(self.screen, (255, 255, 255), (self.width // 2, self.height // 2), 200, width=3)

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
    def __init__(self, x, y, radius, color):
        self.position=np.array([x+10,y]).astype(float)
        self.vitesse=np.array([0,0]).astype(float)
        self.radius = radius
        self.color = color

    def draw(self, surface):
        """
        Dessine la balle sur la surface donnée.
        """
        pygame.draw.circle(surface, self.color, self.position, self.radius)

    def update_vitesse(self, vitesse_max_balle):
        # Accelerer vers le bas
        self.vitesse[1] += 0.3  # Ajouter une accélération vers le bas
        speed = np.linalg.norm(self.vitesse)
        if speed > vitesse_max_balle:
            self.vitesse = (self.vitesse / speed) * vitesse_max_balle
        print(self.vitesse)

    def update_position(self, centre, vitesse_max_balle):
        """
        Met à jour la position de la balle en fonction de sa vitesse et de la position du centre.
        """
        self.update_vitesse(vitesse_max_balle)
        direction=self.position-centre
        distance= np.linalg.norm(direction)
        if distance > 200- self.radius:
            if distance!=0:
                direction_normale = direction / distance
                self.vitesse = self.vitesse - 2*np.dot(self.vitesse, direction_normale) * direction_normale

        self.position += self.vitesse
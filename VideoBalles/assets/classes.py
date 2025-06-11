import pygame
import numpy as np

class Partie:
    def __init__(self, width, height, bg=(0, 0, 0)):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.bg = bg
        self.liste_balles = []

    def addBalle(self, x, y, radius, color):
        balle = Balle(x, y, radius, color)
        self.liste_balles.append(balle)

    def setPartie(self, centre):
        self.screen.fill(self.bg)
        for b in self.liste_balles:
            b.update_position(centre)
            b.draw(self.screen)

        pygame.draw.circle(self.screen, (255, 255, 255), (self.width // 2, self.height // 2), 200, width=3)

    def Afficher(self):
        pygame.display.flip()

    def getScreen(self): 
        return self.screen
    
    def makeScreenshot(self, frame):
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
        pygame.draw.circle(surface, self.color, self.position, self.radius)

    def update_vitesse(self, vitesse_max):
        # Accelerer vers le bas
        self.vitesse[1] += 0.3  # Ajouter une accélération vers le bas
        speed = np.linalg.norm(self.vitesse)
        if speed > vitesse_max:
            self.vitesse = (self.vitesse / speed) * vitesse_max
        print(self.vitesse)

    def update_position(self, centre):
        self.update_vitesse()
        direction=self.position-centre
        distance= np.linalg.norm(direction)
        if distance > 200- self.radius:
            if distance!=0:
                direction_normale = direction / distance
                self.vitesse = self.vitesse - 2*np.dot(self.vitesse, direction_normale) * direction_normale

        self.position += self.vitesse
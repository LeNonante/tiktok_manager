from random import randint

def generer_heures():
    heures = []
    for _ in range(3):  # Générer 3 heures aléatoires
        heure = f"{randint(0, 23):02}:{randint(0, 59):02}"
        heures.append(heure)
        
    while len(set(heures)) < 3:  # Assurer que les heures sont uniques
        heures = []
        for _ in range(3):  # Générer 3 heures aléatoires
            heure = f"{randint(0, 23):02}:{randint(0, 59):02}"
            heures.append(heure)

    heures.sort()
    return heures

heures_COMPLET = []

for i in range (3000):
     heures_COMPLET.extend(generer_heures())
    
with open(f"VideoBalles/assets/horaires/horaires.txt", "w") as f:
        f.write("\n".join(heures_COMPLET))
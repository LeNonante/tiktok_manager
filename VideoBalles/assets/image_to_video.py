import subprocess
import cv2
import os
from pathlib import Path
import mido
import copy

def create_video_from_images(folder_path, output_path="output_video.mp4", fps=60):    
    
    folder = Path(folder_path)

    images = []
    for ext in [".png", ".jpg", ".jpeg"]:
        images.extend(folder.glob(f'*{ext}'))
    
    # Trier les images par nom
    images.sort()

    print()

    image_list = [str(img) for img in images]

    print(f"Nb Images: {len(images)}")

    # Vérifier que le premier fichier existe pour obtenir les dimensions
    first_image_path = image_list[0]
    if not os.path.exists(first_image_path):
        print(f"Erreur: Le fichier {first_image_path} n'existe pas")
        return False
    
    # Lire la première image pour obtenir les dimensions
    first_frame = cv2.imread(first_image_path)
    if first_frame is None:
        print(f"Erreur: Impossible de lire l'image {first_image_path}")
        return False
    
    height, width, layers = first_frame.shape
    
    # Définir le codec et créer l'objet VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
    # Traiter chaque image
    for i, image_path in enumerate(image_list):
        if not os.path.exists(image_path):
            print(f"Attention: Le fichier {image_path} n'existe pas, ignoré")
            continue
            
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Attention: Impossible de lire {image_path}, ignoré")
            continue
        
        # Redimensionner l'image si nécessaire pour correspondre aux dimensions de la vidéo
        if frame.shape[:2] != (height, width):
            frame = cv2.resize(frame, (width, height))
        
        video_writer.write(frame)
        
        # Afficher le progrès
        if (i + 1) % 10 == 0 or i == len(image_list) - 1:
            print(f"Traité: {i + 1}/{len(image_list)} images")
    
    # Libérer les ressources
    video_writer.release()
    cv2.destroyAllWindows()
    
    print(f"Vidéo enregistrée : {output_path}")
    return True

def combine_video_audio(video_path, audio_path, output_path, fps=60):
    """
    Combine une vidéo et un fichier audio en utilisant ffmpeg
    
    Args:
        video_path (str): Chemin vers le fichier vidéo
        audio_path (str): Chemin vers le fichier audio
        output_path (str): Chemin de sortie pour la vidéo finale
        fps (int): Frames par seconde
    """
    try:
        # Vérifier que les fichiers existent
        if not os.path.exists(video_path):
            print(f"Erreur: Le fichier vidéo {video_path} n'existe pas")
            return False
        
        if not os.path.exists(audio_path):
            print(f"Erreur: Le fichier audio {audio_path} n'existe pas")
            return False
        
        # Commande ffmpeg pour combiner vidéo et audio
        cmd = [
            'ffmpeg',
            '-i', video_path,      # Fichier vidéo d'entrée
            '-i', audio_path,      # Fichier audio d'entrée
            '-c:v', 'copy',        # Copier le codec vidéo (pas de réencodage)
            '-c:a', 'aac',         # Encoder l'audio en AAC
            '-strict', 'experimental',
            '-shortest',           # Arrêter quand le plus court se termine
            '-y',                  # Écraser le fichier de sortie s'il existe
            output_path
        ]
        
        print(f"Combinaison de {video_path} et {audio_path}...")
        
        # Exécuter la commande
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Vidéo finale créée : {output_path}")
            return True
        else:
            print(f"Erreur ffmpeg : {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("Erreur: ffmpeg n'est pas installé ou n'est pas dans le PATH")
        print("Installez ffmpeg depuis https://ffmpeg.org/")
        return False
    except Exception as e:
        print(f"Erreur lors de la combinaison : {e}")
        return False
    
def boucler_midi(fichier_entree, fichier_sortie, nb_boucles=10):
    # Charger le fichier MIDI original
    midi_original = mido.MidiFile(fichier_entree)
    
    # Créer un nouveau fichier MIDI
    nouveau_midi = mido.MidiFile(ticks_per_beat=midi_original.ticks_per_beat)
    
    # Pour chaque piste dans le fichier original
    for piste_originale in midi_original.tracks:
        # Créer une nouvelle piste pour cette piste
        nouvelle_piste = mido.MidiTrack()
        
        # Répéter la piste nb_boucles fois
        for i in range(nb_boucles):
            # Copier tous les messages de la piste
            for msg in piste_originale:
                # Créer une copie du message
                nouveau_msg = msg.copy()
                
                # Pour la première boucle, garder le timing original
                # Pour les suivantes, ajuster seulement le premier message
                if i > 0 and msg == piste_originale[0] and hasattr(msg, 'time'):
                    # Optionnel : ajuster le timing si nécessaire
                    pass
                
                nouvelle_piste.append(nouveau_msg)
        
        # Ajouter la nouvelle piste au fichier
        nouveau_midi.tracks.append(nouvelle_piste)
    
    # Sauvegarder
    nouveau_midi.save(fichier_sortie)
    print(f"Fichier bouclé {nb_boucles} fois sauvegardé : {fichier_sortie}")
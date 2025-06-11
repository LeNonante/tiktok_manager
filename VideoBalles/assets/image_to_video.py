import cv2
import os
from pathlib import Path

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
print((1,3)-(2,2))
#create_video_from_images("VideoBalles/assets/screen", "resultat.mp4")
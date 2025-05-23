import pyktok as pyk
from moviepy import ImageClip, VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, vfx
#from moviepy import speedx



def DL_original(lien) :
    pyk.save_tiktok(lien,
                True,
                    'video_data.csv')


def EDIT_video(video) :
    # Charger la vidéo
    video = VideoFileClip("@tiktok_video_7011536772089924869.mp4")
    #Charger la musique
    #audio = AudioFileClip("ma_musique.mp3").subclip(0, video.duration)

   # 3. Ajouter une image (logo)
    logo = ImageClip("assets/LOGO.png")
    logo = logo.with_duration(video.duration) \
            .resized(height=80) \
            .with_position(("left", "top")) \
            .with_opacity(0.8)

    """
    # 4. Ajouter du texte
    texte = TextClip("TEST", fontsize=50, color='red')#, font='Arial-Bold', method='caption')
    texte = texte.with_duration(video.duration) \
                 .with_position(("center", "bottom"))
    """
    # 5. Modifier la vitesse de la vidéo
    #video_vitesse = speedx(video, 1.5)


    # 6. Combiner les éléments : vidéo, logo, texte
    final = CompositeVideoClip([logo])
    #final = final.set_audio(audio)

    # 7. Exporter la vidéo finale
    final.write_videofile("video_finale.mp4", fps=24, codec="libx264", audio_codec="aac")




#DL_original('https://www.tiktok.com/@tiktok/video/7011536772089924869?is_copy_url=1&is_from_webapp=v1')
EDIT_video('video_finale.mp4')
print('Video downloaded')
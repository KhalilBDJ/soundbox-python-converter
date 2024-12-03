from flask import Flask, request, jsonify
from pytube import YouTube
import moviepy
import os
import uuid

app = Flask(__name__)

# Dossier temporaire pour stocker les fichiers
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/convert', methods=['POST'])
def convert_to_mp3():
    try:
        # Récupérer l'URL de la vidéo depuis la requête
        data = request.json
        video_url = data.get('url')
        if not video_url:
            return jsonify({"error": "URL is required"}), 400

        # Télécharger la vidéo
        yt = YouTube(video_url)
        video = yt.streams.filter(only_audio=True).first()
        temp_file = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.mp4")
        video.download(filename=temp_file)

        # Convertir en MP3
        output_file = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.mp3")
        clip = moviepy.AudioFileClip(temp_file)
        clip.write_audiofile(output_file)
        clip.close()

        # Supprimer le fichier temporaire MP4
        os.remove(temp_file)

        # Retourner le fichier MP3
        return jsonify({"mp3_file": output_file}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

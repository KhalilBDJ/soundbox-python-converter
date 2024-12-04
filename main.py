import base64
from flask import Flask, request, jsonify
from pytube import YouTube
import os
import uuid

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_to_mp3():
    try:
        # Récupérer l'URL de la vidéo depuis la requête
        data = request.json
        video_url = data.get('url')
        if not video_url:
            return jsonify({"error": "URL is required"}), 400

        # Initialiser l'objet YouTube
        yt = YouTube(video_url)

        # Récupérer les informations de la vidéo
        try:
            video_title = yt.title
        except Exception as e:
            video_title = "Unknown Title"
            print(f"Warning: Unable to fetch video title. Error: {str(e)}")

        try:
            video_duration = yt.length
        except Exception as e:
            video_duration = 0
            print(f"Warning: Unable to fetch video duration. Error: {str(e)}")

        # Télécharger la vidéo en audio
        audio_stream = yt.streams.filter(only_audio=True).first()
        temp_file = f"{uuid.uuid4()}.mp4"
        audio_stream.download(filename=temp_file)

        # Lire les données du fichier et les encoder en Base64
        with open(temp_file, "rb") as audio_file:
            encoded_audio = base64.b64encode(audio_file.read()).decode("utf-8")

        # Supprimer le fichier temporaire
        os.remove(temp_file)

        # Retourner les données encodées et les informations de la vidéo
        return jsonify({
            "name": video_title,
            "duration": video_duration,
            "audio_base64": encoded_audio
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

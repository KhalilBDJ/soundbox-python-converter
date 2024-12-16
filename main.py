import base64
from flask import Flask, request, jsonify
import os
import uuid
from io import BytesIO
from pydub import AudioSegment
from pytubefix import YouTube

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
        return jsonify({"error": str(e)})


@app.route('/trim', methods=['POST'])
def trim_audio():
    try:
        # Récupérer les données de la requête
        data = request.json
        audio_base64 = data.get('audio_base64')
        start = data.get('start')
        end = data.get('end')

        if not audio_base64 or start is None or end is None:
            return jsonify({"error": "audio_base64, start, and end are required"}), 400

        # Décoder l'audio Base64
        audio_data = base64.b64decode(audio_base64)

        # Charger l'audio avec Pydub
        audio = AudioSegment.from_file(BytesIO(audio_data))

        # Convertir les temps en millisecondes
        start_ms = start * 1000
        end_ms = end * 1000

        # Découper l'audio
        trimmed_audio = audio[start_ms:end_ms]

        # Exporter l'audio découpé en mémoire
        output_buffer = BytesIO()
        trimmed_audio.export(output_buffer, format="mp3")

        # Encoder en Base64
        trimmed_audio_base64 = base64.b64encode(output_buffer.getvalue()).decode("utf-8")

        # Retourner l'audio découpé
        return jsonify({
            "trimmed_audio_base64": trimmed_audio_base64
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

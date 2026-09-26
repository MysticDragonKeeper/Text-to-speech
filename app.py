from flask import Flask, render_template, request, send_file
from io import BytesIO
import asyncio
import edge_tts

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


async def generate_speech(text):
    audio = BytesIO()

    communicate = edge_tts.Communicate(
        text,
        voice="en-US-AriaNeural"
    )

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.write(chunk["data"])

    audio.seek(0)
    return audio


@app.route("/speak", methods=["POST"])
def speak():
    text = request.form.get("text", "").strip()

    print(f"Received text length: {len(text)} characters")

    if not text:
        return "Please enter some text.", 400

    if len(text) > 20000:
        return "Text is too long. Maximum length is 20,000 characters.", 400

    try:
        print("Starting Edge TTS generation...")

        audio = asyncio.run(generate_speech(text))

        print("Edge TTS generation complete.")

        return send_file(
            audio,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="speech.mp3"
        )

    except Exception as e:
        print("TTS ERROR:", repr(e))
        return f"Speech generation failed: {str(e)}", 500


if __name__ == "__main__":
    app.run(debug=True)
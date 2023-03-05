import openai
import whisper
from whisper.utils import WriteVTT
from pytube import YouTube
import os

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = "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"


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        url = request.form["video_url"]
        translated_language = request.form["translated-language"]

        filename = audio_conversion(url)
        model = whisper.load_model("base")
        transcribed = model.transcribe(filename, fp16=False)

        with open('sub.vtt', "w") as txt:
            WriteVTT.write_result(self=WriteVTT, result=transcribed, file=txt)

        with open('sub.vtt', "r") as txt:
            result = '<br>'.join(txt.readlines()).replace('WEBVTT', '')

        translated = translate(result, translated_language)
        
        return redirect(url_for("index", result=result, translated=translated))
    
    result = request.args.get("result")
    translated = request.args.get("translated")
    return render_template("index.html", result=result, translated=translated)

def audio_conversion(vid_url):
    youtube = YouTube(vid_url)
    video = youtube.streams.filter(only_audio=True).first()
    destination = "C:/Users/User/Desktop/break the block/openai-quickstart-python-master"
    out_file = video.download(output_path=destination)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    print(youtube.title + " has been successfully downloaded.")

    return new_file

def translate(transcription, language):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt= f"Translate {transcription} into {language}",
        temperature=0.3,
        max_tokens=500,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    return response.choices[0].text
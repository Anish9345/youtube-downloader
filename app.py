from flask import Flask, render_template, request, send_file
from pytube import YouTube
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch():
    url = request.form['url']
    yt = YouTube(url)

    # Get video streams (mp4 only, progressive = video+audio)
    video_streams = yt.streams.filter(progressive=True, file_extension='mp4').all()

    # Get audio streams (for mp3 later)
    audio_streams = yt.streams.filter(only_audio=True).all()

    return render_template('choose.html', yt=yt, videos=video_streams, audios=audio_streams)

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    itag = request.form['itag']
    yt = YouTube(url)

    stream = yt.streams.get_by_itag(itag)
    filename = stream.download()

    # Convert to mp3 if audio
    if stream.mime_type == "audio/webm":
        base, ext = os.path.splitext(filename)
        new_file = base + '.mp3'
        os.rename(filename, new_file)
        filename = new_file

    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

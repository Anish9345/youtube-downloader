import os
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/fetch', methods=['POST'])
def fetch():
    url = request.form['url']

    ydl_opts = {'listformats': True}
    formats = []
    title = ""
    thumbnail = ""

    # Extract available formats
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get("title", "Video")
        thumbnail = info.get("thumbnail", "")
        for f in info['formats']:
            if f.get("ext") == "mp4" and f.get("height"):
                formats.append({
                    "format_id": f["format_id"],
                    "quality": f"{f['height']}p",
                    "ext": "mp4"
                })
            elif f.get("acodec") != "none" and f.get("vcodec") == "none":
                # audio only
                formats.append({
                    "format_id": f["format_id"],
                    "quality": f.get("abr", "128") + " kbps",
                    "ext": "mp3"
                })

    return render_template("choose.html", url=url, formats=formats, title=title, thumbnail=thumbnail)


@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_id = request.form['format_id']

    # temp filename
    outtmpl = "download.%(ext)s"

    ydl_opts = {
        'format': format_id,
        'outtmpl': outtmpl,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }] if format_id.endswith("mp3") else []
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    # if mp3, adjust filename
    if filename.endswith(".webm") or filename.endswith(".m4a"):
        filename = filename.rsplit(".", 1)[0] + ".mp3"

    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

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

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
        'noplaylist': True,
        'ignoreerrors': True,
        'extractor_args': {
            'youtube': {'player_client': ['web']}  # force web extractor
        }
    }

    formats = []
    title = ""
    thumbnail = ""

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        return f"❌ Failed to fetch video info: {str(e)}"

    if not info:
        return "❌ Could not fetch video info. This video may require login or is restricted."

    title = info.get("title", "Video")
    thumbnail = info.get("thumbnail", "")

    for f in info.get('formats', []):
        if f.get("ext") == "mp4" and f.get("height"):
            formats.append({
                "format_id": f["format_id"],
                "quality": f"{f['height']}p",
                "ext": "mp4"
            })
        elif f.get("acodec") != "none" and f.get("vcodec") == "none":
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

    outtmpl = "download.%(ext)s"
    ydl_opts = {
        'format': format_id,
        'outtmpl': outtmpl,
        'noplaylist': True,
        'ignoreerrors': True,
        'extractor_args': {
            'youtube': {'player_client': ['web']}
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }] if format_id.endswith("mp3") else []
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
    except Exception as e:
        return f"❌ Download failed: {str(e)}"

    if filename.endswith(".webm") or filename.endswith(".m4a"):
        filename = filename.rsplit(".", 1)[0] + ".mp3"

    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

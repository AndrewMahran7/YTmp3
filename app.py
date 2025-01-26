from flask import Flask, request, render_template, send_file
import os
from yt_dlp import YoutubeDL

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_type = request.form['format']

    # Ensure downloads directory exists
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # yt-dlp options
    options = {
        'format': 'bestaudio/best' if format_type == 'mp3' else 'bestvideo+bestaudio',
        'outtmpl': f'downloads/%(title)s.%(ext)s',
        'cookies': 'youtube-cookies.txt',  # Path to the cookies file
    }

    # Add postprocessor for MP3 conversion
    if format_type == 'mp3':
        options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        # Download the video
        with YoutubeDL(options) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)

        # Adjust filename for MP3 files
        if format_type == 'mp3':
            filename = filename.replace('.webm', '.mp3').replace('.m4a', '.mp3')

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Dynamically bind to the port Render assigns
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

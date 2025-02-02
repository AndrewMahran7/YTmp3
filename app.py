import os
from flask import Flask, request, render_template, send_file
from yt_dlp import YoutubeDL

app = Flask(__name__)

# Ensure downloads folder exists
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_type = request.form['format']

    # Set proxy
    PROXY = "http://167.71.48.245:8080"  # Replace with a working proxy

    # yt-dlp options with proxy and cookies
    options = {
        'format': 'bestaudio/best' if format_type == 'mp3' else 'bestvideo+bestaudio',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'cookies': os.path.abspath('youtube-cookies.txt'),  # Ensure absolute path
        'proxy': PROXY,  # Use proxy for requests
    }

    # Add MP3 conversion if needed
    if format_type == 'mp3':
        options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        # Debugging: Check if cookies file exists
        print(f"Checking cookies file at: {options['cookies']}")
        print("File exists:", os.path.exists(options['cookies']))

        # Download video using yt-dlp
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

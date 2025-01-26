from flask import Flask, request, render_template, send_file
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

# Ensure the downloads directory exists
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_type = request.form['format']

    # yt-dlp options with file-based cookies
    options = {
        'format': 'bestaudio/best' if format_type == 'mp3' else 'bestvideo+bestaudio',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'cookies': 'youtube-cookies.txt',  # Use the pre-exported cookies file
    }
    print("Cookies file exists:", os.path.exists('youtube-cookies.txt'))

    # Add postprocessor for MP3 conversion
    if format_type == 'mp3':
        options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        # Debugging: Ensure the cookies file exists
        if not os.path.exists('youtube-cookies.txt'):
            raise FileNotFoundError("Cookies file 'youtube-cookies.txt' not found. Ensure it's uploaded.")

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

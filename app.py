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

    # Get the absolute path to the cookies file
    cookies_path = os.path.abspath('youtube-cookies.txt')

    # Debugging: Check if the file exists
    print(f"Checking cookies file at: {cookies_path}")
    print("File exists:", os.path.exists(cookies_path))

    # yt-dlp options with cookies
    options = {
        'format': 'bestaudio/best' if format_type == 'mp3' else 'bestvideo+bestaudio',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'cookies': cookies_path,  # Use absolute path
    }

    # Add postprocessor for MP3 conversion
    if format_type == 'mp3':
        options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        # Check if cookies file exists before downloading
        if not os.path.exists(cookies_path):
            raise FileNotFoundError("Cookies file not found. Upload it to Render.")

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

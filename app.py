from flask import Flask, request, render_template, send_file
from yt_dlp import YoutubeDL
import os
import shutil

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

    options = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'cookies': os.path.join(os.getcwd(), 'youtube-cookies.txt'),  # Use absolute path
    }

    # Debugging: Print path to check if file exists
    print("Checking cookies file on Render:")
    print("File exists:", os.path.exists(options['cookies']))
    print("Absolute path:", options['cookies'])


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
            shutil.copy('static/youtube-cookies.txt', 'youtube-cookies.txt')  # Backup location

        else:
            raise FileExistsError("Cookies are in the file")
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

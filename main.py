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
    output_path = 'downloads'

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    try:
        # Set download options based on the requested format
        ydl_opts = {
            'format': 'bestaudio/best' if format_type == "mp3" else 'best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        }

        # Add postprocessors for MP3 conversion if needed
        if format_type == "mp3":
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        # Download the file
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

            # Adjust the file name if MP3 was requested
            if format_type == "mp3":
                file_name = file_name.rsplit('.', 1)[0] + '.mp3'

        return send_file(file_name, as_attachment=True)

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    #app.run(debug=True)

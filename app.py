from flask import Flask, render_template, request, make_response, flash, redirect, Response
from werkzeug.utils import secure_filename
from uuid import uuid4
from nightcorify import nightcorify
import os, sys, time, re
from multiprocessing import Process

# Create the flask app
app = Flask(__name__)

# Folder in which the temp files are stored and processed
app.config['UPLOAD_FOLDER'] = r'C:\Users\ruyil\OneDrive\Desktop\Python\nightcorify\temp'

# 64 MB max size
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024
app.secret_key = 'assassinationclassroomisthebestanime'

"""
TODO test all formats
Checklist: mp3, wav, ogg
Done!
"""
accepted_formats = set(['mp3', 'wav', 'ogg'])
mimetypes = {
    "mp3": 'audio/mpeg',
    "wav": 'audio/vnd.wav',
    "ogg": 'audio/ogg'
}

def valid_file(f):
    """
    Checks if the file name satisfies the following conditions:
    1. Name is not empty
    2. File has an extension
    3. File extension is accepted
    """
    return (not f == '') and ('.' in f) and (f.split('.')[-1].lower() in accepted_formats)

def remove_temp():
    while True:
        # Remove all temporary audio files
        try:
            for file in os.listdir("./temp"):
                os.remove(os.path.join("./temp", file))
            time.sleep(60)
        except:
            pass

@app.route('/', methods=['GET', 'POST'])
def index():
    # If the request is a POST request, perform the nightcorification
    if request.method == 'POST':

        # File in response body?
        if 'file' not in request.files:
            flash('File not found.')
            return redirect(request.url)

        # Valid audio format?
        audio = request.files['file']
        if not valid_file(audio.filename):
            flash('Invalid file and/or file type.')
            return redirect(request.url)

        # Strip all non-alphanumeric or non-"()[]-." characters
        name = re.sub(r'[^a-zA-Z\(\)\[\]\d\-\.]', '', re.sub(r'\s\t', '_', audio.filename))

        # http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
        fname = secure_filename('%s-%s' % (str(uuid4()), name))
        fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)

        # Create temp file
        tempname = 'nc-temp-%s-%s' % (str(uuid4()), fname)
        temppath = os.path.join(app.config['UPLOAD_FOLDER'], tempname)

        # Save audio file to specified secure path
        audio.save(fpath)

        # Nightcorify
        nightcorify(fpath, temppath)

        # Remove original
        os.remove(fpath)

        # Function to return a generator containing audio data of the nightcorified file
        def generate():
            with open(temppath, 'rb') as sound:
                data = sound.read(1024)
                while data:
                    yield data
                    data = sound.read(1024)
        try:
            response = Response(generate(), mimetype=mimetypes[name.split('.')[-1]], headers={ 'Content-Disposition': ('attachment;filename=nightcore-' + name) })
        except:
            flash("Unexpected error:", sys.exc_info()[0])
            return redirect(request.url)
        return response

    elif request.method == 'GET':
        # Render the main page in which they can access information about the service or upload a file to nightcorify.
        return render_template('index.html')

    # If the request is of any other method, return a 404
    # TODO change this to a proper 404 response error
    return make_response(render_template('index.html'), 404)
    

# Run the app.
if __name__ == '__main__':
    p = Process(target=remove_temp)
    p.start()
    app.run(debug=True)
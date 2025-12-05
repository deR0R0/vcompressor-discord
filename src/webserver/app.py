import flask
import os
from flask import request

from src.utils.jobmanager import get_user_id
from src.Config import VIDEO_FOLDER

app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
async def index():
    return "Please do not visit this page directly, but rather use the link the Discord Bot provided for you."


@app.route('/upload', methods=['GET', 'POST'])
async def upload():
    # we need a job id to track the upload
    if len(request.args) == 0:
        return "Invalid request. No parameters provided.", 400

    # check for job id so we can track which user sent the request
    job_id = request.args.get('job_id')
    if not job_id:
        return "Invalid request. No job_id provided.", 400

    # determine what to return
    if request.method == 'POST':
        return await handle_post(request, job_id)
    else:
        return await handle_get(job_id)

async def handle_post(request, job_id):
    # make sure they have a file
    if 'file' not in request.files:
        return "No file part in the request.", 400

    # get file
    file = request.files['file']
    if file.filename == '':
        return "No selected file.", 400
    
    # correct type
    if file.filename.rfind('.') == -1 or not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv', '.asf', '.ogg')):
        return "Invalid file type. Please upload a video file.", 400
    
    # get the user id
    user_id = get_user_id(int(job_id))
    if user_id == -1:
        return "This job is past expired."

    # save the file
    file.save(os.path.join(VIDEO_FOLDER, f"{str(user_id)}{file.filename[file.filename.rfind("."):]}"))

    return f"File '{file.filename}' uploaded successfully for job ID {job_id}.\nGo back to discord :D"

async def handle_get(job_id: str):
    # return the upload file form
    # this entire form is vibecoded. web dev sucks
    template = '''
    <html>
        <head>
            <meta charset="utf-8">
            <title>Upload Video File</title>
        </head>
        <body>
            <h1>Upload Video File</h1>
            <form id="uploadForm" action="/upload?job_id=__JOB_ID__" method="post" enctype="multipart/form-data">
                <input id="file" type="file" name="file" accept="video/*" required><br><br>
                <input type="submit" value="Upload">
            </form>
            <progress id="progress" value="0" max="100" style="display:none;"></progress>
            <p id="status"></p>
            <script>
                document.addEventListener('DOMContentLoaded', () => {
                    const form = document.getElementById('uploadForm');
                    const fileInput = document.getElementById('file');
                    const statusText = document.getElementById('status');
                    const progressBar = document.getElementById('progress');

                    form.addEventListener('submit', (event) => {
                        event.preventDefault();
                        if (!fileInput.files.length) {
                            statusText.textContent = 'Select a file before uploading.';
                            return;
                        }

                        const formData = new FormData();
                        formData.append('file', fileInput.files[0]);

                        const xhr = new XMLHttpRequest();
                        xhr.open('POST', '/upload?job_id=__JOB_ID__');

                        xhr.upload.addEventListener('loadstart', () => {
                            statusText.textContent = 'Uploading...';
                            progressBar.value = 0;
                            progressBar.style.display = 'inline-block';
                        });

                        xhr.upload.addEventListener('progress', (progressEvent) => {
                            if (progressEvent.lengthComputable) {
                                const percent = Math.round((progressEvent.loaded / progressEvent.total) * 100);
                                progressBar.value = percent;
                            }
                        });

                        xhr.addEventListener('load', () => {
                            if (xhr.status === 200) {
                                statusText.textContent = xhr.responseText;
                                fileInput.value = '';
                            } else {
                                statusText.textContent = 'Error: ' + xhr.responseText;
                            }
                        });

                        xhr.addEventListener('error', () => {
                            statusText.textContent = 'Network error while uploading. Please try again.';
                        });

                        xhr.addEventListener('loadend', () => {
                            progressBar.style.display = 'none';
                        });

                        xhr.send(formData);
                    });
                });
            </script>
        </body>
    </html>
    '''

    return template.replace('__JOB_ID__', job_id)

def run():
    app.run(host="0.0.0.0", port=1234, debug=False, load_dotenv=False)
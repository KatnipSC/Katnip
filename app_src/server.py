import os
import sys
import shutil
from flask import Flask, request, render_template, jsonify, send_file, after_this_request
from io import BytesIO

sys.path.append('app_static\\parse\\')
import parser

app = Flask(__name__, static_folder='../app_static', template_folder='../app_templates')

@app.route('/')
def homepage():
    """Displays the homepage."""
    
    return render_template('editor.html')

@app.route("/download/<id>")
def download_file(id):
    """Sends the corresponding sb3 project file to be downloaded on the client side."""
    
    # Create filename
    filename = f"program_{id}.sb3"
    
    return send_file(os.path.join(f"app_static\\generated_projects\\{id}", filename), as_attachment=True)

@app.route("/projects/<id>")
def serve_project(id):
    """Serves the generated Scratch 3 project."""
    
    # Create filename
    filename = f"program_{id}.sb3"

    @after_this_request
    def clear_files(response):
        """Remove the temporary file after serving."""
        
        file_path = f"app_static/generated_projects/{id}/"
        shutil.rmtree(file_path)

        return response

    # Read file into io object to avoid problems with deleting files in use
    with open(os.path.join(f"app_static/generated_projects/{id}/", filename), "rb") as f:
        file_data = BytesIO(f.read())

    return send_file(
        file_data,
        as_attachment=False,
        mimetype="application/zip",
        download_name=filename
    )

@app.route('/translate', methods=['POST'])
def translate():
    """Translates ScratchText language into an .SB3 file located at app_static/generated_projects/id/program.sb3"""
    
    code = request.data.decode('utf-8') # Decode code
    
    # Create code structure
    code = {"Stage": ["",[["Default-Blank", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgYGBgAAAABQABpfZFQAAAAABJRU5ErkJggg=="]]],
               "S1": [code, [["Smile","data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGPgFvwPAAFGARyS/G3DAAAAAElFTkSuQmCC"]]]
               }
    
    # Translate code
    project_parser = parser.project()
    project_parser.process_scrtxt(code) # Make this be all items not just 0th
    project_parser.write()
    
    return jsonify({"proj_id": project_parser.id})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
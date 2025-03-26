import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename, allowed_extensions):
    #Check if the file has an allowed extension.
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_upload_file(file, upload_folder):
    #Save an uploaded file with a secure filename.
    filename = secure_filename(file.filename)
    # Add a UUID to ensure uniqueness
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    return filepath

def get_student_folder(group_id, student_id):
    #Get the folder path for a specific student.
    base_path = current_app.config['uploads']
    return os.path.join(base_path, 'GROUPS', group_id, 'Students', student_id)

def get_test_results_path(group_id, student_id, subject, test_id):
    #Get the path to test results for a specific student.
    student_folder = get_student_folder(group_id, student_id)
    return os.path.join(student_folder, 'subjects', subject, test_id, 'evaluation_results', 'result.txt')
from flask import render_template, request, jsonify, redirect, url_for, flash
from services.ocr import ocr_engine
from services.nlp import similarity
from services.evaluator import evaluator
from app.utils import allowed_file, save_upload_file

def register_routes(app):
   
    @app.route('/')
    def index():
        #Home page route
        return 
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        #Handle file upload
        return
    @app.route('/results/<group_id>/<student_id>/<test_id>')
    def view_results(group_id, student_id, test_id):
        #View test results
        return 
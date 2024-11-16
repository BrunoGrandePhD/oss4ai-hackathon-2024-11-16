import logging
from flask import Blueprint, request, render_template, jsonify
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import os
from src.services.llm.classifier import process_clothing_image

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Blueprint
api = Blueprint('api', __name__)
socketio = SocketIO()

# Configure upload settings
UPLOAD_FOLDER = 'uploads/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route("/upload_image", methods=["POST"])
def upload_image():
    """Handle image upload and processing for clothing analysis"""
    try:
        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Process the image with the LLM
                analysis_result = process_clothing_image(filepath)
                
                # Log the analysis result for debugging
                logger.info(f"Analysis result: {analysis_result}")
                
                # Check if we got an error response
                if analysis_result.get('category') == 'error':
                    return jsonify({
                        'error': 'Analysis failed',
                        'details': analysis_result.get('description', 'Unknown error')
                    }), 500
                
                return jsonify({
                    'message': 'Image processed successfully',
                    'filename': filename,
                    'analysis': analysis_result
                }), 200
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                return jsonify({
                    'error': 'Error processing file',
                    'details': str(e)
                }), 500
        else:
            logger.error("Invalid file type")
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': 'Unexpected error',
            'details': str(e)
        }), 500
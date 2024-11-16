import logging
from flask import Blueprint, request, render_template, jsonify
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import os

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

@api.route("/", methods=["GET"])
def home():
    """Render the image upload page"""
    return render_template('image_upload.html')

@api.route("/upload_image", methods=["POST"])
def upload_image():
    """Handle image upload for clothing analysis"""
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
            
            logger.info(f"Successfully saved image: {filename}")
            return jsonify({
                'message': 'Image uploaded successfully',
                'filename': filename,
                'filepath': filepath
            }), 200
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return jsonify({'error': 'Error saving file'}), 500
    else:
        logger.error("Invalid file type")
        return jsonify({'error': 'Invalid file type'}), 400
import logging
from flask import Blueprint, request, render_template, jsonify
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import os
from src.services.llm.classifier import process_clothing_image
from src.utils.storage import ClosetStorage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Blueprint and storage
api = Blueprint('api', __name__)
socketio = SocketIO()
closet_storage = ClosetStorage()

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

@api.route("/upload_image", methods=["GET", "POST"])
def upload_image():
    """Handle image upload and processing for clothing analysis"""
    if request.method == "GET":
        return render_template('image_upload.html')
        
    if request.method == "POST":
        try:
            if 'file' not in request.files:
                logger.error("No file part in request")
                return jsonify({
                    'error': 'No file part',
                    'analysis': {
                        "category": "unknown",
                        "color": "unknown",
                        "style": "unknown",
                        "pattern": "unknown",
                        "season": "unknown",
                        "occasion": "unknown",
                        "description": "No file uploaded"
                    }
                }), 400
            
            file = request.files['file']
            
            if file.filename == '':
                logger.error("No selected file")
                return jsonify({
                    'error': 'No selected file',
                    'analysis': {
                        "category": "unknown",
                        "color": "unknown",
                        "style": "unknown",
                        "pattern": "unknown",
                        "season": "unknown",
                        "occasion": "unknown",
                        "description": "No file selected"
                    }
                }), 400
            
            if file and allowed_file(file.filename):
                try:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    
                    # Process the image
                    analysis_result = process_clothing_image(filepath)
                    
                    # Save to closet
                    item_id = closet_storage.add_item(analysis_result, filename)
                    
                    logger.info(f"Successfully processed and stored image: {filename}")
                    return jsonify({
                        'message': 'Image processed and stored successfully',
                        'filename': filename,
                        'item_id': item_id,
                        'analysis': analysis_result
                    }), 200
                    
                except Exception as e:
                    logger.error(f"Error processing file: {str(e)}", exc_info=True)
                    return jsonify({
                        'error': f'Error processing file: {str(e)}',
                        'analysis': {
                            "category": "error",
                            "color": "unknown",
                            "style": "unknown",
                            "pattern": "unknown",
                            "season": "unknown",
                            "occasion": "unknown",
                            "description": f"Error processing image: {str(e)}"
                        }
                    }), 500
            else:
                logger.error("Invalid file type")
                return jsonify({
                    'error': 'Invalid file type',
                    'analysis': {
                        "category": "unknown",
                        "color": "unknown",
                        "style": "unknown",
                        "pattern": "unknown",
                        "season": "unknown",
                        "occasion": "unknown",
                        "description": "Invalid file type"
                    }
                }), 400
                
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return jsonify({
                'error': f'Unexpected error: {str(e)}',
                'analysis': {
                    "category": "error",
                    "color": "unknown",
                    "style": "unknown",
                    "pattern": "unknown",
                    "season": "unknown",
                    "occasion": "unknown",
                    "description": f"Unexpected error: {str(e)}"
                }
            }), 500

@api.route("/closet", methods=["GET"])
def get_closet():
    """Get all items in the closet"""
    try:
        items = closet_storage.get_all_items()
        return jsonify({
            'items': items
        }), 200
    except Exception as e:
        logger.error(f"Error getting closet items: {e}")
        return jsonify({
            'error': f'Error getting closet items: {str(e)}'
        }), 500

@api.route("/closet/<item_id>", methods=["GET"])
def get_item(item_id):
    """Get a specific item from the closet"""
    try:
        item = closet_storage.get_item(item_id)
        if item is None:
            return jsonify({
                'error': 'Item not found'
            }), 404
        return jsonify(item), 200
    except Exception as e:
        logger.error(f"Error getting item {item_id}: {e}")
        return jsonify({
            'error': f'Error getting item: {str(e)}'
        }), 500
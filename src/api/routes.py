import logging
import os

from flask import Blueprint, jsonify, render_template, request, send_from_directory
from flask_socketio import SocketIO

from src.services.fashn.fashnClient import FashnClient
from src.services.llm.classifier import process_clothing_image
from src.services.llm.outfit_recommender import generate_outfit_recommendations
from src.services.llm.prompt_templates import clothing_item
from src.utils.storage import ClosetStorage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Blueprint and storage
api = Blueprint("api", __name__)
socketio = SocketIO()
closet_storage = ClosetStorage()


# Configure upload settings
UPLOAD_FOLDER = "uploads/images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if the file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route("/", methods=["GET"])
def home():
    """Render the image upload page"""
    return render_template("image_upload.html")


@api.route("/upload_image", methods=["GET", "POST"])
def upload_image():
    """Handle image upload and processing for clothing analysis"""
    if request.method == "GET":
        return render_template("image_upload.html")

    unknown_analysis = {k: "unknown" for k in clothing_item.keys()}

    if request.method == "POST":
        try:
            if "file" not in request.files:
                logger.error("No file part in request")
                return (
                    jsonify({"error": "No file part", "analysis": unknown_analysis}),
                    400,
                )

            file = request.files["file"]

            if file.filename == "":
                logger.error("No selected file")
                return (
                    jsonify(
                        {"error": "No selected file", "analysis": unknown_analysis}
                    ),
                    400,
                )

            if file and allowed_file(file.filename):
                try:
                    # Save image and get filepath
                    filename, filepath = closet_storage.save_image(file)

                    # Process the image
                    analysis_result = process_clothing_image(str(filepath))

                    # Save to closet with original file
                    item_id = closet_storage.add_item(analysis_result, file)

                    logger.info(f"Successfully processed and stored image: {filename}")
                    return (
                        jsonify(
                            {
                                "message": "Image processed and stored successfully",
                                "filename": filename,
                                "item_id": item_id,
                                "analysis": analysis_result,
                            }
                        ),
                        200,
                    )

                except Exception as e:
                    logger.error(f"Error processing file: {str(e)}", exc_info=True)
                    return (
                        jsonify(
                            {
                                "error": f"Error processing file: {str(e)}",
                                "analysis": unknown_analysis,
                            }
                        ),
                        500,
                    )
            else:
                logger.error("Invalid file type")
                return (
                    jsonify(
                        {"error": "Invalid file type", "analysis": unknown_analysis}
                    ),
                    400,
                )

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": f"Unexpected error: {str(e)}",
                        "analysis": unknown_analysis,
                    }
                ),
                500,
            )


@api.route("/images/<path:filename>")
def serve_image(filename):
    """Serve images from the data/images directory"""
    return send_from_directory(closet_storage.images_dir, filename)


@api.route("/closet", methods=["GET"])
def get_closet():
    """Get all items in the closet"""
    try:
        items = closet_storage.get_all_items()
        return jsonify({"items": items}), 200
    except Exception as e:
        logger.error(f"Error getting closet items: {e}")
        return jsonify({"error": f"Error getting closet items: {str(e)}"}), 500


@api.route("/closet/<item_id>", methods=["GET"])
def get_item(item_id):
    """Get a specific item from the closet"""
    try:
        item = closet_storage.get_item(item_id)
        if item is None:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item), 200
    except Exception as e:
        logger.error(f"Error getting item {item_id}: {e}")
        return jsonify({"error": f"Error getting item: {str(e)}"}), 500


@api.route("/closet/outfits", methods=["GET"])
def get_outfit_recommendations():
    """Get outfit recommendations with optional filters"""
    try:
        # Get query parameters with None as default
        occasion = request.args.get("occasion", None)
        season = request.args.get("season", None)
        style = request.args.get("style", None)

        outfit_recommendations = generate_outfit_recommendations(
            closet_storage, occasion=occasion, season=season, style=style
        )

        if outfit_recommendations is None:
            return jsonify({"error": "Outfit recommendations not found"}), 404

        outfit_recommendations_expanded = [
            {
                **outfit,
                "items": [
                    closet_storage.get_item(item_id) for item_id in outfit["items"]
                ],
            }
            for outfit in outfit_recommendations
        ]

        return jsonify(outfit_recommendations_expanded), 200

    except Exception as e:
        logger.error(f"Error getting outfit recommendations: {e}")
        return (
            jsonify({"error": f"Error getting outfit recommendations: {str(e)}"}),
            500,
        )


@api.route("/wearit", methods=["POST"])
def wear_item():
    """Wear an item of clothing"""

    try:
        fashnClient = FashnClient.getInstance()
        data = request.get_json()
        person_path = data.get("person_path")
        cloth_path = data.get("cloth_path")
        category = data.get("category")
        image_url, error = fashnClient.wear_it(person_path, cloth_path, category)
        if error:
            return jsonify({"error": error.message}), 500
        else:
            return (jsonify({"image_url": image_url})), 200
    except Exception as e:
        logger.error(f"Error wearing item: {str(e)}")
        return jsonify({"error": f"Error wearing item: {str(e)}"}), 500


@api.route("/outfits")
def outfits():
    """Render the outfits template"""
    try:
        return render_template("outfits.html")
    except Exception as e:
        logger.error(f"Error rendering outfits template: {str(e)}")
        return jsonify({"error": f"Error rendering outfits template: {str(e)}"}), 500

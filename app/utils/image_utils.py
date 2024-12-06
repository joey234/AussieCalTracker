import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image
import io

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file):
    """Save an uploaded image and return the filename."""
    try:
        # Read and process the image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Generate secure filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'food_{timestamp}.jpg'
        
        # Ensure upload folder exists
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])
        
        # Save the image
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        
        return filename
    except Exception as e:
        print(f"Error saving image: {str(e)}")
        return None

def delete_image(filename):
    """Delete an image file."""
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
    return False 
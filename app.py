import os
import logging
import time
from flask import Flask, render_template, request, jsonify, send_file, url_for
from bg_remover import remove_background
import tempfile
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Create temp directory for storing uploaded and processed images
TEMP_FOLDER = os.path.join(tempfile.gettempdir(), 'bg_remover')
os.makedirs(TEMP_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    try:
        # Check if we receive base64 data
        if request.is_json:
            data = request.get_json()
            if 'image_data' not in data:
                return jsonify({'error': 'No image data provided'}), 400
            
            # Get the base64 string and filename
            base64_data = data['image_data']
            original_filename = data.get('filename', 'image.png')
            
            # Check if the filename has valid extension
            if not original_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                return jsonify({'error': 'File format not supported. Please upload PNG, JPG, JPEG, or WEBP files'}), 400
            
            # Extract the base64 content (remove data:image/png;base64, part)
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Decode base64 to binary
            import base64
            image_data = base64.b64decode(base64_data)
            
            # Generate unique filenames
            input_filename = f"{uuid.uuid4().hex}_{original_filename}"
            input_path = os.path.join(TEMP_FOLDER, input_filename)
            
            # Save the image data to file
            with open(input_path, 'wb') as f:
                f.write(image_data)
                
        # Check for file upload (fallback for non-JS clients)
        elif 'image' in request.files:
            file = request.files['image']
            
            if file.filename == '':
                return jsonify({'error': 'No image selected'}), 400
            
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                return jsonify({'error': 'File format not supported. Please upload PNG, JPG, JPEG, or WEBP files'}), 400
            
            # Generate unique filenames
            input_filename = f"{uuid.uuid4().hex}_{file.filename}"
            input_path = os.path.join(TEMP_FOLDER, input_filename)
            
            # Save the uploaded file
            file.save(input_path)
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        # Process the image
        logging.debug(f"Starting background removal for {input_path}")
        output_path = remove_background(input_path)
        
        if not output_path:
            return jsonify({'error': 'Failed to process image'}), 500
        
        # Get just the filename for the response
        output_filename = os.path.basename(output_path)
        logging.debug(f"Background removed successfully. Result saved as {output_filename}")
        
        # Return the filename of processed image
        return jsonify({'success': True, 'filename': output_filename})
    
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.route('/processed/<filename>')
def get_processed_image(filename):
    file_path = os.path.join(TEMP_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='image/png')
    else:
        return jsonify({'error': 'File not found'}), 404

# Cleanup temporary files (can be enhanced with a scheduled task)
@app.route('/cleanup', methods=['POST'])
def cleanup_temp_files():
    try:
        for filename in os.listdir(TEMP_FOLDER):
            file_path = os.path.join(TEMP_FOLDER, filename)
            # Remove files older than 1 hour (can be adjusted)
            if os.path.isfile(file_path) and (time.time() - os.path.getmtime(file_path)) > 3600:
                os.remove(file_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

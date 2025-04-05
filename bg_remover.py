import os
import logging
import uuid
import tempfile
from gradio_client import Client, handle_file

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def remove_background(image_path):
    """
    Remove background from image using Gradio client
    
    Args:
        image_path: Path to the input image
        
    Returns:
        Path to the processed image or None if processing failed
    """
    try:
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join(tempfile.gettempdir(), 'bg_remover')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate output filename
        output_filename = f"{uuid.uuid4().hex}_no_bg.png"
        output_path = os.path.join(temp_dir, output_filename)
        
        logging.debug(f"Removing background from image: {image_path}")
        logging.debug(f"Output will be saved to: {output_path}")
        
        # Initialize Gradio client
        client = Client("abdullahalioo/remove_background")
        
        # Process the image
        result = client.predict(
            image=handle_file(image_path),
            api_name="/predict"
        )
        
        logging.debug(f"Gradio client returned: {result}")
        
        # Save the processed image from result (assuming result is the path to processed image)
        if isinstance(result, str) and os.path.exists(result):
            # If result is a file path, copy it to our output path
            import shutil
            shutil.copy(result, output_path)
        else:
            # If result is the actual image data, save it directly
            with open(output_path, 'wb') as f:
                if isinstance(result, bytes):
                    f.write(result)
                else:
                    f.write(result.encode('utf-8'))
        
        return output_path
    
    except Exception as e:
        logging.error(f"Error in background removal: {str(e)}")
        return None

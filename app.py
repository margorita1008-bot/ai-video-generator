from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import replicate
import os
import tempfile
import requests
from werkzeug.utils import secure_filename
import uuid
import base64
from io import BytesIO
import logging
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configure Replicate
os.environ['REPLICATE_API_TOKEN'] = 'r8_epSDg4LMRstkweQhis84p8fzj2P10oT3ldG50'

# Create uploads directory
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    logger.info("Home page accessed")
    return render_template('index.html')

@app.route('/validate_url', methods=['POST'])
def validate_url():
    data = request.get_json()
    image_url = data.get('image_url')
    
    logger.info(f"URL validation requested for: {image_url}")
    
    if not image_url:
        logger.warning("URL validation failed: No URL provided")
        return jsonify({'error': 'Image URL is required'}), 400
    
    # Basic URL validation
    if not (image_url.startswith('http://') or image_url.startswith('https://')):
        logger.warning(f"URL validation failed: Invalid URL format - {image_url}")
        return jsonify({'error': 'Please enter a valid URL starting with http:// or https://'}), 400
    
    # Test if the URL is accessible
    try:
        logger.info(f"Testing URL accessibility: {image_url}")
        response = requests.head(image_url, timeout=10)
        if response.status_code == 200:
            logger.info(f"URL validation successful: {image_url}")
            return jsonify({'success': True, 'image_url': image_url})
        else:
            logger.warning(f"URL validation failed: HTTP {response.status_code} - {image_url}")
            return jsonify({'error': 'Image URL is not accessible'}), 400
    except Exception as e:
        logger.error(f"URL validation error: {str(e)} - {image_url}")
        return jsonify({'error': f'Cannot access image URL: {str(e)}'}), 400

@app.route('/generate', methods=['POST'])
def generate_video():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        image_url = data.get('image_url')
        duration = data.get('duration', 5)
        negative_prompt = data.get('negative_prompt', '')
        
        logger.info(f"Video generation request started - Prompt: '{prompt[:50]}...', Image: {image_url}, Duration: {duration}s")
        
        if not prompt:
            logger.warning("Video generation failed: No prompt provided")
            return jsonify({'error': 'Prompt is required'}), 400
        
        if not image_url:
            logger.warning("Video generation failed: No image URL provided")
            return jsonify({'error': 'Image URL is required'}), 400
        
        # Log the parameters being sent to Replicate
        replicate_params = {
            "mode": "standard",
            "prompt": prompt,
            "duration": duration,
            "start_image": image_url,
            "negative_prompt": negative_prompt
        }
        logger.info(f"Calling Replicate API with parameters: {replicate_params}")
        
        # Call Replicate API
        start_time = datetime.now()
        logger.info("Starting Replicate API call - this will poll for completion...")
        
        output = replicate.run(
            "kwaivgi/kling-v2.1",
            input=replicate_params
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Replicate API call completed in {generation_time:.2f} seconds")
        logger.info("Note: The multiple HTTP requests you see are Replicate's polling mechanism checking generation status")
        
        # Get the video URL
        logger.info(f"Video output: {output}")
        
        # Handle different output types
        if hasattr(output, 'url'):
            video_url = output.url()
        elif isinstance(output, str):
            video_url = output
        elif isinstance(output, list) and len(output) > 0:
            video_url = output[0]
        else:
            logger.error(f"Unexpected output format: {type(output)} - {output}")
            raise ValueError(f"Unexpected output format: {type(output)}")
        
        logger.info(f"Video generated successfully: {video_url}")
        
        return jsonify({
            'success': True,
            'video_url': video_url,
            'message': 'Video generated successfully!'
        })
        
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500

@app.route('/logs')
def view_logs():
    """View application logs"""
    try:
        if os.path.exists('app.log'):
            with open('app.log', 'r') as f:
                logs = f.read()
            return f"<pre>{logs}</pre>"
        else:
            return "No logs found"
    except Exception as e:
        logger.error(f"Failed to read logs: {str(e)}")
        return f"Error reading logs: {str(e)}"

@app.route('/download/<path:video_url>')
def download_video(video_url):
    try:
        logger.info(f"Video download requested: {video_url}")
        
        # Download the video from the URL
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        logger.info(f"Video download started, content-length: {response.headers.get('content-length', 'unknown')}")
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        # Write the video content to the temporary file
        bytes_written = 0
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
            bytes_written += len(chunk)
        
        temp_file.close()
        logger.info(f"Video download completed: {bytes_written} bytes written")
        
        return send_file(temp_file.name, as_attachment=True, download_name='generated_video.mp4')
        
    except Exception as e:
        logger.error(f"Video download failed: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

if __name__ == '__main__':
    logger.info("Starting AI Video Generator application")
    logger.info("Application configured with Replicate API")
    app.run(debug=True)

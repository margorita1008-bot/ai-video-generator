# AI Video Generator

A web application that generates videos using AI prompts and start images, powered by Replicate's Kling v2.1 model.

## Features

- Generate videos from text prompts and start images
- Support for JPG, PNG, and SVG image formats
- Customizable video duration (1-10 seconds)
- Optional negative prompts
- Black and white minimalist UI
- Direct video download functionality

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## Usage

1. **Enter a video prompt** - Describe the video you want to generate
2. **Upload a start image** - Choose a JPG, PNG, or SVG image file
3. **Set duration** - Choose video length (1-10 seconds)
4. **Add negative prompt** (optional) - Describe what you don't want in the video
5. **Click "Generate Video"** - Wait for the AI to create your video
6. **Download the result** - Save the generated video to your device

## API Integration

This application uses Replicate's Kling v2.1 model with the following configuration:
- Mode: Standard
- Duration: 1-10 seconds
- Start image: User uploaded image
- Negative prompt: Optional user input

## File Structure

```
├── app.py              # Flask backend application
├── templates/
│   └── index.html      # Frontend HTML template
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Notes

- The application requires an internet connection to access Replicate's API
- Video generation may take several minutes depending on complexity
- Maximum file upload size is 16MB
- Generated videos are temporary and should be downloaded promptly

## API Behavior

The Replicate API uses a polling mechanism for video generation:
1. **Initial request** starts the generation process
2. **Multiple polling requests** check the status every few seconds
3. **Completion** when the video is ready

This is normal behavior - you'll see many HTTP requests in the logs as the API polls for completion. This is how Replicate's async processing works.

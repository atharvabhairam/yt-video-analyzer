# Video Analyzer Documentation

## 1. Package Imports and Their Purpose

### Core Dependencies
```python
import streamlit as st 
```
**Purpose**: Streamlit is a web application framework that makes it easy to create web apps for data science and machine learning projects.
- Used for creating the web interface, buttons, file uploads, and displaying results
- Example: `st.title("My App")` creates a title on the webpage

```python
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
```
**Purpose**: Phidata provides tools for building AI agents and using AI models
- `Agent`: Creates an AI agent that can process tasks
- `Gemini`: Google's AI model for processing text and images/videos
- `DuckDuckGo`: Tool for web searches
- Example:
```python
agent = Agent(
    name="My Agent",
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[DuckDuckGo()]
)
```

```python
from google.generativeai import upload_file, get_file
import google.generativeai as genai
```
**Purpose**: Google's Generative AI library for interacting with Gemini models
- Used for uploading and processing video files
- Example:
```python
processed_file = upload_file("video.mp4")
result = get_file(processed_file.name)
```

```python
from pytube import YouTube
```
**Purpose**: Library for downloading YouTube videos
- Used to download videos from YouTube URLs for processing
- Example:
```python
yt = YouTube("https://youtube.com/watch?v=...")
video = yt.streams.first()
video.download()
```

### Utility Imports
```python
import os
from dotenv import load_dotenv
from pathlib import Path
import tempfile
from urllib.parse import urlparse, parse_qs
import requests
import time
```
**Purpose**: Various utility functions for:
- Environment variables (dotenv)
- File handling (os, Path)
- Temporary file management (tempfile)
- URL parsing (urlparse, parse_qs)
- HTTP requests (requests)
- Time operations (time)

## 2. Custom Functions Overview

### URL Processing Functions

#### `extract_video_id(url)`
**Purpose**: Extracts the video ID from a YouTube URL
```python
# Example Usage:
url = "https://www.youtube.com/watch?v=abc123"
video_id = extract_video_id(url)  # Returns "abc123"

url = "https://youtu.be/abc123"
video_id = extract_video_id(url)  # Returns "abc123"
```

#### `is_valid_youtube_url(url)`
**Purpose**: Validates if a given URL is a working YouTube video link
```python
# Example Usage:
url = "https://www.youtube.com/watch?v=abc123"
if is_valid_youtube_url(url):
    print("Valid YouTube URL")
else:
    print("Invalid URL")
```

#### `download_youtube_video(url)`
**Purpose**: Downloads a YouTube video to a temporary file
```python
# Example Usage:
url = "https://www.youtube.com/watch?v=abc123"
video_path = download_youtube_video(url)
# Returns path to temporary file containing the video
```

### Agent Initialization

#### `initialize_agent()`
**Purpose**: Creates and caches the AI agent instance
```python
# Example Usage:
agent = initialize_agent()
response = agent.run("Analyze this video")
```

## 3. Program Flow

### 1. Application Setup
1. Loads environment variables (API keys)
2. Configures page layout and title
3. Initializes the AI agent

### 2. User Interface Components
The app provides two input methods via tabs:

#### Tab 1: Video Upload
- Users can upload video files directly
- Supports mp4, mov, and avi formats
- Example:
```python
video_file = st.file_uploader("Upload a video file", type=['mp4', 'mov', 'avi'])
```

#### Tab 2: YouTube URL
- Users can enter YouTube video URLs
- Supports both full and shortened URLs
- Example:
```python
youtube_url = st.text_input("Enter YouTube Video URL")
```

### 3. Video Processing Flow

#### For Uploaded Videos:
1. User uploads video file
2. File is saved to temporary location
3. Video is displayed in the UI
4. When analysis is requested:
   - Video is processed using Gemini
   - Results are displayed

#### For YouTube Videos:
1. User enters YouTube URL
2. URL is validated
3. Video is displayed using iframe
4. When analysis is requested:
   - Video is downloaded
   - Processed using Gemini
   - Results are displayed

### 4. Analysis Process
1. User enters their query about the video
2. Clicks "Analyze Video" button
3. System:
   - Processes video through Gemini
   - Generates analysis based on query
   - Displays results
   - Cleans up temporary files

## 4. Understanding Gen-AI Components

### What is Gemini?
- Gemini is Google's multimodal AI model
- Can understand and analyze:
  - Text
  - Images
  - Videos
  - Combinations of these

### How the AI Agent Works
1. **Input Processing**:
   - Takes your video (uploaded or YouTube)
   - Processes it into a format Gemini can understand

2. **Analysis**:
   - Uses Gemini to "watch" the video
   - Understands the content
   - Can answer questions about what it sees

3. **Response Generation**:
   - Creates human-readable responses
   - Can focus on specific aspects you ask about

### Example Usage
If you upload a cooking video and ask "What ingredients were used?", the agent will:
1. Process the video
2. Identify ingredients it sees
3. List them in a structured response

## 5. Error Handling

The application includes error handling for:
- Invalid YouTube URLs
- Failed video downloads
- Processing errors
- Temporary file cleanup

Each error is displayed to the user with a clear message explaining what went wrong.

## 6. Best Practices

When using the application:
1. Use clear, specific questions
2. Ensure videos are accessible
3. For YouTube videos, use official URLs
4. Wait for processing to complete
5. Check error messages if something fails


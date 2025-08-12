import streamlit as st 
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from google.generativeai import upload_file, get_file
import google.generativeai as genai
import requests
import time
from pathlib import Path
import tempfile
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from pytube import YouTube
import yt_dlp
load_dotenv()

import os

API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Page configuration
st.set_page_config(
    page_title="Multimodal AI Agent- Video Analyzer",
    page_icon="🎥",
    layout="wide"
)

st.title("AI Video Analyzer Agent 🎥🎤🖬")
st.header("Powered by Gemini 2.0 Flash Exp")

def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    # For full YouTube URLs
    parsed_url = urlparse(url)
    if 'youtube.com' in parsed_url.netloc:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    # For shortened youtu.be URLs
    elif 'youtu.be' in parsed_url.netloc:
        return parsed_url.path[1:]
    return None

def is_valid_youtube_url(url):
    """Validate YouTube URL and check if video exists."""
    video_id = extract_video_id(url)
    if not video_id:
        return False
    
    # Check if video exists using YouTube oEmbed endpoint
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}"
    try:
        response = requests.get(oembed_url)
        return response.status_code == 200
    except:
        return False

def download_youtube_video(url):
    """Download YouTube video using yt-dlp."""
    try:
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'worst[ext=mp4]',  # Get lowest quality mp4
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Update output template to use temporary directory
            ydl_opts['outtmpl'] = os.path.join(temp_dir, '%(id)s.%(ext)s')
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = os.path.join(temp_dir, f"{info['id']}.mp4")
                
                # Copy to a new temporary file that will persist
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                    with open(video_path, 'rb') as video_file:
                        temp_file.write(video_file.read())
                    return temp_file.name
                    
    except Exception as e:
        raise Exception(f"Error downloading YouTube video: {str(e)}")

@st.cache_resource
def initialize_agent():
    return Agent(
        name="Video AI Analyzer",
        model=Gemini(id="gemini-2.0-flash-exp"),
        tools=[DuckDuckGo()],
        markdown=True,
    )

## Initialize the agent
multimodal_Agent = initialize_agent()

# Create tabs for different input methods
tab1, tab2 = st.tabs(["Upload Video", "YouTube URL"])

with tab1:
    # File uploader
    video_file = st.file_uploader(
        "Upload a video file", type=['mp4', 'mov', 'avi'], help="Upload a video for AI analysis"
    )

    if video_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            temp_video.write(video_file.read())
            video_path = temp_video.name

        st.video(video_path, format="video/mp4", start_time=0)

with tab2:
    # YouTube URL input
    youtube_url = st.text_input(
        "Enter YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/...",
        help="Enter a valid YouTube video URL for analysis"
    )

    if youtube_url:
        if is_valid_youtube_url(youtube_url):
            video_id = extract_video_id(youtube_url)
            st.components.v1.iframe(
                f"https://www.youtube.com/embed/{video_id}",
                height=400,
                # allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            )
        else:
            st.error("Please enter a valid YouTube URL")

# Common analysis section
if (video_file or (youtube_url and is_valid_youtube_url(youtube_url))):
    user_query = st.text_area(
        "What insights are you seeking from the video?",
        placeholder="Ask anything about the video content. The AI agent will analyze and gather additional context if needed.",
        help="Provide specific questions or insights you want from the video."
    )

    if st.button("🔍 Analyze Video", key="analyze_video_button"):
        if not user_query:
            st.warning("Please enter a question or insight to analyze the video.")
        else:
            temp_files = []  # Keep track of temporary files
            try:
                with st.spinner("Processing video and gathering insights..."):
                    if video_file:
                        video_path = temp_video.name
                    else:
                        # Download YouTube video to a temporary file
                        video_path = download_youtube_video(youtube_url)
                        temp_files.append(video_path)

                    # Process the video file
                    processed_video = upload_file(video_path, mime_type="video/mp4")
                    while processed_video.state.name == "PROCESSING":
                        time.sleep(1)
                        processed_video = get_file(processed_video.name)

                    # Prompt generation for analysis
                    analysis_prompt = f"""
                        Analyze the video for content and context.
                        Respond to the following query using video insights and supplementary web research:
                        {user_query}

                        Provide a detailed, user-friendly, and actionable response.
                    """

                    # AI agent processing
                    response = multimodal_Agent.run(analysis_prompt, videos=[processed_video])

                # Display the result
                st.subheader("Analysis Result")
                st.markdown(response.content)

            except Exception as error:
                st.error(f"An error occurred during analysis: {error}")
            finally:
                # Clean up all temporary files
                for temp_file in temp_files:
                    Path(temp_file).unlink(missing_ok=True)
                if video_file:
                    Path(video_path).unlink(missing_ok=True)
else:
    st.info("Upload a video file or enter a YouTube URL to begin analysis.")

# Customize text area height
st.markdown(
    """
    <style>
    .stTextArea textarea {
        height: 100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
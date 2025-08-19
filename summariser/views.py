from django.shortcuts import render
from dotenv import load_dotenv
from .forms import YtForm
import os
import time
import requests
from google.api_core.exceptions import ServiceUnavailable
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Extract transcript
def extract_transcript_details(youtube_video_url):
    try:
        if "v=" in youtube_video_url:
            video_id = youtube_video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[1].split("?")[0]
        else:
            raise ValueError("Invalid YouTube URL format")

        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript, video_id
    except Exception as e:
        raise e

# Generate summary with Gemini
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    max_retries = 3
    for i in range(max_retries):
        try:
            response = model.generate_content(prompt + transcript_text)
            return response.text
        except (requests.exceptions.ConnectionError, ServiceUnavailable) as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(2)  # wait before retry
    return "Failed to generate summary due to network issue."

# Main view
def home(request):
    prompt = """You are a YouTube video summarizer. 
    Summarize the transcript in points (max 250 words).
    """

    summary = ''
    video_id = None

    if request.method == 'POST':
        form = YtForm(request.POST)
        if form.is_valid():
            link = form.cleaned_data['Link']
            transcript_text, video_id = extract_transcript_details(link)
            if transcript_text:
                summary = generate_gemini_content(transcript_text, prompt)
    else:
        form = YtForm()

    context = {
        "form": form,
        "response": summary,
        "video_id": video_id
    }
    return render(request, "yt.html", context)

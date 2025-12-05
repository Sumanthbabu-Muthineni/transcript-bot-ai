"""
YouTube Transcript Extraction Module
Handles extraction of transcripts from YouTube videos
"""
import re
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

# Note: YouTube blocks AWS IPs. For production, use proxies or YouTube Data API.
# For POC/demo, this works with cookies or from non-cloud IPs.


def extract_video_id(url):
    """
    Extract video ID from various YouTube URL formats
    Supports: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/embed/ID
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/v\/)([a-zA-Z0-9_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError("Invalid YouTube URL format")


def get_transcript(video_url):
    """
    Fetch transcript from YouTube video
    Returns concatenated transcript text
    """
    try:
        video_id = extract_video_id(video_url)
        print(f"   Video ID extracted: {video_id}")

        # Use the new API (v1.2.3+) - instance method instead of static
        # Try with proxies if configured (for AWS Lambda)
        proxies = {}
        http_proxy = os.getenv('HTTP_PROXY')
        https_proxy = os.getenv('HTTPS_PROXY')

        if http_proxy or https_proxy:
            if http_proxy:
                proxies['http'] = http_proxy
            if https_proxy:
                proxies['https'] = https_proxy
            print(f"   Using proxy configuration")
            ytt_api = YouTubeTranscriptApi(proxies=proxies)
        else:
            ytt_api = YouTubeTranscriptApi()

        # Fetch transcript - returns transcript object
        transcript = ytt_api.fetch(video_id)

        # Convert to raw data (list of dicts with 'text', 'start', 'duration')
        transcript_data = transcript.to_raw_data()

        print(f"   ✓ Transcript fetched: {len(transcript_data)} segments")

        # Combine all transcript segments into single text
        full_transcript = " ".join([segment['text'] for segment in transcript_data])

        return {
            'success': True,
            'video_id': video_id,
            'transcript': full_transcript,
            'length': len(full_transcript)
        }

    except TranscriptsDisabled:
        return {
            'success': False,
            'error': 'Transcripts are disabled for this video'
        }
    except NoTranscriptFound:
        return {
            'success': False,
            'error': 'No transcript/captions found for this video. Please try a video with captions enabled.'
        }
    except VideoUnavailable:
        return {
            'success': False,
            'error': 'Video is unavailable (may be private, age-restricted, or deleted)'
        }
    except ValueError as e:
        return {
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        error_msg = str(e)
        print(f"   Debug - Full error: {error_msg}")
        print(f"   Error type: {type(e).__name__}")
        return {
            'success': False,
            'error': f'Error fetching transcript: {error_msg}'
        }

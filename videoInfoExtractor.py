from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import re


class VideoInfoExtractor:
    def __init__(self, video_url):
        self.video_url = video_url

    def extract_video_id(self, video_url):
        self.video_url = video_url
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url)
        if not match:
            raise ValurError("Invalid Youtube URL")
        video_id = match.group(1)
        return video_id
    
    def extract_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([t["text"] for t in transcript])
        except Exception as e:
            return None
        
    def extract_metadata(self):
        yt = Youtube(self.video_url)
        return{
            "title": yt.title,
            "description": yt.description,
            "author": yt.author,
            "published_date": yt.publish_date,
            "views": yt.views,
            "likes": yt.likes,
            "comments": yt.comments,
            "duration": yt.length,
            "thumbnail_url": yt.thumbnail_url,
            "tags": yt.tags,
        }
    def extract_info(self, transcript, metadata):
        # combine transcript and metadata for context
        context = f"Title: {metadata['title']}\nDescription: {metadata['description']}\nTranscript: {transcript}"
        
        return context





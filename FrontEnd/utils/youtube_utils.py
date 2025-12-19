import os
import logging
from googleapiclient.discovery import build
import re

logger = logging.getLogger(__name__)

def extract_video_id(url):
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^\s\/\?\&]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\\?v=([^\s\&]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_comments_from_video(video_url, max_comments=50):
    api_key = os.getenv("YOUTUBE_API_KEY")
    video_id = extract_video_id(video_url)

    logger.info(f"YouTube URL: {video_url}")
    logger.info(f"Video ID  : {video_id}")
    logger.info(f"API key?  : {'ya' if api_key else 'tidak'}")

    if not video_id:
        logger.warning("Video ID tidak valid.")
        return []

    if not api_key:
        logger.error("API Key tidak tersedia.")
        return []

    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText"
        )
        response = request.execute()

        items = response.get("items", [])
        if not items:
            logger.warning("Tidak ada komentar ditemukan.")
            return []

        comments = []
        for item in items:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
            if len(comments) >= max_comments:
                break

        logger.info(f"Berhasil ambil {len(comments)} komentar.")
        return comments

    except Exception as e:
        logger.exception(f"ERROR saat ambil komentar: {e}")
        return []

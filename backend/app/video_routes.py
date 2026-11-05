"""YouTube Data API v3 search, cached. No downloading or scraping videos."""
import asyncio
import json
import os
import time
import urllib.parse
import urllib.request
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix='/api/learning/videos', tags=['learning-videos'])
_cache = {}
_CACHE_SECONDS = 3600


def _search_youtube(query, key):
    params = urllib.parse.urlencode({
        'part': 'snippet', 'type': 'video', 'videoEmbeddable': 'true',
        'videoSyndicated': 'true', 'safeSearch': 'strict',
        'maxResults': 6, 'relevanceLanguage': 'vi',
        'q': query, 'key': key,
    })
    req = urllib.request.Request('https://www.googleapis.com/youtube/v3/search?' + params,
                                 headers={'User-Agent': 'MATHWEB-Learning/1.0'})
    with urllib.request.urlopen(req, timeout=7) as response:
        data = json.load(response)
    items = []
    for item in data.get('items', []):
        vid = item.get('id', {}).get('videoId', '')
        if len(vid) == 11 and all(c.isalnum() or c in '_-' for c in vid):
            snippet = item.get('snippet', {})
            items.append({'id': vid, 'title': snippet.get('title', ''),
                          'channel': snippet.get('channelTitle', ''),
                          'thumbnail': f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'})
    return items


@router.get('')
async def learning_videos(grade: int = Query(..., ge=10, le=12),
                          topic: str = Query(..., min_length=2, max_length=120)):
    topic = ' '.join(topic.split())
    key = os.environ.get('YOUTUBE_API_KEY', '').strip()
    if not key:
        return {'videos': [], 'configured': False,
                'message': 'Cần cấu hình YOUTUBE_API_KEY trên backend để tự tìm video.'}
    cache_key = (grade, topic.lower())
    cached = _cache.get(cache_key)
    if cached and time.monotonic() - cached[0] < _CACHE_SECONDS:
        return {'videos': cached[1], 'configured': True, 'cached': True}
    try:
        videos = await asyncio.to_thread(_search_youtube, f'Toán {grade} {topic} bài giảng', key)
    except Exception as exc:
        raise HTTPException(status_code=503, detail='Không thể truy vấn video YouTube lúc này.') from exc
    if len(_cache) > 400:
        _cache.clear()
    _cache[cache_key] = (time.monotonic(), videos)
    return {'videos': videos, 'configured': True, 'cached': False}

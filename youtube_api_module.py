import aiohttp
from datetime import datetime, timedelta


API_KEY = 'AIzaSyC1kjO6Zsh7OAqipegtvOIQA6S6gMORyh0'


async def search_video(api_key: str, query: str, region_code: str = "RU") -> dict:
    search_url = "https://www.googleapis.com/youtube/v3/search"
    one_month_ago = (datetime.now() - timedelta(days=30)).isoformat("T") + "Z"
    search_params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "regionCode": region_code,
        "order": "relevance",
        "videoDuration": "medium",
        "publishedAfter": one_month_ago,
        "maxResults": 30,
        "key": api_key,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=search_url, params=search_params) as response:
            if response.status != 200:
                print(f"Ошибка: {response.status}")
                return {}
            searched_data = await response.json()
            video_ids = [item['id']['videoId'] for item in searched_data['items']]
            channel_ids = [item['snippet']['channelId'] for item in searched_data['items']]
            return {'video_ids': video_ids, 'channel_ids': channel_ids}


async def video_analytics(api_key: str, video_id_list: list) -> dict:
    videos_url = "https://www.googleapis.com/youtube/v3/videos"
    videos_params = {
        "part": "snippet,statistics",
        "id": ",".join(video_id_list),
        "key": api_key,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=videos_url, params=videos_params) as response:
            if response.status != 200:
                print(f"Ошибка: {response.status}")
                return {}
            videos_data = await response.json()
            video_info = {
                video['id']: {
                    "channel_id": video['snippet']['channelId'],
                    "view_count": video['statistics']['viewCount']
                }
                for video in videos_data['items']
            }
            video_info['type'] = 'video_data'
            return video_info


async def channel_analytics(api_key: str, channel_id_list: list) -> dict:
    channels_url = "https://www.googleapis.com/youtube/v3/channels"
    channels_params = {
        "part": "snippet,statistics,brandingSettings",
        "id": ",".join(channel_id_list),
        "key": api_key,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=channels_url, params=channels_params) as response:
            if response.status != 200:
                print(f"Ошибка при получении информации о каналах: {response.status}")
                return {}

            channels_data = await response.json()

            channel_info = {
                channel['id']: {
                    "subscriberCount": channel['statistics'].get('subscriberCount', 'N/A'),
                    "isMonetized": 'monetizationSettings' in channel.get('brandingSettings', {})
                }
                for channel in channels_data['items']
                }
            channel_info['type'] = 'channel_data'
            return channel_info



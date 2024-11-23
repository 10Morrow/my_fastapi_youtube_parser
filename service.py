import asyncio
import time
API_KEY = 'AIzaSyC1kjO6Zsh7OAqipegtvOIQA6S6gMORyh0'
"""
1) не больше 10 запросов в секунду.
2) Использовать 'объединение' запросов для экономии токенов.
"""
from youtube_api_module import search_video, video_analytics, channel_analytics


def chunk_list(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


async def combined_data(data_set: list) -> list:
    api_key = API_KEY
    analytic_tasks = []
    search_tasks = [search_video(api_key, word) for word in data_set]
    searched_data_list = await asyncio.gather(*search_tasks)

    video_ids = {video_id for search_set in searched_data_list for video_id in search_set['video_ids']}
    channel_ids = {channel_id for search_set in searched_data_list for channel_id in search_set['channel_ids']}

    chunked_video_ids = list(chunk_list(list(video_ids), 50))
    chunked_channel_ids = list(chunk_list(list(channel_ids), 50))

    for chunk in chunked_video_ids:
        analytic_tasks.append(video_analytics(api_key, chunk))

    for chunk in chunked_channel_ids:
        analytic_tasks.append(channel_analytics(api_key, chunk))

    combined_data_list = await asyncio.gather(*analytic_tasks)
    return combined_data_list


async def data_compaire(data_set: list):
    finally_combined_data = await combined_data(data_set)

    video_analytics_data = {}
    channel_analytics_data = {}
    for data_block in finally_combined_data:
        if data_block['type'] == 'video_data':
            video_analytics_data.update(data_block)
        else:
            channel_analytics_data.update(data_block)
    del video_analytics_data['type']
    del channel_analytics_data['type']
    for key, values in video_analytics_data.items():
        channel_info = channel_analytics_data[values['channel_id']]
        values.update(channel_info)
    return video_analytics_data


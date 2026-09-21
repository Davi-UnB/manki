import requests
from lxml import html
import urllib.parse

def get_stroke_images(word: str) -> str:
    result = ''
    seen = set()
    for char in word:
        if char not in seen and char.strip():
            seen.add(char)
            url = f'https://www.strokeorder.com/chinese/{char}'
            try:
                response = requests.get(url)
                response.raise_for_status()
                tree = html.fromstring(response.content)
                video_url = tree.xpath("//div[contains(@class, 'kanji-video-poster-wrap')]/@data-video-src")
                if video_url:
                    full_url = requests.compat.urljoin(url, video_url[0])
                    print("ACHOU VIDEO:", full_url)
            except Exception as e:
                print("ERRO:", e)

get_stroke_images("热心")

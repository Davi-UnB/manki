import requests
from lxml import html

class StrokeScraperService:
    """Responsável pela mineração de imagens de ordem dos traços."""
    @staticmethod
    def get_images_html(word: str) -> str:
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
                    gif_url = tree.xpath("//img[contains(@src, '/assets/bishun/animation/')]/@src")
                    
                    if gif_url:
                        full_url = requests.compat.urljoin(url, gif_url[0])
                        result += f'<img src="{full_url}"> '
                except Exception as e:
                    print(f"⚠️ Erro ao extrair stroke de '{char}': {e}")
        return result

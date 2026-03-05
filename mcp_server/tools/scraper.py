import httpx
from bs4 import BeautifulSoup

def scrape_page_text(url : str) -> str:
    """웹페이지의 텍스트 콘텐츠를 스크랩합니다."""
    resp = httpx.get(url)

    if resp.status_code != 200:
        return f"Failed to fetch {url}"
    
    soup = BeautifulSoup(resp.text, "html.parser")

    if soup.body:
        text = soup.body.get_text(separator=" ", strip=True)
        return " ".join(text.split())
    
    return ""

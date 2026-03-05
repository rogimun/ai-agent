import feedparser

def get_news_headlines() -> str:
    """구글 RSS 피드에서 최신 뉴스와 URL을 반환합니다."""
    rss_url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)

    if not feed.entries:
        return "뉴스를 가져올 수 없습니다."
    
    news_list = []

    for i, entry in enumerate(feed.entries, 1):
        title = getattr(entry, "title", "제목 없음")
        link = getattr(entry, "link", "#")

        print(f"뉴스 {i}: {title} - {link}")

        if not title or title == "None":
            title = "제목 없음"
        if not link or link == "None":
            link = "#"

        news_item = f"{i}. [{title}]({link})"
        news_list.append(news_item)

    return "\n".join(news_list)
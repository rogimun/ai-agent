from mcp.server.fastmcp import FastMCP
from mcp_server.tools import weather, news, sports, scraper, info, search

mcp = FastMCP("AI-Tools")

# 1. Scraper
@mcp.tool()
def scrape_page_text(url: str) -> str:
    """웹페이지의 텍스트 콘텐츠를 스크랩합니다."""
    return scraper.scrape_page_text(url)

# 2. Weather
@mcp.tool()
def get_weather(city_name: str) -> str:
    """도시 이름을 받아 해당 도시의 현재 날씨 정보를 제공합니다."""
    return weather.get_weather(city_name)

# 3. News
@mcp.tool()
def get_news_headlines() -> str:
    """구글 RSS 피드에서 최신 뉴스와 URL을 가져옵니다."""
    return news.get_news_headlines()

# 4. Sports
@mcp.tool()
def get_kbo_rank() -> str:
    """한국 프로야구 구단의 랭킹 정보를 제공합니다."""
    return sports.get_kbo_rank()

# 5. Info (Schedule & Quote)
@mcp.tool()
def today_schedule() -> str:
    """오늘의 주요 일정을 확인합니다."""
    return info.today_schedule()

@mcp.tool()
def daily_quote() -> str:
    """사용자에게 영감을 주는 명언을 제공합니다."""
    return info.daily_quote()

# 6. Briefing (복합 도구)
@mcp.tool()
def brief_today() -> str:
    """날씨, 뉴스, 일정 등을 종합하여 사용자에게 브리핑을 제공합니다."""
    return """
    다음을 순서대로 실행하고 결과를 종합하여 보고하세요:
    1. 사용자의 위치 파악 (필요 시 질문)
    2. 해당 지역 날씨(get_weather) 조회
    3. 최신 뉴스(get_news_headlines) 요약
    4. 야구 순위(get_kbo_rank) 및 일정(today_schedule) 확인
    5. 마지막으로 명언(daily_quote) 한마디.
    """

@mcp.tool()
def retrieve_knowledge(query: str) -> str:
    """
    회사의 취업 규칙, 복지, 개인정보보호 지침 등 내부 문서에서 답을 찾을 때 사용합니다.
    질문(query)을 넣으면 관련 문구들을 반환합니다.
    """
    return search.retrieve_knowledge(query)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0")
    
from tavily import TavilyClient
from shared.config import settings

client = TavilyClient(api_key=settings.TAVILY_API_KEY)

def get_web(query: str) -> str:

    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )

        results = []

        for i, r in enumerate(response.get("results", []), 1):
            results.append(
                f"""
                    [검색 결과 {i}]
                    제목: {r.get('title')}
                    내용: {r.get('content')}
                    URL: {r.get('url')}
                """
            )

        return "\n\n".join(results)
    except Exception as e:
        return f"웹 검색 중 오류 발생: {str(e)}"

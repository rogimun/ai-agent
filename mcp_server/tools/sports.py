import httpx

def get_kbo_rank() -> str:
    """한국 프로야구 구단의 랭킹을 가져옵니다"""

    result = httpx.get("https://sports.daum.net/prx/hermes/api/team/rank.json?leagueCode=kbo&seasonKey=2025")
    return result.text
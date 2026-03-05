from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from shared.config import settings

def today_schedule() -> str:
    """임의의 스케줄을 반환합니다."""
    events = ["10:00 팀 미팅", "13:00 점심 약속", "15:00 프로젝트 회의", "19:00 헬스장"]

    return " | ".join(events)

def daily_quote() -> str:
    """사용자에게 영감을 주는 명언을 출력합니다"""
    chat_model = ChatOpenAI(model=settings.MODEL_NAME)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "당신은 오늘 하루의 명언을 알려주는 도우미입니다. 사용자의 명언 요청이 있을시 명언만 출력합니다."
            ),
            ("human", "오늘의 명언을 출력해주세요."),
        ]
    )
    chain = prompt | chat_model
    response = chain.invoke({})
    return response.content

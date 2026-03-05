from pathlib import Path
from langchain_core.messages import SystemMessage
from .state import AgentState

def load_prompt(filename: str) -> str:
    """prompts 폴더에서 텍스트 파일을 읽어옵니다."""
    path = Path(__file__).parent / "prompts" / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def call_model(state: AgentState, llm):
    """LLM을 호출하여 다음 행동을 결정하는 노드"""
    messages = state["messages"]
    
    # 대화 시작 시 시스템 프롬프트가 없으면 주입
    if not any(isinstance(m, SystemMessage) for m in messages):
        system_content = load_prompt("system.txt")
        messages = [SystemMessage(content=system_content)] + messages
    
    # LLM 호출
    response = llm.invoke(messages)
    
    # 업데이트할 메시지만 반환 (StateGraph가 자동으로 합쳐줌)
    return {"messages": [response]}
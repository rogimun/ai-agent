from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver

from .state import AgentState
from .nodes import call_model

def create_agent_workflow(llm, tools):
    # 단기 메모리 설정
    memory = InMemorySaver()
    
    # 1. 그래프 초기화
    workflow = StateGraph(AgentState)

    # 2. 노드 등록
    # 람다를 사용하여 llm 객체를 노드 함수에 전달합니다.
    workflow.add_node("agent", lambda state: call_model(state, llm))
    workflow.add_node("tools", ToolNode(tools))

    # 3. 엣지(연결선) 설정
    workflow.add_edge(START, "agent")
    
    # 조건부 엣지: 도구 사용 여부에 따라 길을 나눔
    workflow.add_conditional_edges(
        "agent",
        lambda state: "tools" if state["messages"][-1].tool_calls else END
    )
    
    # 도구 사용 후 다시 에이전트에게 돌아와 답변 정리
    workflow.add_edge("tools", "agent")

    # 4. 컴파일
    return workflow.compile(checkpointer=memory)
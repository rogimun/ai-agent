from langchain_core.messages import HumanMessage

async def stream_agent_response(agent_executor, message: str, session_id: str):
    """에이전트의 응답을 스트리밍하는 비동기 제너레이터"""
    if agent_executor is None:
        yield "에이전트가 아직 준비되지 않았습니다. 잠시 후 다시 시도해주세요."
        return
    
    try:
        config = {"configurable" : {"thread_id": session_id}}
        input_message = HumanMessage(content=message)

        async for event in agent_executor.astream_events(
            {"messages": [input_message]},
            config = config,
            version = "v2",
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield content
            elif kind == "on_tool_start":
                print(f"Tool start: {event['name']}")
            elif kind == "on_tool_end":
                print(f"Tool end: {event['name']}")
    except Exception as e:
        print(f"스트리밍 중 오류 발생 : {e}")
        yield f"오류가 발생했습니다: {e}"

from fastapi import APIRouter, Request, Form
from fastapi.responses import StreamingResponse
from web.streaming import stream_agent_response

router = APIRouter()

@router.post("/chat")
async def chat(request: Request, message: str = Form(...), session_id: str = Form(...)):
    """사용자 메시지를 받아 에이전트의 응답을 스트리밍합니다."""
    agent_executor = request.app.state.agent_executor
    return StreamingResponse(
        stream_agent_response(agent_executor, message, session_id),
        media_type="text/event-stream",
    )

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI

from shared.config import settings
from agent.workflow import create_agent_workflow

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """MCP 서버 연결, 도구 로드 및 에이전트 워크플로우를 초기화합니다."""
    logger.info("🚀 애플리케이션 시작: MCP 서버 연결 및 에이전트 설정 중...")
    
    url = "http://mcp-server:8000/mcp"
    max_retries = 10  # 최대 10번 시도
    retry_delay = 3   # 3초 간격
    
    # 1. 연결 재시도 루프
    for i in range(max_retries):
        try:
            async with streamablehttp_client(url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    # MCP 세션 초기화
                    await session.initialize()
                    logger.info("✅ MCP 세션 초기화 성공")

                    # MCP 도구를 LangChain 도구로 변환
                    tools = await load_mcp_tools(session)
                    logger.info(f"🛠️ {len(tools)}개의 도구 로드 완료")

                    # LLM 및 에이전트 워크플로우 생성 (기존 로직)
                    llm = ChatOpenAI(
                        model=settings.MODEL_NAME,
                        api_key=settings.OPENAI_API_KEY,
                        temperature=0
                    ).bind_tools(tools)

                    app.state.agent_executor = create_agent_workflow(llm, tools)
                    logger.info("🤖 에이전트 워크플로우 생성 완료. 애플리케이션이 준비되었습니다.")
                    
                    yield
                    break

        except (ConnectionError, Exception) as e:
            logger.warning(f"연결 시도 실패 ({i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error("MCP 서버 연결 최종 실패. 에이전트 없이 시작하거나 종료됩니다.")
                app.state.agent_executor = None
                yield

    logger.info("애플리케이션 종료: 자원을 정리합니다.")
    app.state.agent_executor = None
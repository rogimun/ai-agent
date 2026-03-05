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
    """MCP 연결 및 에이전트 워크플로우를 안전하게 초기화합니다."""
    logger.info("애플리케이션 초기화 시작...")
    
    url = "http://mcp-server:8000/mcp"
    max_retries = 15  # 최대 15번 시도 (약 45~60초)
    retry_delay = 4   # 시도 간격 (초)

    app.state.agent_executor = None

    for i in range(max_retries):
        try:
            logger.info(f"MCP 서버 연결 시도 중... ({i+1}/{max_retries})")
            
            # streamablehttp_client를 컨텍스트 매니저로 연결
            async with streamablehttp_client(url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    # 1. MCP 세션 초기화
                    await session.initialize()
                    logger.info("✅ MCP 세션 연결 성공!")

                    # 2. MCP 도구를 LangChain 형식으로 로드
                    tools = await load_mcp_tools(session)
                    logger.info(f"{len(tools)}개의 도구 로드 완료")

                    # 3. 에이전트 워크플로우 설정
                    llm = ChatOpenAI(
                        model=settings.MODEL_NAME,
                        api_key=settings.OPENAI_API_KEY,
                        temperature=0
                    ).bind_tools(tools)

                    app.state.agent_executor = create_agent_workflow(llm, tools)
                    logger.info("에이전트 워크플로우 설정이 완료되었습니다.")
                    
                    yield 
                    break # 앱 종료 시 루프 탈출

        except Exception as e:
            logger.warning(f"연결 실패: {type(e).__name__}")
            
            if i < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error("MCP 서버 연결 최종 실패. 에이전트 없이 서버를 시작합니다.")
                yield

    logger.info("애플리케이션이 종료됩니다. 자원을 정리합니다.")
    app.state.agent_executor = None
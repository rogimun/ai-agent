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

# 로그 출력 설정
logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 애플리케이션의 생명주기 동안 MCP 연결 및 에이전트 설정을 관리합니다."""
    logger.info("애플리케이션 시작 프로세스 가동...")
    
    url = "http://mcp-server:8000/mcp"
    max_retries = 20  # 최대 20번 시도 (약 1분)
    retry_delay = 3   # 3초 간격 시도

    # 연결 성공 여부를 추적
    connected = False

    for i in range(max_retries):
        try:
            logger.info(f"MCP 서버 연결 시도 중... ({i+1}/{max_retries})")
            
            # streamablehttp_client 연결 시도
            async with streamablehttp_client(url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    # 1. MCP 세션 초기화
                    await session.initialize()
                    logger.info("MCP 세션 초기화 성공!")

                    # 2. MCP 도구 로드 (기존 로직)
                    tools = await load_mcp_tools(session)
                    logger.info(f"{len(tools)}개의 도구 로드 완료")

                    # 3. LLM 및 에이전트 설정 (기존 로직)
                    llm = ChatOpenAI(
                        model=settings.MODEL_NAME,
                        api_key=settings.OPENAI_API_KEY,
                        temperature=0
                    ).bind_tools(tools)

                    app.state.agent_executor = create_agent_workflow(llm, tools)
                    logger.info("에이전트 워크플로우 생성 완료. 애플리케이션이 준비되었습니다.")
                    
                    connected = True
                    yield  
                    break # 종료 시 루프 탈출

        except Exception as e:
            logger.warning(f"연결 실패: {e}")
            if i < max_retries - 1:
                logger.info(f"{retry_delay}초 후 다시 시도합니다...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("모든 연결 시도 실패. MCP 서버 상태를 확인하세요.")
                app.state.agent_executor = None
                yield

    logger.info("애플리케이션 종료.")
    app.state.agent_executor = None
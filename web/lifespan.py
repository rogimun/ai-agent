import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI

from shared.config import settings
from agent.workflow import create_agent_workflow

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 애플리케이션의 생명주기 동안 MCP 연결 및 에이전트 설정을 관리합니다."""
    print("애플리케이션 시작: MCP 서버에 연결하고 에이전트를 설정합니다...")

    max_retries = 5
    retry_delay = 3    
    connected = False

    for i in range(max_retries):
        try:
            async with streamablehttp_client(settings.MCP_SERVER_URL) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await load_mcp_tools(session)

                    llm = ChatOpenAI(
                        model=settings.MODEL_NAME,
                        api_key=settings.OPENAI_API_KEY,
                        temperature=0
                    ).bind_tools(tools)

                    app.state.agent_executor = create_agent_workflow(llm, tools)
                    print("에이전트 설정 완료. 애플리케이션이 준비되었습니다.")
                    connected = True
                    yield
                    break
        except Exception as e:
            if i < max_retries - 1:
                print(f"{retry_delay}초 후 다시 시도합니다...")
                await asyncio.sleep(retry_delay)
            else:
                print("최대 재시도 횟수 초과. 서버를 시작할 수 없습니다.")
                raise e
            
    if connected:
        print("애플리케이션 종료.")
        app.state.agent_executor = None

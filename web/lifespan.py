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

    #async with streamablehttp_client("http://localhost:8000/mcp/") as (read, write, _):
    async with streamablehttp_client("http://mcp-server:8000/mcp") as (read, write, _):
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
            yield

    print("애플리케이션 종료.")
    app.state.agent_executor = None

import os, sys
import asyncio
import datetime, json 
from agent_framework import Agent, MCPStdioTool
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

from fastmcp import FastMCP

load_dotenv()


async def main():
  
    async with (
        MCPStdioTool(
            name="local-mcp",           # must match mcp server name
            command = sys.executable,   # will run python interpretor so that MCP server starts
            args=["05.mcp_server.py"]   # name of the file to be executed which has server
        ) as mcp_server,

        Agent(
                client = OpenAIChatClient(),
                instructions = "You are an assistant that works with tools. Always use available tools via MCP only if needed. " \
                    "Do not fabricate data. Do not use tools if user does not ask query which needs tool calling",
                name = "MCPAgent"
            ) as agent,
    ):
        session = agent.create_session()

        while True:
            query = input("\n Enter Text \n")

            if query in ('bye','exit','quit'):
                break

            async for chunk in agent.run(query, session = session, stream = True, tools=mcp_server):
                if chunk.text:
                   print(chunk.text, end = "", flush = True)
       
   

if __name__ == "__main__":
    asyncio.run(main())
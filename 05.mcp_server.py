import os, sys
import asyncio
import datetime, json 
from typing import Annotated
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(name = "local-mcp")


@mcp.tool
def get_current_datetime():
    ''' Returns current date, time and day'''
    current_date = datetime.datetime.now()
    return current_date.strftime("Date : %Y - %m - %d | Time : %H - %M - %S | Day : %A")


@mcp.tool
def get_weather(city):
    '''Returns weather of a city'''
    dummy_data = {
        "hyderabad" : {"condition" : "sunny", "temp" : "40 degree"},
        "mumbai"    : {"condition" : "windy", "temp" : "20 degree"},
                 }
    data = dummy_data.get(city.lower())
    return json.dumps(data)


    
if __name__ == "__main__":
    print("FastMCP server started", file = sys.stderr, flush = True)
    # For local use so stdio
    mcp.run(transport = "stdio")
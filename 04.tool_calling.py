import os
import asyncio
import datetime, json 
from typing import Annotated
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

load_dotenv()

def get_current_datetime():
    ''' Returns current date, time and day'''
    current_date = datetime.datetime.now()
    return current_date.strftime("Date : %Y - %m - %d | Time : %H - %M - %S | Day : %A")

def get_weather(city):
    '''Returns weather of a city'''
    dummy_data = {
        "hyderabad" : {"condition" : "sunny", "temp" : "40 degree"},
        "mumbai"    : {"condition" : "windy", "temp" : "20 degree"},
                 }
    data = dummy_data.get(city.lower())
    return json.dumps(data)

agent = Agent(
    client = OpenAIChatClient(),
    instructions = "You are an assistant that works with tools. Always use available tools only if needed. " \
                    "Do not fabricate data. Do not use tools if user does not ask query which needs tool calling",
    name = "ToolAgent",
    tools = [get_weather,
             get_current_datetime]
            )

# Create session to store short term memory
session = agent.create_session()

async def main():

    while True:
        query = input("\n Enter Text : ")
        print("\n")

        if query in ('bye','exit','quit'):
            break

        async for chunk in agent.run(query, session = session, stream = True):
            if chunk.text:
                print(chunk.text, end = "", flush = True)

    
if __name__ == "__main__":
    asyncio.run(main())
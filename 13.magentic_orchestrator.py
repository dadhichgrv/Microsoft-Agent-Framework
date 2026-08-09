import os, sys
import asyncio, time
from typing import Any, cast
from pydantic import BaseModel
from agent_framework import Agent, ContextProvider, AgentSession,  SessionContext, AgentResponse
from agent_framework.orchestrations import MagenticBuilder
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

load_dotenv()
    
# Create class to add some context that you want to pass to system instructions for agent
class UserPreference(ContextProvider):
    """ Inject context that you want to inject into agent"""

    def __init__(self, context_text : str):
        super().__init__("context-provider")
        self._text = context_text

    async def before_run(
            self,
            *,
            agent : Any,
            session : AgentSession,
            context : SessionContext,
            state   : dict[str, Any]
                        ) :
        context.extend_instructions(self.source_id, self._text)

# this can be done through file read also by adding context to a file and reading that file
business_context_provider = UserPreference(
                                            """
                                            Customer 1 :
                                            TPID : 12345
                                            Account Name : Contoso
                                            Estimated Revenue : $1,000
                                            Recommended Product : ME3 to ME5 Upsell
                                            Existing Product : ME3


                                            Customer 2 :
                                            TPID : 54321
                                            Account Name : FOURTH COFFEE
                                            Estimated Revenue : $500
                                            Recommended Product : OE3 to ME3 Upsell
                                            Existing Product : ME3


                                            """
                                            )


# Class for Structured Output
class FeedBack_Output(BaseModel):
    score : int 
    feedback : str

# Recommendation Agent to create reason to believe text based on customer data
recommendation_agent = Agent(
                        client = OpenAIChatClient(),
                        name   = "recommendation_agent",
                        instructions = """ You are recommendation assistant who create reason for given recommendation.
                                            Look at given data and recommend reason for this recommendation.
                                            Output shud not be more than 50 words
                                       """,
                        context_providers = [business_context_provider]
                      
                        )

# Critic Agent that will evaluate the reason text and give score & feedback 
critic_agent = Agent(
                client = OpenAIChatClient(),
                name = "criticagent",
                instructions = """ You are harsh but constructive critic assistant. Review the recommnedation generated 
                                    and give a score and feedback if any in below format :
                                    Score    : int
                                    Feedback : Suggestions if any
                                    If score is more than 8, your feedback is to approve it else reject it
                                      """ 
            
                                  
                # default_options = {
                #                     "response_format" : FeedBack_Output
                #                   },
                      ) 



opportunity_agent = Agent(
                        client = OpenAIChatClient(),
                        name   = "oppty_agent",
                        instructions = """ You are opportunity creation assistant who helps user create opportunity from a lead.
                                            Return "Opportunity Created Successfully".
                                       """,
                        context_providers = [business_context_provider]
                        )


decline_agent = Agent(
                client = OpenAIChatClient(),
                name = "decline_agent",
                instructions = """ You are lead decline assistant who helps user decline a lead.
                                    Return "Lead Declined Successfully".
                                      """  ,
                context_providers = [business_context_provider]
                      ) 

share_partner_agent = Agent(
                client = OpenAIChatClient(),
                name = "share_partner_agent",
                instructions = """ You are partner sharing assistant who shares the lead with partner.
                                   Return "Lead Shared with partner successfuly". 
                                """,
                context_providers = [business_context_provider]
                      ) 

general_agent = Agent(
                client = OpenAIChatClient(),
                name = "general_agent",
                instructions = " You are general assistant who helps users with account information. Provide account details if asked",
                context_providers = [business_context_provider]
                      ) 


orchestration_agent = Agent(
                            client       = OpenAIChatClient(),
                            name         = "Orchestrator",
                            instructions = """ You are magentic orchestrator. Plan which agent to invoke and in what order in 
                                                order to complete the task. Re-plan dynamically depending on result.
                                                Respond this in 60 seconds.
                                            """ 
                            )

workflow = MagenticBuilder(
            participants = [opportunity_agent, decline_agent],
            manager_agent = orchestration_agent,
            max_round_count = 10,
            max_stall_count = 3,
            max_reset_count = 2
                            ).build()


async def main():
     
     query = " Provide reason to recommend for Fourth Coffee Account"
     query2 = "Take this Contose and decline it "
               
     events = await workflow.run(query2)
     outputs = events.get_outputs()

     if outputs:
         final : AgentResponse = outputs[0]

         for msg in final.messages:
             print(msg.text)


if __name__ == "__main__":
    asyncio.run(main())

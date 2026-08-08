import os, sys
import asyncio, time
from typing import Any, cast
from pydantic import BaseModel
from agent_framework import Agent, ContextProvider, AgentSession,  SessionContext
from agent_framework.orchestrations import SequentialBuilder, ConcurrentBuilder
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
                                    If score is more than 8, your response is to approve it else reject it
                                      """ 
            
                                  
                # default_options = {
                #                     "response_format" : FeedBack_Output
                #                   },
                      ) 



# Run this for 3 iterations to generate draft reason to believe and revise it 
async def critic_loop(query : str, max_iterations : int = 3):
    # Create session to remember loop data in that session
    session = recommendation_agent.create_session()

    draft = (
        await recommendation_agent.run(query, session = session)
            ).text
    
    for i in range(max_iterations):
        print(f"Iteration {i+1}")

        # Adding Structured Output constrain here
        result = (await critic_agent.run(draft,  options = {
                                                             "response_format" : FeedBack_Output
                                                           },
                                     )).text

        score = FeedBack_Output.model_validate_json(result).score
        feedback = FeedBack_Output.model_validate_json(result).feedback

        print(f"Draft : {draft}")
        print(f"Score : {score}")
        print(f"Feedback : {feedback}")

        if int(score) >= 8:
            print(f"Approved on iteration : {i+1}")
            return draft
        
        draft = (await recommendation_agent.run(f"Revise your previous draft based on this feedback : {feedback}",
                                               session = session 
                                               )
                ).text
        
    print("Max iteration reached. Returning last version")
    return draft    


async def main():
     
     query = " Provide reason to recommend for Fourth Coffee Account"
               
     final_response = await critic_loop(query)
     print(f"Response : {final_response}")
     print("-"*30)


  

if __name__ == "__main__":
    asyncio.run(main())

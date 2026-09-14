from agents import build_search_agent, build_reader_agent, writer_chain , critic_chain

def run_research_pipeline(topic : str) -> dict:

     state = {}

     #search agent working 
     search_agent = build_search_agent()
     search_result= search_agent.invoke({ 
          "messages" : [("user", f"Find recent relaible and detailed information about {topic} ")]
          })

     state["search_results"] = search_result['messages'][-1].content

     print("\n search_results" , state['search_results'])



     #step 2 reader agent
     reader_agent = build_reader_agent()
     reader_result= reader_agent.invoke({ 
          "messages" : [( "user" ,  
                        f"Based on the following search result about '{topic}'"
                        f"Pick the most relevant URL and scrape it deeper for content.\n\n "
                        f"Search Result:\n{state['search_results'] [:200]}"
                        )]

     })


     state["scraped_content"] = reader_result["messages"][-1].content
     print("\n reader_result" , state['scraped_content'])

     #step 3 writer chain

     research_combined= (
     f"SEARCH_RESULT: \n {state ['search_results']} \n\n "
     f"DETAILED SCRAPED CONTENT:  \n {state ['scraped_content']}" )

     state["report"] = writer_chain.invoke({
          "topic": topic ,
          "research" : research_combined })

     print("\n Final Report\n" , state['report'])

     #critic report 

     state['feedback']=critic_chain.invoke({
          "report" : state['report']
     })

     print("\n critic Report\n" , state['feedback'])

     return state 


if __name__ == "__main__" :
     topic = input("\n Enter a research topic:")
     run_research_pipeline(topic)






          
     
          
   



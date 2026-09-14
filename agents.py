from langchain.agents import create_agent

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , web_scraper
from dotenv import load_dotenv
import os 
from langchain_groq import ChatGroq

load_dotenv() 

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0,)

# 1 agent 
def build_search_agent():
    return create_agent(
        model =llm,
        tools=[web_search],
    )

#2 agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[web_scraper],
    )  

#writer chain LCEL PIPELINE

writer_prompt = ChatPromptTemplate.from_messages(
    [("system", "You are a an expert reader and writer. write clear , structured and insightful reports."),
     ("human", """Write a detailed research report on the topic below.

     topic: {topic}
     Research Gathered:
     {research}

     Structured the report as:
     -Introduction
     -Key Findings (minimum 3 well-explained points)
     -Conclusion
     -Sources (list all URLs found in the reasearch)
     -Be datialed , factual and professional
        """)])
#llm will give this kind of answer using it's brain

writer_chain = writer_prompt | llm | StrOutputParser()

#critic chain
critic_prompt = ChatPromptTemplate.from_messages(
    [("system", "You are a sharp and constructive research critic. Be honest and specific ."),
     ("human", """Review the research report below and evaluate it strictly.
     Report:
     {report}

     Respond in this exact format:
     -score : X/10
     strengths:
     - ...
     - ...

     Areas to Improve:
     - ...
     - ...
     - ...

     One line verdict:
     ...""")])

critic_chain = critic_prompt | llm | StrOutputParser()


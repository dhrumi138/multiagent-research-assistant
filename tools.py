from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from rich import print

#first tool
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str: 
    """
    Perform a web search using Tavily API and return the reliable information on the topic . returns Titles , URLs and snippets of the top search results.
    """
    
    results= tavily_client.search(query=query,max_results = 2)

    out = []

    for r in results['results']:
        out.append(f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}\n")

    return "\n ------ \n".join(out)

@tool
def web_scraper(url:str) -> str:
    """
    Scrape and return the text content from given URL for deeper reading . """
    try:
        response = requests.get(url, timeout=10 , headers={"User-Agent": "Mozilla/5.0"})  # Set a timeout for the request
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script','style','nav','footer']):
            tag.decompose()  # Remove script and style elements
        return  soup.get_text(separator=' ', strip=True) [:1500]
    except requests.exceptions.RequestException as e:
        return f"An error occurred while trying to scrape the webpage: {str(e)}"
    


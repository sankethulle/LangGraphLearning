from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage,HumanMessage
from langchain_openai import ChatOpenAI
from typing import TypedDict,Annotated
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import sqlite3
from langsmith import traceable
import os
import requests

load_dotenv()
llm_model = ChatOpenAI(
    model = "gpt-4o-mini"
)
os.environ['LANGCHAIN_PROJECT'] = 'LangGraph_persistant_storage'
stock_api_key = os.environ['VANTAGE_API_KEY']
config = {'configurable':{'thread_id':'thread_id'}}

# tools

search_tool = DuckDuckGoSearchRun()

@tool
def calculator(first:float,second:float,operation:str)->dict:
    """
    This is arithmatic tool which takes three inuts and perform arithmatic calculations
    first two paramters are type of float on which need to perform
    addition/substraction/multiplication/division operations based on the third input
    and return result
    """
    try:
        result:float=0
        if operation=='add':
         result = first+second
        elif operation=='sub':
         result = first-second
        elif operation=='mul':
            result = first*second
        elif operation=='div':
            result = first/second
        else:
           return {'error':f'invalid operation {operation}'}
        
        return {'first':first,'second':second,'operation':operation,'result':result}      

    except Exception as e:
        return {'error':str(e)}

@tool
def get_stock_price(symbol:str)->dict:
   """
   Fetch current stock price for given stock symbol ex.- AAPL,TSLA
   apikey is defined in the url onlyh
   """ 
   api_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={stock_api_key}'
   response = requests.get(api_url)
   return response.json()

tools = [search_tool,calculator,get_stock_price]
llm_with_tools = llm_model.bind_tools(tools)

class ChatBotState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

def chat_node(state:ChatBotState)->dict:
   """
   LLM node which may answer or request tool call   
   """
   messages = state['messages']
   llm_response = llm_with_tools.invoke(messages)
   return {'messages':[llm_response]}

connection = sqlite3.connect(database="Chatbot.db",check_same_thread=False)
checkpointer = SqliteSaver(conn=connection)
graph = StateGraph(ChatBotState)
graph.add_node("chat_node",chat_node)
graph.add_node("tool_node",ToolNode(tools))

graph.add_edge(START,"chat_node")
graph.add_conditional_edges(
    "chat_node",
    tools_condition,
    {"tools": "tool_node", "__end__": END},
)
graph.add_edge("tool_node", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)
@traceable(name='f_get_all_threads')
def get_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)    



from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage,HumanMessage
from langchain_openai import ChatOpenAI
from typing import TypedDict,Annotated
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langsmith import traceable
import os

load_dotenv()
llm_model = ChatOpenAI(
    model = "gpt-4o-mini"
)
os.environ['LANGCHAIN_PROJECT'] = 'LangGraph_persistant_storage'
config = {'configurable':{'thread_id':'thread_id'}}

class ChatBotState(TypedDict):
    message:Annotated[list[BaseMessage],add_messages]
@traceable(name='f_process_user_message')
def process_user_message(state:ChatBotState)->dict:
    print(f'[process_user_message"]')
    userQuery = state['message']        
    llm_response=llm_model.invoke(userQuery)    
    return {'message':[llm_response]}

connection = sqlite3.connect(database="Chatbot.db",check_same_thread=False)
checkpointer = SqliteSaver(conn=connection)
graph = StateGraph(ChatBotState)
graph.add_node("process_user_message",process_user_message)
graph.add_edge(START,"process_user_message")
graph.add_edge("process_user_message",END)
chatbot = graph.compile(checkpointer=checkpointer)
@traceable(name='f_get_all_threads')
def get_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)    



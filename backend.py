from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage,HumanMessage
from langchain_openai import ChatOpenAI
from typing import TypedDict,Annotated
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()
llm_model = ChatOpenAI(
    model = "gpt-4o-mini"
)

config = {'configurable':{'thread_id':'thread_id'}}

class ChatBotState(TypedDict):
    message:Annotated[list[BaseMessage],add_messages]

def process_user_message(state:ChatBotState)->dict:
    print(f'[process_user_message"]')
    userQuery = state['message']        
    llm_response=llm_model.invoke(userQuery)    
    return {'message':[llm_response]}

checkpointer = MemorySaver()
graph = StateGraph(ChatBotState)
graph.add_node("process_user_message",process_user_message)
graph.add_edge(START,"process_user_message")
graph.add_edge("process_user_message",END)
chatbot = graph.compile(checkpointer=checkpointer)

# while True:
#     user_message = input('Type your message')
#     print('user: ',user_message)
#     if user_message.strip().lower() in ['exit','bye','quit']:
#         break
    
#     response = chatbot.invoke({'message':[HumanMessage(content=user_message)]},config=config)
#     print('AI: ',response['message'][-1].content)

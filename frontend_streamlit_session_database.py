import streamlit as st
from langchain_core.messages import HumanMessage
from backend_database import chatbot,get_all_threads
import uuid
from datetime import datetime
from langsmith import traceable
import os

os.environ['LANGCHAIN_PROJECT'] = 'LangGraph_persistant_storage'

@traceable(name='f_generate_threadId')
def generate_threadId():
    readable_id = datetime.now().strftime("%d %B %Y, %I:%M:%S %p")
    return readable_id

@traceable(name='f_save_thread_to_session')
def save_thread_to_session(thread_id):
    print(f"[In save_thread_to_session]") 
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)    

@traceable(name='f_reset_session')
def reset_session():
    print(f'[In reset_session]')     
    st.session_state['thread_id'] = generate_threadId()
    st.session_state['message_history'] = []
    save_thread_to_session(st.session_state['thread_id'])  

@traceable(name='f_load_session_chat')
def load_session_chat(thread_id):
    print(f'[In load_session_chat]')
    values = chatbot.get_state(config={'configurable':{'thread_id':st.session_state['thread_id']}}).values
    if "message" in values:
        return values['message']
    else:
        return []
        

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_threadId()
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = get_all_threads()

save_thread_to_session(st.session_state['thread_id'])
# CONFIG = {'configurable':{'thread_id':st.session_state['thread_id']}}
CONFIG = {'configurable':{
               'thread_id':st.session_state['thread_id']
            },
          'metadata':{
              'thread_id':st.session_state['thread_id']
            },
            'run_name':'LLM_CALL'

          }


st.sidebar.title('Lang-Graph Application')
if st.sidebar.button("New Chat"):
    reset_session()

st.sidebar.header("My Sessions")
for id in st.session_state['chat_thread'][::-1]:
    if st.sidebar.button(str(id)):
        st.session_state['thread_id'] = id
        session_chat = load_session_chat(id)        
        session_data = []
        for chat in session_chat:
            if isinstance(chat ,HumanMessage):
                role='user'
            else: 
                role='assistant'
            dict={
                'role':role,
                'content':chat.content
            }
            session_data.append(dict)    
        st.session_state['message_history'] = session_data


for messages in st.session_state['message_history']:
    with st.chat_message(messages['role']):
         st.text(messages['content'])

input_message = st.chat_input("Enter message")
if input_message:
    with st.chat_message('user'):
            st.text(input_message)

    st.session_state['message_history'].append({
     'role':'user',
     'content':input_message
})
    with st.chat_message('assistant'):
       ai_response = st.write_stream(
       message_chunk.content for message_chunk ,metadata  in chatbot.stream(
                 {'message':[HumanMessage(content=input_message)]},
                 config=CONFIG,
                 stream_mode='messages'
            )
       )  

    st.session_state['message_history'].append({
     'role':'assistant',
     'content':ai_response
}
)
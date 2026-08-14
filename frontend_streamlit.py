import streamlit as st
from langchain_core.messages import HumanMessage
from backend import chatbot

CONFIG = {'configurable':{'thread_id':'thread-1'}}

if 'message_history' not in st.session_state: \
    st.session_state['message_history'] = []
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
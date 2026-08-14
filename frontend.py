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
    ai_response = chatbot.invoke({'message':[HumanMessage(content=input_message)]},config=CONFIG)
    response_content = ai_response['message'][-1].content
    with st.chat_message('assistant'):
        st.text(response_content)

    st.session_state['message_history'].append({
     'role':'assistant',
     'content':response_content
}
)
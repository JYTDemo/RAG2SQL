import streamlit as st
from main import datachat as dc

#chat_object= dc(file_path='./data/employees.csv')
chat_object= dc()

conn=st.button('connect')
if conn:
    chat_object.vectorize()

st.title(":blue[Talk to Database]")
col1, col2, col3 = st.columns(3)
with col3:
    st.subheader("powered by GenAI")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] == 'user':
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if message["role"] == 'assistant':
        with st.chat_message(message["role"]):
            st.dataframe(message["content"],hide_index=True)


# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = chat_object.data_ops(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        #st.markdown(response)
        st.dataframe(response,hide_index=True)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})


# what is the location of the employee Steven ?
# How many employees are there from each of the cities ?
# what is the count of employees by each job title
# How many employees have no phone number
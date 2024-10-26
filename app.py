import streamlit as st

from Chatbot_manager import *
from Agent_manager import *

# 近代オリンピックが始まった当初水泳競技は自由形しかなく皆んな平泳ぎでした。背泳ぎの方が早いとなり皆んな背泳ぎを始めたのでオリンピックで自由形とは別に背泳ぎという競技が始まりました。今度はクロールの方が早い！と皆んな気づき自由形でクロールが席巻しました。しょうがないので伝統的な平泳ぎという別の種目を作りました。 平泳ぎの定義は当初うつ伏せで手足の動きが左右対称である事、とされました。バタフライの方が早くね？とみんなバタフライを始めたのでこらこらちゃんと平泳ぎをしなさいとバタフライという別の種目が作られました。

# 上の文章のファクトチェックをしてください


ai = Chatbot_manager(system_prompt="You are great asistant.")

if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "processes" not in st.session_state:
    st.session_state.processes = []

st.title("Chatbot without 🦜langchain")

for index, message in enumerate(st.session_state.messages):
    if message.role.value == "user":
        with st.chat_message("user"): 
            st.markdown(message.prompt)
    elif message.role.value == "assistant":
        with st.chat_message("assistant"): 
            for i, process in enumerate(st.session_state.processes[int(index/2)]):
                if i != len(st.session_state.processes[int(index/2)])-1:
                    with st.expander(f"{process.task.agent_role}: {process.task.query}"):
                        st.markdown(process.text)
                else:
                    st.markdown(process.text)

message_placeholder = st.empty()
full_text = ""
process = []

if prompt := st.chat_input("メッセージを入力してください"):
    st.session_state.messages.append(Chat_request(prompt=prompt))
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        ai = Agent_manager()
        # print(st.session_state.messages[:-1])
        ai.planner_memory_update(memory=st.session_state.messages[:-1])
        ai.langmodel_memory_update(memory=st.session_state.messages[:-1])
        response = ai.invoke_stream(query=Chat_request(prompt=prompt))
        
        with st.spinner("Thinking..."):
            for token in response:
                if token.role == "Answerer":
                    if token.task.number == len(process):
                        process.append(token)
                        message_placeholder = st.empty()
                    else:
                        process[token.task.number].text += token.text
                        message_placeholder.markdown(process[token.task.number].text)
                    
                elif token.task.number == len(process):
                    process.append(token)
                    expander = st.expander(f"{process[token.task.number].task.agent_role}: {process[token.task.number].task.query}")
                    message_placeholder = expander.empty()
                else:
                    process[token.task.number].text += token.text
                    message_placeholder.markdown(process[token.task.number].text)
    
    st.session_state.messages.append(ai.response)
    st.session_state.processes.append(process)
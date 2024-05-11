__import__('pysqlite3')
import sys

sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from work import work
import os

st.title(":gray[AI-律小法]     :cn:")
st.header('专业法律AI助手-由文心一言提供模型能力', divider='rainbow')
st.markdown('结合:blue[百万有效法律法规数据]以及:blue[实时数据检索]从法律层面更精准的解决您的法律问题')

if "token" not in st.session_state:
    st.session_state["token"] = ""
sidebar = st.sidebar
with sidebar:
    st.title(":gray[AI-律小法]     :cn:")
    st.header('专业法律AI助手-由文心一言提供模型能力', divider='rainbow')
    baidu_api_key = st.text_input("请输入您的Access Token", type="password")
    if baidu_api_key:
        st.session_state["token"] = baidu_api_key
        # work.ACCESS_TOKEN = baidu_api_key
        # os.environ['BAIDU_API_KEY'] = baidu_api_key
        st.success("Access Token已保存")    
# print(st.session_state["token"])
law_chatbot = work.Law_Work(access_token=st.session_state["token"])
question = st.text_input("请输入咨询的法律问题：", "如何支付加班费？")
button = st.button("提交", type="primary")

placeholder = st.empty()
# col1, col2, col3 = st.columns(5)
with placeholder.container():
    if button:
        if st.session_state["token"] != None:
            placeholder.empty()        
            with placeholder.container():
                st.markdown("## 用户问题：")
                st.markdown(f":blue[{question}]")
                try:
                    with st.spinner("AI-律小法正在生成专业答案..."):
                        answer_content = ""
                        placeholder = st.empty()
                        result = law_chatbot.run(question)
                        for mes in result[0]:
                            answer_content += mes.get_result()
                            placeholder.write(answer_content) 
                        placeholder.write(answer_content)
                        if len(result[1])>=1:
                            with st.popover(f"{question}:blue[更多解答]"):
                                st.markdown("### 类似相关问题")
                                for i in result[1][2]:
                                    st.markdown(f":blue[{i}]")
                                    st.divider()
                        st.divider()
                        st.markdown("* 法律答案由:gray[AI-律小法]生成")
                        st.markdown("* 答案有ai生成仅供参考，不承担任何法律责任")
                except Exception as e:
                    st.error(e, icon="🚨")
        else:
            st.error("请输入Access Token后使用", icon="🚨")

 

            
            

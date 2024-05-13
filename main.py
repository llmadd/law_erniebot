__import__('pysqlite3')
import sys

sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from work import work, mysql_db, xf_audio
import os
from streamlit_mic_recorder import mic_recorder
import pymysql
db_connection = pymysql.connect(**work.config)

st.title(":gray[AI-律小法]     :cn:")
st.header('专业法律AI助手-由文心一言提供模型能力', divider='rainbow')
st.markdown('结合:blue[百万有效法律法规数据]以及:blue[实时数据检索]从法律层面更精准的解决您的法律问题')

if "token" not in st.session_state:
    st.session_state["token"] = ""
if "question" not in st.session_state:
    st.session_state["question"] = "如何支付加班费？"
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = ""
sidebar = st.sidebar
with sidebar:
    st.title(":gray[AI-律小法]     :cn:")
    st.header('专业法律AI助手-由文心一言提供模型能力', divider='rainbow')
    baidu_api_key = st.text_input("请输入您的[Access Token](https://aistudio.baidu.com/index/accessToken)（点击获取Access Token）", type="password")
    st.markdown("* 如有意见反馈，欢迎评论区交流")
    st.markdown("* 更多功能需求，[联系我](mailto:xunqichen@126.com)")
    if baidu_api_key:
        st.session_state["token"] = baidu_api_key
        # work.ACCESS_TOKEN = baidu_api_key
        # os.environ['BAIDU_API_KEY'] = baidu_api_key
        st.success("Access Token已保存")    
# print(st.session_state["token"])

law_chatbot = work.Law_Work(access_token=st.session_state["token"])

question_placeholder = st.empty()
with question_placeholder:
    question = st.text_input("请输入咨询的法律问题：", st.session_state["question"],key = "text")
# st.divider()
col1, col2= st.columns([0.9, 0.1])
with col1:
    audio = mic_recorder(
    start_prompt="语音输入",
    stop_prompt="Stop recording",
    just_once=False,
    use_container_width=False,
    format="wav",
    callback=None,
    args=(),
    kwargs={},
    key=None)
with col2:
    button = st.button("提交", type="primary")

if audio:

    st.session_state.audio_bytes = audio["bytes"]

    st.audio(st.session_state.audio_bytes)

    # st.write(st.session_state.audio_bytes)
    recognizer = xf_audio.SpeechRecognizer(appid=os.getenv("XF_APPID"), api_secret=os.getenv("XF_APISecret"),
                                api_key=os.getenv("XF_APIKey"), audio_bytes = st.session_state.audio_bytes)
    recognizer.run()
    st.session_state["question"] = recognizer.get_result()
    with question_placeholder:
        question_placeholder.empty()
        question = st.text_input("请输入咨询的法律问题：", st.session_state["question"], key = ["audio"])


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
                        mysql_db.update_answer(db_connection=db_connection,question_id=result[2],answer=answer_content)
                        if len(result[1])>=1:
                            # print(result[1])
                            with st.popover(f"{question}:blue[更多解答]"):
                                st.markdown("### 类似相关问题")
                                for i in range(len(result[1][1])):
                                    st.markdown(f"* [{result[1][2][i]}]({result[1][1][i]})")
                                    st.divider()
                        
                        st.divider()
                        st.markdown("* 法律答案由:gray[AI-律小法]生成")
                        st.markdown("* 答案由ai生成仅供参考，不承担任何法律责任")
                except Exception as e:
                    st.error(e, icon="🚨")
        else:
            st.error("请输入Access Token后使用", icon="🚨")

 

            
            

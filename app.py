# st.title("标题")
# st.header("一级标题")
# st.subheader("二级标题")
# st.markdown("**Markdown 文本**")
# st.caption("小字说明")
# st.write("任意内容，万能输出")
# st.text("普通文本")
#
# st.button("按钮")
# st.slider("滑块", 0, 100)
# st.text_input("输入框")
# st.checkbox("复选框")
# st.radio("单选", ["选项A","选项B"])
# st.selectbox("下拉", ["选项1","选项2"])
#
# st.dataframe(df)        # 显示表格
# st.line_chart(df)       # 折线图
# st.image("图片路径")
#
# st.sidebar.button("侧边栏按钮")
# col1, col2 = st.columns(2)   # 分两栏
# with col1:
#     st.write("左边")

import streamlit as st
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com",
)

st.set_page_config(
    page_title="AI伴侣",
    page_icon="🎡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)
#大标题
st.title("AI智能伴侣")
import streamlit as st

system_prompt = """
你是一个温柔知心的AI助手，你的名字叫小怡，请用温柔的语气回答客户的问题
"""
prompt = st.chat_input("Say something")
if prompt:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        elif message["role"] == "assistant":
            st.chat_message("assistant").write(message["content"])

    st.chat_message("user").write(prompt)
    print("--------->调用AI大模型，提示词:", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.    create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            *st.session_state.messages,
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}},
    )

#     print("--------->AI大模型生成的回复:", response.choices[0].message.content)
    #非流式输出接包方式
    # st.chat_message("assistant").write(response.choices[0].message.content)
    # st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
    #流式输出接包方式

    response_messages=st.empty()
    full_content=""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content=chunk.choices[0].delta.content
            full_content+=content
            response_messages.chat_message("assistant").write(full_content)
    st.session_state.messages.append({"role": "assistant", "content": full_content})


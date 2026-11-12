from email.utils import collapse_rfc2231_value

import streamlit as st
import os
from openai import OpenAI
import datetime as dt
import json
def save_session():
    # 1.保存当前会话数据
    if st.session_state.session_id:
        # 构建新对话
        session_data = {"name": st.session_state.name,
                        "character": st.session_state.character,
                        "messages": st.session_state.messages,
                        "session_id": st.session_state.session_id}
        if not os.path.exists("sessions"):
            os.makedirs("sessions")
        with open(f"sessions/{st.session_state.session_id}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
def load_sessions():
    session_list = []
    if not os.path.exists("sessions"):
        return session_list
    for file in os.listdir("sessions"):
        if file.endswith(".json"):
              session_list.append(file[:-5])
    return session_list
def load_session(session_id):
    try:
        if not os.path.exists(f"sessions/{session_id}.json"):
            return None
        with open(f"sessions/{session_id}.json", "r", encoding="utf-8") as f:
            session_data = json.load(f)
            st.session_state.messages = session_data["messages"]
            st.session_state.name = session_data["name"]
            st.session_state.character = session_data["character"]
            st.session_state.session_id = session_id # Changed from st.session_state.session_id = {session_id} to st.session_state.session_id = session_id
    except Exception:
        st.error("加载会话失败")



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



system_prompt = """
                   你叫%s,现在是用户的真实伴侣,请完全代入伴侣角色。:
                   规则:
                        1.每次只回1条消息
                        2.禁止任何场景或状态描述性文字
                        3.匹配用户的语言
                        4.回复简短,像微信聊天一样
                        5.用符合伴侣性格的方式对话
                        6.回复的内容,要充分体现伴侣的性格特征
                        7.有需要的话可以发表情
                   伴侣性格:
                        -%s
                   你必须严格遵守上述规则来回复用户。
                 """
#聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []
#昵称
if "name" not in st.session_state:
    st.session_state.name = "小怡"

#性格
if "character" not in st.session_state:
    st.session_state.character = "活泼开朗的河南姑娘"
#会话标识
if "session_id" not in st.session_state:
    st.session_state.session_id = dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")#当前时间

# 侧边栏信息
with st.sidebar:

    st.subheader("AI控制面板")
    if st.button("新建会话", width="stretch", icon="🚀"):
        # 保存当前会话数据
        save_session()
        #创建新会话
        if st.session_state.messages:
           st.session_state.messages = []
           st.session_state.session_id = dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # 当前时间
           save_session()
           st.rerun()

    st.text("历史会话")

    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(session, width="stretch", icon="📄",key=f"load_{session}", type="primary" if session == st.session_state.session_id else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            if st.button("", width="stretch", icon="❌", key=f"delete_{session}"):
                pass
        # st.button(session, width="stretch", icon="📄")
        # st.button("", width="stretch", icon="❌")
    st.subheader("伴侣信息")
    name=st.text_input ("昵称",placeholder="请输入昵称",value= st.session_state.name)
    if name:
        st.session_state.name = name
    character=st.text_area ("性格",placeholder="请输入性格",value= st.session_state.character)
    if character:
        st.session_state.character = character

st.text(f"会话名称: {st.session_state.name}")

for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    elif message["role"] == "assistant":
        st.chat_message("assistant").write(message["content"])

prompt = st.chat_input("Say something")
if prompt:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    st.chat_message("user").write(prompt)
    print("--------->调用AI大模型，提示词:", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.    create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.name, st.session_state.character)},
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
    #大模型返回结果
    st.session_state.messages.append({"role": "assistant", "content": full_content})
    #保存会话数据
    save_session()


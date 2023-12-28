# coding=utf-8
# Copyright 2023 South China University of Technology and 
# Engineering Research Ceter of Ministry of Education on Human Body Perception.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Author: Chen Yirong <eeyirongchen@mail.scut.edu.cn>
# Date: 2023.03.14

''' 运行方式

安装依赖
```bash
pip install tiktoken
pip install streamlit==1.27.0
```
启动服务：
```bash
streamlit run use_chatgpt_app_v3.py --server.port 9026
```

## 测试访问

http://116.57.86.151:9026

'''

# st-chat uses https://www.dicebear.com/styles for the avatar

# https://emoji6.com/emojiall/

import os
import json
import time
import tiktoken
import requests
import streamlit as st

dialogue_history_dir = './chatgpt_history'

#model_name="gpt-3.5-turbo-16k-0613"

url = "https://openai.api2d.net/v1/chat/completions"

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer fkxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx' # <-- 把 fkxxxxx 替换成你自己的 Forward Key，注意前面的 Bearer 要保留，并且和 Key 中间有一个空格。
} # 1132461715@qq.com

st.set_page_config(
    page_title="ChatGPT(内网版)",
    page_icon="👩‍🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """     
-   版本：👩‍🔬ChatGPT(内网版)
-   机构：广东省数字孪生人重点实验室
-   作者：陈艺荣
	    """
    }
)

st.header("👩‍🔬ChatGPT(内网版)")

with st.expander("ℹ️ - 关于我们", expanded=False):
    st.write(
        """     
-   版本：👩‍🔬ChatGPT(内网版)
-   机构：广东省数字孪生人重点实验室
-   作者：陈艺荣
	    """
    )


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens




def clear_chat_history():
    del st.session_state.messages


def init_chat_history():
    with st.chat_message("assistant", avatar='👩‍🔬'):
        st.markdown("您好，我是ChatGPT(内网版),服务由广东省数字孪生人重点实验室提供，很高兴为您服务🥰")

    if "messages" in st.session_state:
        for message in st.session_state.messages:
            avatar = '🧑‍💻' if message["role"] == "user" else '👩‍🔬'
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
    else:
        st.session_state.messages = []

    return st.session_state.messages


def init_chat_id():
    if 'chatid' not in st.session_state:
        if not os.path.exists(dialogue_history_dir):
            # 创建保存用户聊天记录的目录
            os.makedirs(dialogue_history_dir)

        json_files = os.listdir(dialogue_history_dir)
        chat_id = len(json_files)
        st.session_state.chatid = chat_id
    
    return st.session_state.chatid
    



def get_history_chat_id():
    if not os.path.exists(dialogue_history_dir):
        # 创建保存用户聊天记录的目录
        os.makedirs(dialogue_history_dir)

    json_files = os.listdir(dialogue_history_dir)
    files = [int(os.path.splitext(file)[0]) for file in json_files]
    files = sorted(files, reverse=True)
    files = [str(file) for file in files]
    return files

    



def main():

    messages = init_chat_history()
    chat_id = init_chat_id()
    files = get_history_chat_id()
    files = [str(chat_id)] + files

    with st.sidebar:
        # AI助手的个性设置
        model_name = st.selectbox(
            '请选择模型的版本',
            ('gpt-3.5-turbo-16k-0613', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo-0613', 'gpt-3.5-turbo', 'gpt-3.5-turbo-0301', 'gpt-4-0613', 'gpt-4'))
        history_chat_id = st.selectbox('请选择查看的历史聊天记录', tuple(files))
        
    if history_chat_id != str(st.session_state.chatid):
        with open(os.path.join(dialogue_history_dir, str(history_chat_id)+'.json'), "r", encoding="utf-8") as f:
            messages = json.load(f)
        st.session_state.messages = messages
        for message in st.session_state.messages:
            avatar = '🧑‍💻' if message["role"] == "user" else '👩‍🔬'
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    if prompt := st.chat_input("Shift + Enter 换行, Enter 发送"):
        with st.chat_message("user", avatar='🧑‍💻'):
            st.markdown(prompt)
        messages.append({"role": "user", "content": prompt})
        print(f"[user] {prompt}", flush=True)
        with st.chat_message("assistant", avatar='👩‍🔬'):
            placeholder = st.empty()
            data = {"model": model_name, "messages": messages, "stream": False}
            start_time = time.time()
            requests_result = requests.post(url, headers=headers, json=data)
            if requests_result.status_code==200:
                response = requests_result.json()['choices'][0]['message']["content"]


                if 'gpt-3.5' in model_name:
                    num_tokens_input_chatgpt = num_tokens_from_messages(data["messages"], model="gpt-3.5-turbo")
                    num_tokens_output_chatgpt = num_tokens_from_messages([{"role": "assistant", "content": response}], model="gpt-3.5-turbo")
                    if '16k' in model_name:
                        total_p = 10*num_tokens_input_chatgpt/666 + 10*num_tokens_output_chatgpt/500
                    else:
                        total_p = 10*num_tokens_input_chatgpt/1333 + 10*num_tokens_output_chatgpt/1000

                else:
                    num_tokens_input_chatgpt = num_tokens_from_messages(data["messages"], model="gpt-4")
                    num_tokens_output_chatgpt = num_tokens_from_messages([{"role": "assistant", "content": response}], model="gpt-4")
                    total_p = 10*num_tokens_input_chatgpt/66.6 + 10*num_tokens_output_chatgpt/33.3
                
                total_cost = 0.0021*total_p # 1050元可以购买500,000 p

                

            else:
                response = '请求出现错误，可能没有点了，请充值后重试，或者网络请求存在问题！'

            end_time = time.time()
            total_time = start_time - end_time

            placeholder.markdown(response)

            with st.expander(label="*Related Information*"):
                st.write(
                    f"time=**{total_time:.2}s**, model_name=**{model_name}**, total_cost=**{total_cost:.2}元**, total_p=**{total_p} P**"
            )

        messages.append({"role": "assistant", "content": response})
        print(json.dumps(messages, ensure_ascii=False), flush=True)

        if messages is not None:
            with open(os.path.join(dialogue_history_dir, str(st.session_state.chatid)+'.json'), "w", encoding="utf-8") as f:
                json.dump(messages, f, indent=4, ensure_ascii=False)

        st.button("清空对话", on_click=clear_chat_history)


if __name__ == "__main__":
    main()

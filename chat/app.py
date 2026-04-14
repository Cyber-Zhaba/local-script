import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://app:8000/generate")

st.set_page_config(page_title="Local Script", page_icon="", layout="centered")
st.title("Local Script")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Опишите, какой Lua-скрипт нужно написать..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    history = ""
    for msg in st.session_state.messages[:-1]:
        role_label = "Пользователь" if msg["role"] == "user" else "Ассистент"
        history += f"{role_label}: {msg['content']}\n\n"

    full_prompt = f"История переписки:\n{history}\n\nТекущий запрос: {prompt}"

    with st.chat_message("assistant"):
        with st.spinner("Агенты работают..."):
            try:
                response = requests.post(
                    API_URL, json={"prompt": full_prompt}, timeout=300
                )
                response.raise_for_status()

                data = response.json()
                result = data.get("result", "Ошибка: Пустой ответ от сервера")
                print(result)

                st.markdown(f"```lua\n{result}\n```")
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"```lua\n{result}\n```"}
                )

            except requests.exceptions.RequestException as e:
                error_msg = f"Ошибка соединения с API: {e}"
                st.error(error_msg)

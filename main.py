import streamlit as st
import openai
import google.generativeai as genai

gemini_key = st.secrets["Gemini_API"]["api_key"]
azure_config = st.secrets["Azure_OpenAI"]

st.sidebar.title("Settings")
model_choice = st.sidebar.selectbox("Choose a Model", ["Gemini (gemini-2.0-flash)", "Azure OpenAI (gpt-35-turbo)"])

with st.sidebar.expander("Advanced Settings", expanded=False):
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    top_p = st.slider("Top-P", 0.0, 1.0, 0.95, 0.05)
    top_k = st.slider("Top-K", 1, 100, 40, 1)
    max_output_tokens = st.slider("Max Tokens", 50, 2048, 512, 50)

st.title("Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if "Gemini" in model_choice:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-2.0-flash")
                full_prompt = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])
                response = model.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": temperature,
                        "top_p": top_p,
                        "top_k": top_k,
                        "max_output_tokens": max_output_tokens
                    }
                )
                reply = response.text
            else:
                openai.api_type = "azure"
                openai.api_key = azure_config["api_key"]
                openai.api_base = azure_config["endpoint"]
                openai.api_version = azure_config["api_version"]

                response = openai.ChatCompletion.create(
                    engine=azure_config["deployment_name"],
                    messages=st.session_state.messages,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_output_tokens
                )
                reply = response["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"Error: {e}"

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

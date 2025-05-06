import streamlit as st, requests, base64
from config import API_URL
from pathlib import Path

st.set_page_config(page_title="BroBot", page_icon="🍻")
st.title("🍻 BroBot – Marketing Assistant")

# ----------------- persistent session -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []      # [(role, text)]
if "ip" not in st.session_state:
    st.session_state.ip = requests.get("https://api.ipify.org").text

AVATAR_PATH = Path(__file__).parent / "assets" / "BroBot.png"

@st.cache_resource
def _avatar_data_uri() -> str:
    data = AVATAR_PATH.read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode()

AVATAR = _avatar_data_uri()

# ------------- render history -------------------------
for role, text in st.session_state.messages:
    with st.chat_message(role, avatar=AVATAR if role == "BroBot" else None):
        st.write(text)

# ------------- new input ------------------------------
prompt = st.chat_input("Ask me anything about marketing…")
if prompt:

    # optimistic user echo
    st.session_state.messages.append(("User", prompt))
    with st.chat_message("User"):
        st.write(prompt)

    # backend call
    try:
        r = requests.post(API_URL, json={"prompt": prompt, "ip": st.session_state.ip}, timeout=30)
        r.raise_for_status()
        reply = r.json().get("reply", "(empty)")
    except Exception as e:
        reply = f"Sorry, backend error: {e}"

    # show BroBot answer
    st.session_state.messages.append(("BroBot", reply))
    with st.chat_message("BroBot", avatar=AVATAR):
        st.write(reply)

    st.rerun()   # refresh chat log

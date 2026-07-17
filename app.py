import streamlit as st
import time
from datetime import datetime

from airindia_assistant import answer_question, get_document_stats

st.set_page_config(
    page_title="Air India AI Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CSS ---------------- #

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"]{
    font-family:Poppins;
}

.stApp{
    background:#F6F7FB;
}

/* Header */

.title{
    font-size:45px;
    font-weight:700;
    color:#C8102E;
    text-align:center;
}

.subtitle{
    text-align:center;
    color:#666;
    margin-bottom:25px;
}

/* Sidebar */

section[data-testid="stSidebar"]{
    background:white;
}

/* Buttons */

.stButton>button{
    width:100%;
    border-radius:12px;
    border:none;
    background:#C8102E;
    color:white;
    font-weight:bold;
    padding:10px;
}

.stButton>button:hover{
    background:#96001F;
    color:white;
}

/* Metric Cards */

.metric-card{

    background:white;

    padding:18px;

    border-radius:15px;

    box-shadow:0px 5px 18px rgba(0,0,0,.08);

    text-align:center;
}

/* Footer */

.footer{

text-align:center;

color:gray;

padding:20px;

}

</style>
""",unsafe_allow_html=True)

# ---------------- Header ---------------- #

st.markdown("""
<div class='title'>
✈️ Air India AI Assistant
</div>

<div class='subtitle'>
Ask Questions From Air India Investigation Documents using Gemini AI
</div>
""",unsafe_allow_html=True)

# ---------------- Sidebar ---------------- #

with st.sidebar:

    st.image(
        "https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Air_India_Logo.svg/512px-Air_India_Logo.svg.png",
        width=180,
    )

    st.markdown("## 📄 Upload Document")

    uploaded_pdf = st.file_uploader(
        "",
        type=["pdf"]
    )

    st.divider()

    st.markdown("### 📊 Document Statistics")

    col1,col2=st.columns(2)

    with col1:
        try:
            stats = get_document_stats()
        except Exception:
            stats = {"pages": 0, "chunks": 0}
        st.metric("Pages", stats.get("pages", 0))

    with col2:
        st.metric("Chunks", stats.get("chunks", 0))

    st.metric("Status","✅ Ready")

    st.divider()

    st.markdown("### 📌 Suggested Questions")

    suggestions=[

        "What happened to Flight AI171?",

        "Timeline of the accident",

        "Safety recommendations",

        "Passengers onboard",

        "Cause of the crash"

    ]

    for q in suggestions:

        if st.button(q):
            st.session_state.user_input=q

    st.divider()

    if st.button("🗑 Clear Chat"):
        st.session_state.messages=[]

# ---------------- Chat History ---------------- #

if "messages" not in st.session_state:
    st.session_state.messages=[]

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ---------------- User Input ---------------- #

prompt=st.chat_input("Ask anything about Air India...")

if "user_input" in st.session_state:
    prompt=st.session_state.user_input
    del st.session_state.user_input

# ---------------- Response ---------------- #

if prompt:

    st.session_state.messages.append(
        {"role":"user","content":prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            time.sleep(1)

            try:
                response = answer_question(prompt, uploaded_file=uploaded_pdf)
            except Exception as exc:
                response = f"Unable to generate a response right now. Error: {exc}"

            st.markdown(response)

    st.session_state.messages.append(

        {

            "role":"assistant",

            "content":response

        }

    )

# ---------------- Footer ---------------- #

st.markdown("""
<div class='footer'>

<hr>

Powered by ❤️ Streamlit | LangChain | Gemini 2.5 Flash

</div>
""",unsafe_allow_html=True)
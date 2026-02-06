import streamlit as st
import google.generativeai as genai
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from pyvi.ViTokenizer import tokenize
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import logging

load_dotenv()

# Config trang
st.set_page_config(page_title="Tư vấn Quy chế", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main > div {padding-top: 1rem;}
    #MainMenu, footer {visibility: hidden;}
    
    .user-bubble {
        background: #1e1e1e !important;
        color: white !important;
        padding: 14px 18px !important;
        border-radius: 20px 20px 4px 20px !important;
        max-width: 80%;
        margin-left: auto !important;
        margin-right: 0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        font-size: 1.05rem;
        line-height: 1.5;
    }
    .assistant-bubble {
        background: #1e1e1e !important;
        color: #ececf1 !important;
        padding: 14px 18px !important;
        border-radius: 20px 20px 20px 4px !important;
        max-width: 80%;
        margin-right: auto !important;
        margin-left: 0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        font-size: 1.05rem;
        line-height: 1.5;
    }
    .user-container {display: flex; justify-content: flex-end; align-items: flex-end; gap: 8px; margin-bottom: 1.5rem;}
    .assistant-container {display: flex; justify-content: flex-start; align-items: flex-end; gap: 8px; margin-bottom: 1.5rem;}
    .user-avatar, .assistant-avatar {width: 36px !important; height: 36px !important; border-radius: 50%; flex-shrink: 0;}

    .assistant-bubble table {
        border-collapse: collapse;
        width: 100%;
        margin: 16px 0;
        font-size: 0.95rem;
    }
    .assistant-bubble th, .assistant-bubble td {
        border: 1.5px solid #555 !important;
        padding: 10px 12px !important;
        text-align: left !important;
    }
    .assistant-bubble th {
        background-color: #2d2d3a !important;
    }
    .assistant-bubble tr:nth-child(even) {
        background-color: #2a2a34 !important;
    }
    .assistant-bubble .table-container {
        overflow-x: auto;
        border-radius: 12px;
        margin: 12px 0;
    }

    .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 12px;
        margin-top: 16px;
    }

    [data-testid="stSidebar"] .stButton button {
    padding: 0px 8px !important;
    width: 100% !important;
    border-radius: 6px !important;
    min-height: 38px !important;
    transition: all 0.2s;
    font-size: 0.9rem !important;
    }

    [data-testid="stSidebar"] .stButton button p {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    [data-testid="stSidebar"] .stButton button[kind="secondary"] {
        background-color: #262730 !important; 
        border: 1px solid #333 !important;
        color: #bbb !important;
    }
    [data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
        border-color: #666 !important;
        background-color: #363740 !important;
        color: #fff !important;
    }

    [data-testid="stSidebar"] .stButton button[kind="primary"] {
        background-color: #0e1117 !important; 
        border: 1px solid #4caf50 !important; 
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
        background-color: #1e1e1e !important;
        box-shadow: 0 0 4px rgba(76, 175, 80, 0.4);
    }

    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        gap: 4px !important;
        align-items: center !important;
    }
    [data-testid="stSidebar"] [data-testid="column"] {
        min-width: 0 !important;
        padding: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
mdl = genai.GenerativeModel('gemini-flash-latest')

@st.cache_resource
def load_resources():
    emb = SentenceTransformer(os.getenv("EMBEDDING_MODEL_PATH"))
    qd = QdrantClient(host=os.getenv("QDRANT_HOST"), port=int(os.getenv("QDRANT_PORT")))
    return emb, qd

emb, qd = load_resources()

# Quản lý lịch sử chat
HF = "chat_history.json"

def load_hist():
    if os.path.exists(HF):
        with open(HF, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_hist(h):
    with open(HF, "w", encoding="utf-8") as f:
        json.dump(h, f, ensure_ascii=False, indent=2)

if "full_history" not in st.session_state:
    st.session_state.full_history = load_hist()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar - lịch sử chat
with st.sidebar:
    st.markdown("### Lịch sử trò chuyện")
    
    if st.button("Bắt đầu hội thoại mới", use_container_width=True):
        nid = len(st.session_state.full_history) + 1
        nc = {
            "id": nid,
            "title": f"Trò chuyện mới {nid}",
            "timestamp": datetime.now().strftime("%H:%M %d/%m"),
            "messages": []
        }
        st.session_state.full_history.append(nc)
        st.session_state.current_chat_id = nid
        st.session_state.messages = []
        save_hist(st.session_state.full_history)
        st.rerun()

    st.markdown("---")
    st.markdown("---")
    for c in reversed(st.session_state.full_history):
        ck = f"chat_{c['id']}"
        
        col_title, col_edit, col_del = st.columns([6, 1.2, 1.2], gap="small")
        is_active = (c["id"] == st.session_state.current_chat_id)
        btn_type = "primary" if is_active else "secondary"

        with col_title:
            btn_label = f"{c['title']}"
            if st.button(
                btn_label, 
                key=ck, 
                help=f"{c['timestamp']} - {c['title']}", 
                use_container_width=True,
                type=btn_type 
            ):
                st.session_state.current_chat_id = c["id"]
                st.session_state.messages = [m.copy() for m in c["messages"]]
                st.rerun()

        with col_edit:
            if st.button("✏️", key=f"edit_{c['id']}", help="Đổi tên", use_container_width=True):
                st.session_state[f"editing_{c['id']}"] = True
        
        with col_del:
            if st.button("🗑️", key=f"del_{c['id']}", help="Xoá hội thoại", use_container_width=True):
                st.session_state[f"confirm_delete_{c['id']}"] = True
        
        if st.session_state.get(f"confirm_delete_{c['id']}", False):
            st.markdown(
                f"<small style='color:#ff6b6b;'>⚠️ Xoá hội thoại “{c['title'][:30]}...”?</small>",
                unsafe_allow_html=True
            )
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🗑️ Xoá luôn", key=f"yesdel_{c['id']}", type="primary"):
                    st.session_state.full_history = [
                        chat for chat in st.session_state.full_history 
                        if chat["id"] != c["id"]
                    ]
                    if st.session_state.current_chat_id == c["id"]:
                        if st.session_state.full_history:
                            latest = st.session_state.full_history[-1]
                            st.session_state.current_chat_id = latest["id"]
                            st.session_state.messages = [m.copy() for m in latest["messages"]]
                        else:
                            st.session_state.current_chat_id = None
                            st.session_state.messages = []
                    save_hist(st.session_state.full_history)
                    st.success("Đã xoá hội thoại!")
                    st.rerun()
            with col2:
                if st.button("Huỷ", key=f"nodelete_{c['id']}"):
                    st.session_state[f"confirm_delete_{c['id']}"] = False
                    st.rerun()

        # Form đổi tên
        if st.session_state.get(f"editing_{c['id']}", False):
            ci, cs, cc = st.columns([3, 1, 1])
            
            with ci:
                nt = st.text_input(
                    "", 
                    value=c["title"], 
                    key=f"input_{c['id']}",
                    label_visibility="collapsed",
                    placeholder="Nhập tên mới..."
                )
            
            with cs:
                if st.button("✓", key=f"save_{c['id']}"):
                    c["title"] = (nt.strip() or f"Trò chuyện {c['id']}")
                    save_hist(st.session_state.full_history)
                    st.session_state[f"editing_{c['id']}"] = False
                    st.rerun()
            
            with cc:
                if st.button("✕", key=f"cancel_{c['id']}"):
                    st.session_state[f"editing_{c['id']}"] = False
                    st.rerun()

        st.markdown("---")

# Header
st.markdown("<h1 style='text-align:center;'>Chatbot tư vấn quy chế học vụ</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>Học vụ • Học bổng • Thôi học • Chuyển ngành • Bảo lưu • Xét tốt nghiệp...</p>", unsafe_allow_html=True)
st.markdown("---")

# Tạo chat đầu nếu chưa có
if not st.session_state.full_history:
    nc = {"id": 1, "title": "Trò chuyện mới", "timestamp": datetime.now().strftime("%H:%M %d/%m"), "messages": []}
    st.session_state.full_history.append(nc)
    st.session_state.current_chat_id = 1
    st.session_state.messages = []
    save_hist(st.session_state.full_history)
    st.rerun()

# Đồng bộ current chat
cc = next((c for c in st.session_state.full_history if c["id"] == st.session_state.current_chat_id), None)
if cc and st.session_state.messages != cc["messages"]:
    st.session_state.messages = [m.copy() for m in cc["messages"]]

# Tự động đổi title từ câu hỏi đầu
if st.session_state.messages and cc["title"].startswith(("Trò chuyện mới", "Trò chuyện")):
    fu = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "")[:50]
    if fu:
        cc["title"] = fu + ("..." if len(fu) >= 50 else "")
        save_hist(st.session_state.full_history)

# Hiển thị tin nhắn
for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f"""
        <div class="user-container">
            <div class="user-bubble">{m["content"]}</div>
            <img src="https://ui-avatars.com/api/?name=You&background=666&color=fff&size=36" class="user-avatar">
        </div>
        """, unsafe_allow_html=True)
    else:
        ct = m["content"]
        if "|\n|" in ct or "<table" in ct:
            ct = f'<div class="table-container">{ct}</div>'
        st.markdown(f"""
        <div class="assistant-container">
            <img src="https://ui-avatars.com/api/?name=CTU&background=666&color=fff&size=36&bold=true" class="assistant-avatar">
            <div class="assistant-bubble">{ct}</div>
        </div>
        """, unsafe_allow_html=True)

        if m.get("images"):
            st.markdown("**Em đính kèm hình minh họa từ quy chế nhé:**")
            cols = st.columns(min(3, len(m["images"])))
            for iu, col in zip(m["images"][:6], cols):
                su = iu.replace("localhost", "127.0.0.1")
                col.image(su, use_container_width=True)

# Tìm kiếm
def search(q, k=15):
    v = emb.encode(tokenize(q)).tolist()
    h = qd.query_points(
        collection_name=os.getenv("QDRANT_COLLECTION"),
        query=v,
        limit=k
    ).points
    return h

def build_ctx(h):
    p = []
    for ht in h:
        p.append(ht.payload["content"])
        p.append("")
    return "\n".join(p)

# Chat input
if pr := st.chat_input("Nhập câu hỏi của bạn tại đây..."):
    st.session_state.messages.append({"role": "user", "content": pr})
    
    st.markdown(f"""
    <div class="user-container">
        <div class="user-bubble">{pr}</div>
        <img src="https://ui-avatars.com/api/?name=You&background=666&color=fff&size=36" class="user-avatar">
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Đang tìm quy định và soạn câu trả lời..."):
        try:
            h = search(pr)
            ctx = build_ctx(h)
            imgs = []
            for ht in h:
                imgs.extend(ht.payload.get("images", []))
            imgs = list(dict.fromkeys(imgs))[:6]

            # Lịch sử chat
            ch = ""
            for m in st.session_state.messages[:-1]:
                r = "Bạn" if m["role"] == "user" else "Trợ lý"
                ch += f"{r}: {m['content']}\n"

            sp = """Bạn là trợ lý AI tư vấn quy chế siêu thân thiện của Trường Đại học Cần Thơ.
Trả lời thật tự nhiên, gần gũi như đang chat với sinh viên, dùng "em" xưng hô, không bao giờ ghi nguồn, không trích dẫn điều khoản trong ngoặc, không ghi "[1]", "[Nguồn]", "theo Điều X" gì cả.
Nếu có bảng thì trả về dạng markdown đẹp.
Có thể suy luận và liên kết thông tin từ các câu hỏi trước đó."""

            fp = f"""{sp}

Lịch sử trò chuyện (nếu có):
{ch}

Thông tin từ quy chế (dùng để trả lời, không được trích dẫn trực tiếp):
{ctx}

Câu hỏi hiện tại: {pr}
Trả lời thân thiện, ngắn gọn, dễ hiểu:"""

            res = mdl.generate_content(
                fp,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=2048,
                )
            )
            ans = res.text

        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                ans = "Em xin lỗi, hôm nay em đã hết lượt trả lời miễn phí của Gemini rồi. Anh/chị thử lại vào ngày mai hoặc liên hệ admin để nâng cấp nhé!"
            else:
                logging.exception(e)
                ans = "Em đang gặp chút trục trặc kỹ thuật, anh/chị thử hỏi lại giúp em với ạ!"

    # Hiển thị câu trả lời
    if "|\n|" in ans or "<table" in ans:
        ans = f'<div class="table-container">{ans}</div>'

    st.markdown(f"""
    <div class="assistant-container">
        <img src="https://ui-avatars.com/api/?name=CTU&background=00b074&color=fff&size=36&bold=true" class="assistant-avatar">
        <div class="assistant-bubble">{ans}</div>
    </div>
    """, unsafe_allow_html=True)

    if imgs:
        st.markdown("**Em đính kèm hình minh họa từ quy chế nhé:**")
        cols = st.columns(min(3, len(imgs)))
        for iu, col in zip(imgs, cols):
            su = iu.replace("localhost", "127.0.0.1")
            col.image(su, use_container_width=True)

    # Lưu lịch sử
    st.session_state.messages.append({"role": "assistant", "content": ans, "images": imgs})
    for c in st.session_state.full_history:
        if c["id"] == st.session_state.current_chat_id:
            c["messages"] = [m.copy() for m in st.session_state.messages]
            break
    save_hist(st.session_state.full_history)
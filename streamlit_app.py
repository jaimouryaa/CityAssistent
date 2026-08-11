"""
Streamlit UI for the LangChain "City Assistant" agent.

Run with:
    streamlit run streamlit_app.py

Requires a .env file (or real env vars) with:
    MISTRAL_API_KEY=...
    OPENWEATHER_API_KEY=...
    TAVILY_API_KEY=...
"""

import os
import queue
import threading

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain_mistralai import ChatMistralAI
from tavily import TavilyClient

st.set_page_config(page_title="City Assistant", page_icon="🌆", layout="centered")

for key in ["MISTRAL_API_KEY", "OPENWEATHER_API_KEY", "TAVILY_API_KEY"]:
    if key not in os.environ and key in st.secrets:
        os.environ[key] = st.secrets[key]


# ============================================================
# Tools (unchanged from Agents.py)
# ============================================================


@tool
def get_weather(city: str) -> str:
    """Get current weather of a city"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    if str(data.get("cod")) != "200":
        return f"Error: {data.get('message', 'Could not fetch weather')}"

    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    return f"Weather in {city}: {desc}, {temp}°C"


@tool
def get_news(city: str) -> str:
    """Get latest news about a city"""
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = tavily_client.search(
        query=f"latest news in {city}", search_depth="basic", max_results=3
    )
    results = response.get("results", [])
    if not results:
        return f"No news found for {city}"

    news_list = []
    for r in results:
        title = r.get("title", "No title")
        url = r.get("url", "")
        snippet = r.get("content", "")
        news_list.append(f"- {title}\n  🔗 {url}\n  📝 {snippet[:100]}...")

    return f"Latest news in {city}:\n\n" + "\n\n".join(news_list)


TOOLS = [get_weather, get_news]

# ============================================================
# Session state
# ============================================================

DEFAULTS = {
    "messages": [],  # chat transcript shown in the UI
    "tool_log": [],  # history of approved/denied tool calls
    "approval_queue": None,  # queue.Queue() -> worker thread pushes pending approvals
    "response_queue": None,  # queue.Queue() -> worker thread pushes final answer/errors
    "awaiting_approval": None,  # currently displayed approval request (dict)
    "auto_approve_flag": [False],  # mutable 1-item list, safe to read from worker thread
    "running": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.approval_queue is None:
    st.session_state.approval_queue = queue.Queue()
if st.session_state.response_queue is None:
    st.session_state.response_queue = queue.Queue()


# ============================================================
# LLM + agent construction
# ============================================================


@st.cache_resource
def get_llm():
    return ChatMistralAI(model="mistral-small-2506")


def build_agent(approval_queue: queue.Queue, auto_approve_flag: list):
    """Build a fresh agent whose approval middleware talks to this run's queues."""

    @wrap_tool_call
    def human_approval(request, handler):
        tool_name = request.tool_call["name"]
        tool_args = request.tool_call.get("args", {})

        if auto_approve_flag[0]:
            return handler(request)

        event = threading.Event()
        req = {"tool_name": tool_name, "args": tool_args, "event": event, "answer": None}
        approval_queue.put(req)
        event.wait()  # blocks the worker thread until the UI thread answers

        if not req["answer"]:
            return ToolMessage(
                content="Tool call denied by user.",
                tool_call_id=request.tool_call["id"],
            )
        return handler(request)

    return create_agent(
        get_llm(),
        tools=TOOLS,
        system_prompt="you are a helpful city assistant.",
        middleware=[human_approval],
    )


def run_agent_in_thread(user_input: str):
    approval_queue = st.session_state.approval_queue
    response_queue = st.session_state.response_queue
    auto_approve_flag = st.session_state.auto_approve_flag
    history = list(st.session_state.messages)  # snapshot, thread-safe (read only)

    def worker():
        try:
            agent = build_agent(approval_queue, auto_approve_flag)
            lc_messages = [{"role": m["role"], "content": m["content"]} for m in history]
            lc_messages.append({"role": "user", "content": user_input})
            result = agent.invoke({"messages": lc_messages})
            final_text = result["messages"][-1].content
            response_queue.put({"ok": True, "text": final_text})
        except Exception as e:  # noqa: BLE001
            response_queue.put({"ok": False, "text": f"Error: {e}"})

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    st.session_state.agent_thread = t
    st.session_state.running = True


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.header("⚙️ Settings")

    auto_approve = st.toggle(
        "Auto-approve tool calls",
        value=st.session_state.auto_approve_flag[0],
        help="When off, you'll be asked to approve every weather/news lookup.",
    )
    st.session_state.auto_approve_flag[0] = auto_approve

    st.divider()
    st.subheader("🔑 API keys")
    for key in ["MISTRAL_API_KEY", "OPENWEATHER_API_KEY", "TAVILY_API_KEY"]:
        st.write(("✅ " if os.getenv(key) else "❌ ") + key)

    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.tool_log = []
        st.rerun()

    if st.session_state.tool_log:
        st.divider()
        st.subheader("🛠️ Tool call log")
        for entry in reversed(st.session_state.tool_log):
            icon = "✅" if entry["approved"] else "🚫"
            st.caption(f"{icon} {entry['tool_name']}({entry['args']})")

# ============================================================
# Main chat area
# ============================================================

st.title("🌆 City Assistant")
st.caption("Ask about the weather or latest news in any city.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input(
    "Ask me about a city...", disabled=st.session_state.running
)
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    run_agent_in_thread(user_input)
    st.rerun()


# ============================================================
# Polling fragment: handles approvals + streams the final answer
# ============================================================


@st.fragment(run_every="0.5s" if st.session_state.running else None)
def poll():
    approval_queue = st.session_state.approval_queue
    response_queue = st.session_state.response_queue

    # Pull in a new approval request if none is currently displayed
    if st.session_state.awaiting_approval is None and not approval_queue.empty():
        st.session_state.awaiting_approval = approval_queue.get()

    if st.session_state.awaiting_approval is not None:
        req = st.session_state.awaiting_approval
        with st.chat_message("assistant"):
            st.warning(
                f"🤖 Agent wants to call **{req['tool_name']}** "
                f"with arguments `{req['args']}`. Approve?"
            )
            c1, c2 = st.columns(2)
            if c1.button("✅ Approve", key=f"approve_{id(req)}", use_container_width=True):
                req["answer"] = True
                req["event"].set()
                st.session_state.tool_log.append(
                    {"tool_name": req["tool_name"], "args": req["args"], "approved": True}
                )
                st.session_state.awaiting_approval = None
                st.rerun()
            if c2.button("🚫 Deny", key=f"deny_{id(req)}", use_container_width=True):
                req["answer"] = False
                req["event"].set()
                st.session_state.tool_log.append(
                    {"tool_name": req["tool_name"], "args": req["args"], "approved": False}
                )
                st.session_state.awaiting_approval = None
                st.rerun()
        return  # don't check for the final response while a decision is pending

    if not response_queue.empty():
        result = response_queue.get()
        st.session_state.messages.append({"role": "assistant", "content": result["text"]})
        st.session_state.running = False
        st.rerun()
    elif st.session_state.running:
        with st.chat_message("assistant"):
            st.markdown("_thinking..._")


poll()

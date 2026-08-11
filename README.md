# 🌆 City Assistant - AI Agent with Tool Calling

An AI-powered **City Assistant** built with **Streamlit, LangChain, Mistral AI, Tavily, and OpenWeather API**.

The assistant can understand natural-language questions about cities and decide when to use external tools for **real-time weather information** and **latest city news**.

A key feature of this project is **human-in-the-loop tool approval**: before the AI agent calls a tool, the user can approve or deny the request.

---

## ✨ Features

* 🤖 **AI-powered conversational assistant**
* 🌤️ **Real-time weather information**
* 📰 **Latest city news**
* 🔧 **LangChain tool calling**
* 🧑‍💻 **Human-in-the-loop approval**
* ✅ Approve or 🚫 deny individual tool calls
* ⚡ Auto-approve mode for faster interactions
* 💬 Streamlit chat interface
* 📝 Tool-call activity log
* 🔐 Environment-variable based API key management
* 🧵 Background agent execution using Python threads
* 🔄 Real-time UI polling for tool approvals and agent responses

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │     User Query      │
                    │  "What's the weather│
                    │      in Ujjain?"    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Streamlit UI    │
                    │    Chat Interface   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    LangChain Agent  │
                    │                     │
                    │    Mistral AI LLM   │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
             ┌──────────────┐      ┌──────────────┐
             │ get_weather  │      │   get_news   │
             │    Tool      │      │     Tool     │
             └──────┬───────┘      └──────┬───────┘
                    │                     │
                    ▼                     ▼
             ┌──────────────┐      ┌──────────────┐
             │  OpenWeather │      │    Tavily    │
             │     API      │      │     API      │
             └──────────────┘      └──────────────┘
```

---

## 🧠 How It Works

The project uses a LangChain agent powered by **Mistral AI**.

When a user asks a question, the agent determines whether it needs one of the available tools.

For example:

```text
User:
What's the weather in Indore?
```

The agent can decide to call:

```text
get_weather("Indore")
```

Before the tool executes, the application can ask the user:

```text
🤖 Agent wants to call get_weather
with arguments {'city': 'Indore'}.

Approve?
```

The user can then:

```text
✅ Approve
```

or

```text
🚫 Deny
```

If approved, the tool executes and the result is returned to the agent.

---

# 🛠️ Tools

## 🌤️ Weather Tool

The `get_weather` tool retrieves current weather information using the OpenWeather API.

Example:

```text
What's the weather in Mumbai?
```

The tool returns information such as:

```text
Weather in Mumbai: clear sky, 29°C
```

The implementation uses:

```python
@tool
def get_weather(city: str) -> str:
```

---

## 📰 News Tool

The `get_news` tool uses Tavily to search for recent news related to a city.

Example:

```text
What's the latest news in Delhi?
```

The agent can call:

```python
get_news("Delhi")
```

The tool returns the top search results with:

* News title
* URL
* Short content snippet

---

# 👤 Human-in-the-Loop Approval

One of the main goals of this project is demonstrating **controlled AI tool usage**.

The agent does not automatically execute tools unless:

### Auto-Approve OFF

The user sees:

```text
🤖 Agent wants to call get_weather
with arguments {'city': 'Ujjain'}.

Approve?
```

Then the user can choose:

```text
✅ Approve
```

or:

```text
🚫 Deny
```

### Auto-Approve ON

Tool calls execute automatically without requiring manual approval.

This makes it possible to switch between:

**Safe / controlled mode**

and

**Fast / automatic mode**

---

# 📁 Project Structure

A recommended project structure is:

```text
S Rag project/
│
├── runnables and tools/
│   ├── streamlit_app.py
│   └── ...
│
├── .env
├── .gitignore
└── README.md
```

---

# ⚙️ Requirements

Make sure you have:

* Python 3.10+
* Streamlit
* LangChain
* Mistral AI integration
* Tavily Python SDK
* python-dotenv
* Requests

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_DIRECTORY>
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

You should see something similar to:

```text
(.venv) PS C:\your-project>
```

---

## 3. Install dependencies

```powershell
python -m pip install streamlit langchain langchain-mistralai tavily-python python-dotenv requests
```

---

# 🔑 API Keys

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
TAVILY_API_KEY=your_tavily_api_key
```

The application loads these variables using:

```python
from dotenv import load_dotenv

load_dotenv()
```



# ▶️ Running the Application

**Important:** This is a Streamlit application, so don't run it using:

```powershell
python streamlit_app.py
```

Instead use:

```powershell
python -m streamlit run streamlit_app.py
```

If your project contains spaces in the path, use quotes:

```powershell
python -m streamlit run "C:\Users\123\Desktop\GEN AI\Chatbots\S Rag project\runnables and tools\streamlit_app.py"
```

Streamlit will provide a local URL such as:

```text
http://localhost:8501
```

Open that URL in your browser.

---

# 🧪 Example Queries

Try asking:

```text
What's the weather in Ujjain?
```

```text
What's the weather in Mumbai?
```

```text
Tell me the latest news in Delhi.
```

```text
What's the weather like in Bangalore and what's the latest news there?
```

```text
Give me the latest news about Indore.
```

---

# 🔄 Agent Workflow

The application follows this general workflow:

```text
                User enters question
                         │
                         ▼
                  Streamlit UI
                         │
                         ▼
                  LangChain Agent
                         │
                         ▼
                    Mistral AI
                         │
             ┌───────────┴───────────┐
             │                       │
        Needs tool?              No tool
             │                       │
             ▼                       ▼
       Tool approval            Direct answer
             │
       ┌─────┴─────┐
       │           │
    Approve       Deny
       │           │
       ▼           ▼
   Execute       Return
     tool        denial
       │
       ▼
 Tool result → Agent → Final response
```

---

# 🧩 Technologies Used

| Technology          | Purpose                         |
| ------------------- | ------------------------------- |
| 🐍 Python           | Application programming         |
| 🎈 Streamlit        | Web interface                   |
| 🦜 LangChain        | Agent and tool orchestration    |
| 🤖 Mistral AI       | Large language model            |
| 🌤️ OpenWeather     | Weather data                    |
| 🔎 Tavily           | Web/news search                 |
| 🔐 python-dotenv    | Environment variable management |
| 🌐 Requests         | HTTP requests                   |
| 🧵 Python Threading | Background agent execution      |

---

# 🔐 Security Considerations

API keys should **never** be hardcoded into the source code.

Use:

```env
MISTRAL_API_KEY=...
OPENWEATHER_API_KEY=...
TAVILY_API_KEY=...
```

and keep `.env` out of Git.

If an API key is accidentally committed to GitHub, revoke it immediately and generate a new key.

---

# 🐛 Troubleshooting

## `ModuleNotFoundError: No module named 'tavily'`

Install:

```powershell
python -m pip install tavily-python
```

Then verify:

```powershell
python -c "from tavily import TavilyClient; print('Tavily OK')"
```

---

## PowerShell says `Unexpected token '-m'`

If you're using the complete Python executable path in PowerShell, use `&`:

```powershell
& "C:\path\to\.venv\Scripts\python.exe" -m pip install tavily-python
```

For example:

```powershell
& "C:\Users\123\Desktop\GEN AI\Chatbots\chatbot krish\.venv\Scripts\python.exe" -m pip install tavily-python
```

---

## Streamlit says `missing ScriptRunContext`

Make sure you are using:

```powershell
python -m streamlit run streamlit_app.py
```

and **not**:

```powershell
python streamlit_app.py
```

---

## API key errors

Check that your `.env` contains:

```env
MISTRAL_API_KEY=...
OPENWEATHER_API_KEY=...
TAVILY_API_KEY=...
```

You can also check the application's sidebar, which displays whether the required keys are detected.

---

# 🚧 Future Improvements

Possible improvements include:

* 🌍 Support for cities outside India
* 📍 Automatic location detection
* 🌡️ Multi-day weather forecasts
* 📰 Better news summarization
* 🔗 Clickable news sources
* 🗺️ Maps and location information
* 💾 Persistent conversation history
* 🔐 More granular tool permissions
* 🧠 Long-term conversational memory
* ⚡ Async tool execution
* 📊 Weather visualization
* 🚀 Deployment to Streamlit Community Cloud / Cloud Run
* 🧪 Automated tests for tools and agent behavior

---

# 🎯 Learning Objectives

This project demonstrates several important concepts in modern AI application development:

1. **LLM-powered agents**
2. **Tool calling**
3. **Human-in-the-loop AI**
4. **External API integration**
5. **LangChain agent orchestration**
6. **Streamlit application development**
7. **Environment variable management**
8. **Threading and asynchronous-style UI workflows**
9. **Real-time information retrieval**
10. **Controlled execution of AI-generated actions**

---

# 👨‍💻 Author

**Jai Mourya**

Built as a hands-on project for learning and experimenting with:

**Generative AI • AI Agents • LangChain • Tool Calling • Mistral AI • Streamlit**

---

## ⭐ If you found this project useful

Consider giving the repository a ⭐ on GitHub!

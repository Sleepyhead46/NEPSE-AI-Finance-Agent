# 🔍 NEPSE Multi-Agent AI System — Detailed End-to-End Process

This document walks through the **complete process** of the NEPSE Multi-Agent AI System, from installation and startup, through data fetching and agent orchestration, to the final rendering of an AI-powered market analysis. Every step below maps directly to code in `app.py`, `main.py`, and `nepse_data.py`.

---

## 📑 Table of Contents

1. [System Overview](#1-system-overview)
2. [Setup & Installation](#2-setup--installation)
3. [Startup Phase (`streamlit run app.py`)](#3-startup-phase)
4. [UI Rendering Process](#4-ui-rendering-process)
5. [Data Layer Flow (NEPSE Live Data)](#5-data-layer-flow)
6. [Agent Orchestration](#6-agent-orchestration)
7. [Query Processing Pipeline (Start → End)](#7-query-processing-pipeline)
8. [Market Trends & All-Stocks Table](#8-market-trends--all-stocks-table)
9. [Full End-to-End Sequence (One Query)](#9-full-end-to-end-sequence)
10. [Logging & Troubleshooting](#10-logging--troubleshooting)

---

## 1. System Overview

The **NEPSE Multi-Agent AI System** is a Streamlit web application that analyzes the **Nepali Stock Market (NEPSE)** using a team of AI agents:

| Component | Responsibility |
|-----------|----------------|
| 🌐 **Web Agent** | Searches the web (via SerpAPI) for Nepali market news, NEPSE developments, and company fundamentals |
| 💰 **Finance Agent** | Calls LIVE NEPSE data tools for real market data, prices, gainers/losers, sectors, and trends |
| 🤝 **Team Coordinator** | Orchestrates both agents — prefers the Finance Agent's **live data** for numbers and the Web Agent's results for **news/fundamentals** |

**Technology Stack:**
- **Frontend:** Streamlit (`app.py`)
- **LLM:** Groq — LLaMA 3.3 70B Versatile (`main.py`)
- **Web Search:** SerpAPI via Phi's `SerpApiTools`
- **Market Data:** NepalIPaisa public API (`nepse_data.py`)
- **Env Management:** python-dotenv (`.env`)

**File Map:**

```
├── app.py            → Streamlit UI, layout, session state, rendering
├── main.py           → Agent initialization + query processing logic
├── nepse_data.py     → LIVE NEPSE data (stdlib only, TTL cache, 12+ functions)
├── requirements.txt  → Dependencies
├── readme.md         → Quick-start overview
└── .gitignore        → Ignore .env, __pycache__, .vscode
```

---

## 2. Setup & Installation

### 2.1 Prerequisites

- **Python 3.8+**
- **Groq API Key** — from [console.groq.com](https://console.groq.com/) *(required)*
- **SerpAPI Key** — from [serpapi.com](https://serpapi.com/) *(used by Web Agent; optional but recommended)*

### 2.2 Step-by-Step Installation

1. **Clone or download** the repository.
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   This installs: `streamlit`, `phidata`, `groq`, `python-dotenv`, `serpapi`, `google-search-results`.
3. **Create a `.env` file** in the project root:
   ```bash
   # .env
   GROQ_API_KEY=your_groq_api_key_here
   SERPAPI_API_KEY=your_serpapi_api_key_here
   ```
4. **(Optional) Smoke-test the data module:**
   ```bash
   python nepse_data.py
   ```
   This runs `test_nepse_data()` which prints the market overview, NABIL stock info, a "bank" search, market trend, and sector trends — validating API connectivity before launching the UI.
5. **Run the app:**
   ```bash
   streamlit run app.py
   ```
6. **Open** `http://localhost:8501` — Streamlit auto-opens the browser.

---

## 3. Startup Phase

The moment `streamlit run app.py` is executed, the following happens **in order**:

### 3.1 Imports & Logging Setup
- `app.py` imports `streamlit`, `datetime`, `logging`, `nepse_data`, and `initialize_agents` / `process_agent_query` from `main`.
- `main.py` configures root logging at `INFO` level with a `%(asctime)s - %(name)s - %(levelname)s - %(message)s` format.
- `main.py` calls `load_dotenv()` to read `GROQ_API_KEY` and `SERPAPI_API_KEY` into the environment.
- `main.py` defines `NEPSE_TOOLS` — a list of **12 live-data functions** from `nepse_data.py` that will be exposed to the Finance Agent:
  `get_market_overview, get_top_gainers, get_top_losers, get_top_volume, get_top_traded, get_stock_info, search_stock, get_company_list, get_sector_stocks, get_all_stocks_table, get_market_trend, get_sector_trends`

### 3.2 Streamlit Page Configuration
```python
st.set_page_config(
    page_title="NEPSE Multi-Agent AI System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### 3.3 Custom CSS Injection
A `<style>` block is injected via `st.markdown(..., unsafe_allow_html=True)` to style:
- `.agent-response` — response cards with a green left border and transparent blue background
- `.query-box` — query display boxes
- `.agent-card` — sidebar agent descriptions
- Buttons — rounded corners, hover lift effect
- Tables inside agent responses — styled headers/cells that inherit text color for dark/light themes

### 3.4 Session State Initialization
Streamlit reruns the script on every interaction, so session state must be initialized once:
```python
if 'chat_history'   not in st.session_state: st.session_state.chat_history = []
if 'total_queries'  not in st.session_state: st.session_state.total_queries = 0
if 'process_query'  not in st.session_state: st.session_state.process_query = False
if 'current_query'  not in st.session_state: st.session_state.current_query = ""
```

### 3.5 Main Flow Call
The script reaches the bottom and calls `main()`, which renders the UI in this order:
1. `render_sidebar()`
2. App title + subtitle
3. `render_quick_actions()` (includes live market cards)
4. `render_query_input()`
5. `process_query()` (handles pending queries)
6. `render_chat_history()`
7. `render_market_trends()`
8. `render_all_stocks()`

---

## 4. UI Rendering Process

### 4.1 Sidebar (`render_sidebar`)
- Shows the system title and agent-team descriptions.
- Displays **session stats**: total queries and chat-history count via `st.metric`.
- A **"Clear History"** button resets `chat_history` and `total_queries` to zero, logs the event, and calls `st.rerun()`.

### 4.2 Live Market Snapshot Cards (`render_live_market_cards`)
1. Calls `nepse_data.get_market_snapshot()`.
2. If no data → shows "⏳ Market data is loading...".
3. Otherwise renders **5 metric cards**:
   - **Avg Market Change** — with ▲/▼ arrow and advancer count
   - **Total Turnover** (Rs)
   - **Shares Traded**
   - **Top Gainer** (symbol + % change)
   - **Top Loser** (symbol + % change)
4. A caption below shows trade date, decliner count, unchanged count, and total stocks tracked.

### 4.3 Quick Analysis Buttons (`render_quick_actions`)
This renders three groups of buttons, each wired to `_trigger_query()`:

1. **Popular Stocks (dynamic)** — `_get_popular_stocks(limit=8)`:
   - Fetches `nepse_data.get_all_stocks()`
   - Sorts all stocks by **turnover** (`amount`) descending
   - Returns the top 8 as `{symbol, company, change}`
   - Rendered in 2 rows of 4 buttons, each labeled `SYMBOL ▲ (+x.xx%)` with a tooltip showing the company name.
   - **Fallback:** if live data fails, renders a hardcoded list (NABIL, EBL, NRIC, ADBL, SHIVM, CHCL, NMB, CIT).
   - Clicking any triggers: `"Provide detailed analysis and recent information about {SYMBOL} stock (Nepal Stock Exchange)"`.

2. **Market Scans** — 4 buttons:
   - 🚀 Top Gainers → `"What are today's top gainers in NEPSE? Use live data and show a table."`
   - 📉 Top Losers → similar with losers
   - 📊 Most Traded → volume/turnover query
   - 💰 Market Overview → full market conditions query

3. **Sector Analysis** — 4 buttons:
   - 🏦 Banking, ⚡ Hydropower, 🛡️ Insurance, 💳 Microfinance
   - Each triggers: `"Analyze the {sector} sector stocks in NEPSE using live data and show key metrics."`

### 4.4 Custom Query Input (`render_query_input`)
- A text input with placeholder `"e.g., Analyze NABIL stock or show today's top gainers in NEPSE"`.
- An **"🚀 Analyze"** button sets `current_query` and `process_query = True`, then logs the submission.

---

## 5. Data Layer Flow

`nepse_data.py` is the foundation of all live market information. It uses **only the Python standard library** (`urllib`, `json`, `time`).

### 5.1 API Endpoint & Caching
```python
API_URL = "https://nepalipaisa.com/api/GetStockLive"
CACHE_TTL_SECONDS = 60
_cache = {"timestamp": 0.0, "data": None}
```

### 5.2 `_fetch_live_data(force_refresh=False)` — The Core Fetcher
1. **Cache check:** if data exists and is younger than 60 seconds, return cached data immediately (no API call).
2. **API request:** otherwise, build a `urllib.request.Request` with a `User-Agent: Mozilla/5.0` header and `urlopen(..., timeout=15)`.
3. **Parse:** decode the JSON, extract `result.stocks` and `result.summary`.
4. **Cache & log:** store `{stocks, summary}` with the current timestamp; log `"Fetched %d stocks from NEPSE API"`.
5. **Error handling:** on any exception, log the error and **return stale cached data** if available. If no cache exists, raise `RuntimeError("Could not fetch NEPSE data: ...")`.

### 5.3 Helper: `_as_float(value, default=0.0)`
Safely converts API values to floats, defaulting to `0.0` on `TypeError`/`ValueError`.

### 5.4 Formatting: `_fmt_stock(s)`
Builds a human-readable one-line quote:
```
SYMBOL - Company Name | LTP: Rs X.XX | Change: +X.XX (+X.XX%) | Prev Close: Rs X.XX | Open: Rs X.XX | High: Rs X.XX | Low: Rs X.XX | Volume: N | Turnover: Rs X.XX | Txn: N
```

### 5.5 The 12 Data Functions (Tools)

| Function | Purpose |
|----------|---------|
| `get_market_summary()` | Raw summary dict (totalAmount, totalShares, totalTxns) |
| `get_all_stocks()` | Full list of live stock quotes |
| `get_market_overview(limit=5)` | Text block: summary + top gainers/losers/volume/turnover |
| `get_top_gainers(limit=10)` | Top stocks by % change (desc) |
| `get_top_losers(limit=10)` | Top stocks by % change (asc) |
| `get_top_volume(limit=10)` | Highest traded volume |
| `get_top_traded(limit=10)` | Highest turnover (Rs) |
| `get_stock_info(symbol)` | Detailed quote for a symbol (uppercased lookup) |
| `search_stock(query)` | Search by symbol/company keyword (max 10 matches) |
| `get_company_list()` | All NEPSE symbols, comma-separated |
| `get_sector_stocks(keyword)` | Stocks whose name matches a sector keyword (e.g. bank) |
| `get_all_stocks_table()` | List of dicts ready for a pandas dataframe |
| `get_market_snapshot()` | Structured dict for dashboard cards (advancers, decliners, avg change, top gainer/loser, trade date) |
| `get_market_trend()` | Breadth + sentiment analysis (BULLISH/BEARISH classification) |
| `get_sector_trends()` | Average % change & turnover per sector (banking, insurance, hydropower, etc.) |

### 5.6 Market Trend Logic (`get_market_trend`)
- Computes total stocks, advancers, decliners, unchanged, avg % change, total volume, total turnover.
- Classifies sentiment:
  - `avg > +0.5` → **STRONGLY BULLISH**
  - `avg > 0` → **MILDLY BULLISH**
  - `avg > -0.5` → **MILDLY BEARISH**
  - else → **STRONGLY BEARISH**

### 5.7 Sector Trends (`get_sector_trends`)
Groups companies by keyword matching in `companyName` (e.g. "bank", "insurance", "laghubitta", "hydropower", "hotel", "fund", etc.) and reports each sector's stock count, average % change, and total turnover.

---

## 6. Agent Orchestration

`main.py` builds the agent team using the **Phi Agent Framework** (`phidata`).

### 6.1 Web Agent 🌐
```python
web_agent = Agent(
    name="Web Agent",
    role="Search the web for information about the Nepali stock market (NEPSE)",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[SerpApiTools()],
    instructions=[
        "Always include sources", "Provide latest information using search results",
        "Provide URLs when available",
        "Focus on Nepali market news, NEPSE developments, and Nepalese economy",
    ],
    show_tool_calls=True, markdown=True,
)
```

### 6.2 Finance Agent 💰
```python
finance_agent = Agent(
    name="Finance Agent",
    role="Get live NEPSE financial data and provide analysis for the Nepali stock market",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=NEPSE_TOOLS,   # 12 live data functions
    instructions=[
        "Use tables to display data", "Provide clear financial analysis",
        "Use the NEPSE tools to get REAL live data from the Nepal Stock Exchange",
        "Prices are in Nepalese Rupees (NPR). Always state 'Rs' for amounts.",
        "Use get_stock_info() for a single stock, search_stock() to find a company by name",
        "Use get_top_gainers(), get_top_losers(), get_top_volume(), get_top_traded() for market movers",
        "Use get_sector_stocks() to analyze a sector",
        "If the NEPSE tool fails, say that live data is unavailable and fall back to general knowledge",
    ],
    show_tool_calls=True, markdown=True,
)
```

### 6.3 Team Coordinator 🤝
```python
agent_team = Agent(
    name="Team Coordinator",
    model=Groq(id="llama-3.3-70b-versatile"),
    team=[web_agent, finance_agent],
    instructions=[
        "Always include sources", "Use tables to display data",
        "Coordinate between agents to provide comprehensive answers",
        "If one agent fails, use the other agent's information",
        "Prefer the Finance Agent's live NEPSE data for numbers",
        "Use the Web Agent for news, announcements, and company fundamentals",
        "Report prices in Nepalese Rupees (Rs/NPR)",
        "Mention that data is as per NEPSE trading date when available",
    ],
    show_tool_calls=True, markdown=True,
)
```

### 6.4 Initialization Flow (`initialize_agents`)
1. Log `"Initializing Web Agent..."` → build Web Agent → log success.
2. Log `"Initializing Finance Agent with NEPSE tools..."` → build Finance Agent → log success.
3. Log `"Initializing Agent Team..."` → wrap both in the Team Coordinator → log success.
4. Return the team.
5. On any exception: log `"Error initializing agents: ..."` with traceback and **re-raise** so the UI can catch it.

---

## 7. Query Processing Pipeline

This is the **heart of the end-to-end process**. Here is exactly what happens from a user click to a rendered answer.

### 7.1 Step 1 — Trigger
A user clicks a quick-action button or the Analyze button → `_trigger_query(query, label)` or the Analyze handler sets:
```python
st.session_state.current_query = query
st.session_state.process_query = True
```

### 7.2 Step 2 — Process Gate
`process_query()` runs (called inside `main()`). It checks `st.session_state.process_query and st.session_state.current_query`.

### 7.3 Step 3 — Bookkeeping
- Increments `total_queries`.
- Logs `"Processing query #{n}: {query}"`.
- **Resets the flag** `process_query = False` (prevents re-processing on reruns).
- Shows a spinner: `"🤖 Agent team is analyzing your query..."`.

### 7.4 Step 4 — Agent Initialization
Calls `initialize_agents()`. If it returns `None`/fails, the UI shows `"❌ Failed to initialize agent team. Check logs for details."`.

### 7.5 Step 5 — Query + Response Display
- Timestamps the query (`datetime.now().strftime('%Y-%m-%d %H:%M:%S')`).
- Renders a `.query-box` div with the query and timestamp.
- Calls `process_agent_query(agent_team, query_to_process)`.

### 7.6 Step 6 — `process_agent_query` (the call into the LLM)
1. Logs the attempt and calls `agent_team.run(query)`.
2. Returns `response.content` if it exists, else `str(response)`.
3. **Error handling / retry:**
   - On exception, logs the error with traceback.
   - If the message contains `"tool_use_failed"`:
     - Builds a **simplified query**: `"Provide information about {query.split('for')[-1] ...}"`.
     - Retries `agent_team.run(simplified_query)`.
     - If the retry also fails, logs and re-raises.
   - Otherwise re-raises the original error.

### 7.7 Step 7 — Render the Response
- Wraps the response in a `.agent-response` styled div.
- `st.success("✅ Analysis complete!")`.

### 7.8 Step 8 — Save to Chat History
```python
st.session_state.chat_history.append({
    "query": query_to_process,
    "response": full_response,
    "timestamp": timestamp,
})
```

### 7.9 Step 9 — Error Path (if an exception occurred)
- Logs `"Error processing query: {str(e)}"` with traceback.
- Shows `st.error("❌ Error: {str(e)}")`.
- If `"tool_use_failed"` in the message, warns that web search failed and agents will use their knowledge base.
- Displays troubleshooting tips:
  - Rephrase the query more simply
  - Check `GROQ_API_KEY` in `.env`
  - Verify internet connection
  - Ask about a single topic instead of multiple

---

## 8. Market Trends & All-Stocks Table

### 8.1 `render_market_trends()`
Renders two columns from live data:
- **🧭 Market Breadth** — from `get_market_trend()` (advancers/decliners/unchanged, avg change, volume, turnover, sentiment)
- **🏭 Sector Performance** — from `get_sector_trends()` (per-sector avg % change & turnover)

Both are shown in `<pre>` code blocks via `st.code`. Failures log an error and show `"⚠️ Could not load live trend data. Try again shortly."`

### 8.2 `render_all_stocks()`
1. Calls `get_all_stocks_table()` → list of dicts for all 300+ stocks.
2. Displays `### Total: {n} listed stocks`.
3. **Filters:**
   - 🔍 Text search on symbol or company name.
   - Sort by: Change (%), LTP (Rs), Volume, Turnover (Rs), or Symbol.
   - Order: Descending / Ascending.
4. **Color-coding:** positive changes → green, negative → red, zero → gray (applied to the "Change (%)" column via pandas `Styler.map`).
5. Renders a paginated/scrollable `st.dataframe` (height 500). Falls back to plain `st.dataframe(rows)` if pandas isn't installed.

---

## 9. Full End-to-End Sequence

Here is the complete lifecycle for one query, e.g. a user clicks **"🏦 Banking"**:

```
User clicks "Banking" button
        │
        ▼
_trigger_query("Analyze the banking sector stocks in NEPSE using live data and show key metrics.", "Banking")
        │  sets session_state.current_query + process_query=True
        ▼
process_query() gate passes
        │
        ▼
Increment total_queries | reset process_query=False | show spinner
        │
        ▼
initialize_agents()
   ├── Web Agent (SerpApiTools) 🌐
   ├── Finance Agent (12 NEPSE tools) 💰
   └── Team Coordinator (wraps both) 🤝
        │
        ▼
process_agent_query(agent_team, query)
        │
        ├── Team Coordinator parses the intent
        │     ├── delegates to Finance Agent → get_sector_stocks("bank")
        │     │        └── _fetch_live_data() → cache check (60s TTL)
        │     │              ├── fresh? return cached
        │     │              └── stale? GET https://nepalipaisa.com/api/GetStockLive
        │     │                     ├── success → cache + return
        │     │                     └── failure → stale fallback or RuntimeError
        │     └── delegates to Web Agent → SerpAPI news search
        │              ├── success → sources + URLs
        │              └── failure → tool_use_failed → simplified retry
        │
        ├── LLaMA 3.3 70B synthesizes answer (markdown tables, Rs amounts)
        │
        ▼
Return full_response (content) to app.py
        │
        ▼
Render response in .agent-response styled div
        │
        ▼
Append {query, response, timestamp} to chat_history
        │
        ▼
st.success("✅ Analysis complete!")
```

### Data-Fetch Timelines (Caching Behavior)

| Event | Cache timestamp | API call? |
|-------|-----------------|-----------|
| App loads (first request) | `0.0` | ✅ Yes — first fetch |
| Within 60s of first fetch | recent | ❌ No — served from cache |
| After 60s (new interaction) | stale | ✅ Yes — refreshed |
| API down + cache exists | — | ✅ Attempt, then stale fallback |
| API down + no cache | — | ❌ RuntimeError raised |

---

## 10. Logging & Troubleshooting

### 10.1 Logging Flow
- Root logger configured in `main.py` at `INFO` level.
- Each module uses `logging.getLogger(__name__)`.
- Key log events:
  - `"Fetched %d stocks from NEPSE API"` — data layer success
  - `"Failed to fetch NEPSE data: %s"` / `"Returning stale cached NEPSE data"` — data layer fallback
  - `"Initializing Web Agent..."` / `"Finance Agent..."` / `"Agent Team..."` — agent setup
  - `"Processing query #{n}: {query}"` — query lifecycle
  - `"Tool error detected, retrying with simpler query..."` — retry path
  - `"Error processing query: {str(e)}"` — UI-level failure

### 10.2 Common Issues & Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| `❌ Failed to initialize agent team` | Missing/invalid `GROQ_API_KEY` | Add the key to `.env`, restart the app |
| Web search fails / tool_use_failed | Missing SerpAPI key

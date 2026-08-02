# 🧠 NEPSE Multi-Agent AI System — Code Explanation

This document explains **how the code works** — file by file, function by function. It maps every piece of code to its purpose, showing how data flows and modules connect.

---

## 📁 File Structure

```
├── app.py           → Streamlit UI (frontend + user interaction)
├── main.py          → Agent setup + query processing (business logic)
├── nepse_data.py    → Live NEPSE market data (data layer)
├── requirements.txt → Python dependencies
├── readme.md        → Quick-start guide
└── .gitignore       → Git ignore rules
```

### Module Dependency Graph

```
   app.py
    │
    ├── imports → nepse_data.py  (for live market cards, stock table, trend data)
    │
    └── imports → main.py        (for initialize_agents(), process_agent_query())
                      │
                      └── imports → nepse_data.py  (exposes 12 functions as NEPSE_TOOLS)
```

---

## 1️⃣ `nepse_data.py` — The Data Layer

**Purpose:** Fetch, cache, and format live NEPSE stock data from the NepalIPaisa API using only Python standard library (`urllib`, `json`, `time`). No external dependencies.

### Global Variables

```python
API_URL = "https://nepalipaisa.com/api/GetStockLive"
CACHE_TTL_SECONDS = 60
_cache = {"timestamp": 0.0, "data": None}
```

- `API_URL` — The public endpoint for live NEPSE data.
- `CACHE_TTL_SECONDS` — Data is cached for 60 seconds to avoid hitting the API on every rerun.
- `_cache` — In-memory dict: `timestamp` (when last fetched) + `data` (the parsed JSON result).

### Core Functions

#### `_fetch_live_data(force_refresh=False)`
The **heart of the data layer**. Every other data function calls this.

```python
def _fetch_live_data(force_refresh=False):
    now = time.time()
    # Cache hit? Return cached data (if within TTL)
    if (not force_refresh and _cache["data"] is not None
        and (now - _cache["timestamp"]) < CACHE_TTL_SECONDS):
        return _cache["data"]

    try:
        # Build HTTP request with User-Agent header
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
        payload = json.loads(raw)
        result = payload.get("result") or {}
        data = {
            "stocks": result.get("stocks", []),
            "summary": result.get("summary", {}),
        }
        # Update cache
        _cache["data"] = data
        _cache["timestamp"] = now
        return data
    except Exception as e:
        # API failure → return stale cache if available
        if _cache["data"] is not None:
            return _cache["data"]
        raise RuntimeError(f"Could not fetch NEPSE data: {e}")
```

**Flow:**
1. Check if valid cached data exists (within 60s) → return it immediately.
2. Otherwise, make a GET request to the NepalIPaisa API.
3. Parse JSON, extract `stocks` list and `summary` dict.
4. Store in cache, update timestamp.
5. On failure → return stale cache as fallback, or raise `RuntimeError`.

#### `_as_float(value, default=0.0)`
Safe type converter — returns `float(value)` or `default` if conversion fails.

#### `_fmt_stock(s)`
Formats a single stock dict into a human-readable string:
```
SYMBOL - Company | LTP: Rs X.XX | Change: +X.XX (+X.XX%) | ... | Volume: X | Turnover: Rs X.XX | Txn: X
```

### 12 Public Data Functions (Used as Agent Tools)

| Function | Signature | Returns | Logic |
|----------|-----------|---------|-------|
| `get_market_summary()` | `() → dict` | Raw summary dict | `_fetch_live_data()["summary"]` |
| `get_all_stocks()` | `() → list[dict]` | Full stock list | `_fetch_live_data()["stocks"]` |
| `get_market_overview(limit=5)` | `(int) → str` | Text block: summary + top gainers/losers/volume/turnover | Sort stocks by % change (desc/asc), volume (desc), turnover (desc) |
| `get_top_gainers(limit=10)` | `(int) → str` | Text list of top gainers | `sorted(stocks, key=percentChange, reverse=True)[:limit]` |
| `get_top_losers(limit=10)` | `(int) → str` | Text list of top losers | `sorted(stocks, key=percentChange)[:limit]` |
| `get_top_volume(limit=10)` | `(int) → str` | Text list by volume | `sorted(stocks, key=volume, reverse=True)[:limit]` |
| `get_top_traded(limit=10)` | `(int) → str` | Text list by turnover | `sorted(stocks, key=amount, reverse=True)[:limit]` |
| `get_stock_info(symbol)` | `(str) → str` | Single stock detail | Match by uppercased `stockSymbol` → `_fmt_stock()` |
| `search_stock(query)` | `(str) → str` | Up to 10 matching stocks | `query.lower()` in `stockSymbol.lower()` or `companyName.lower()` |
| `get_company_list()` | `() → str` | Comma-separated symbols | `sorted(symbols)` joined by `", "` |
| `get_sector_stocks(keyword)` | `(str) → str` | Stocks matching sector keyword | Match `keyword.lower()` in `companyName` or `stockSymbol` |
| `get_all_stocks_table()` | `() → list[dict]` | All stocks as dicts for dataframe | Each dict: `Symbol, Company, LTP (Rs), Change (Rs), Change (%), Open, High, Low, Prev Close, Volume, Turnover, Txn` |
| `get_market_snapshot()` | `() → dict or None` | Structured snapshot for dashboard cards | Computes: advancers, decliners, unchanged, avg_change, top_gainer, top_loser, trade_date |
| `get_market_trend()` | `() → str` | Breadth + sentiment analysis | Avg % change → sentiment classification (STRONGLY BULLISH / MILDLY BULLISH / MILDLY BEARISH / STRONGLY BEARISH) |
| `get_sector_trends()` | `() → str` | Per-sector performance | Groups by keyword matching (11 sectors) → avg % change + total turnover |

### Sentiment Classification Logic (`get_market_trend`)

```python
if avg_change > 0.5:       sentiment = "STRONGLY BULLISH"
elif avg_change > 0:       sentiment = "MILDLY BULLISH"
elif avg_change > -0.5:    sentiment = "MILDLY BEARISH"
else:                      sentiment = "STRONGLY BEARISH"
```

### Sector Keyword Mapping (`get_sector_trends`)

```python
sectors = {
    "Commercial Banks":       ["bank"],
    "Development Banks":      ["development bank"],
    "Finance":                ["finance"],
    "Insurance":              ["insurance"],
    "Microfinance":           ["laghubitta", "microfinance"],
    "Hydropower":             ["hydropower", "khola", "power"],
    "Hotel & Tourism":        ["hotel", "resort", "tourism"],
    "Manufacturing & Processing": ["mills", "manufacturing", "distillery", "bottlers", "cement"],
    "Trading":                ["trading"],
    "Investment":             ["investment"],
    "Mutual Funds":           ["fund"],
}
```

### `test_nepse_data()`
A CLI smoke test (runs when `python nepse_data.py` is executed):
1. Prints `get_market_overview(limit=5)`
2. Prints `get_stock_info("NABIL")`
3. Prints `search_stock("bank")` (truncated to 800 chars)
4. Prints `get_market_trend()`
5. Prints `get_sector_trends()`

---

## 2️⃣ `main.py` — Agent System & Query Processing

**Purpose:** Initialize the multi-agent AI team (Web Agent + Finance Agent + Team Coordinator) and process user queries through them.

### Key Imports

```python
from phi.agent import Agent                # Phi framework agent class
from phi.tools.serpapi_tools import SerpApiTools  # Google search tool
from phi.model.groq import Groq            # Groq LLM interface
from dotenv import load_dotenv             # .env file reader
import os, logging
import nepse_data                          # All 12 NEPSE tools
```

### NEPSE_TOOLS — The Tool Registry

```python
NEPSE_TOOLS = [
    nepse_data.get_market_overview,
    nepse_data.get_top_gainers,
    nepse_data.get_top_losers,
    nepse_data.get_top_volume,
    nepse_data.get_top_traded,
    nepse_data.get_stock_info,
    nepse_data.search_stock,
    nepse_data.get_company_list,
    nepse_data.get_sector_stocks,
    nepse_data.get_all_stocks_table,
    nepse_data.get_market_trend,
    nepse_data.get_sector_trends,
]
```

This list is passed to the Finance Agent as its `tools` parameter. The Phi framework automatically converts each function into a callable tool that the LLM can invoke.

### `initialize_agents()`

```python
def initialize_agents():
    """Returns: agent_team (Agent) or raises exception"""
```

**Step-by-step:**

1. **Web Agent** (`SerpApiTools`):
   - Uses Groq LLaMA 3.3 70B as the LLM.
   - Has `SerpApiTools()` for web search (requires `SERPAPI_API_KEY` in `.env`).
   - Instructions: include sources, latest info, URLs, focus on Nepali market.

2. **Finance Agent** (12 NEPSE tools):
   - Same LLM model.
   - Has `NEPSE_TOOLS` (all 12 data functions).
   - Instructions: use tables, format Rs amounts, use specific tools for specific tasks, fallback on tool failure.

3. **Team Coordinator**:
   - Same LLM model.
   - `team=[web_agent, finance_agent]` — delegates to sub-agents.
   - Instructions: prefer Finance Agent for numbers, Web Agent for news, coordinate, handle failures.

4. Returns `agent_team` on success, re-raises on failure.

### `process_agent_query(agent_team, query)`

```python
def process_agent_query(agent_team, query):
    """Returns: str (response content)"""
```

**Flow:**
1. Calls `agent_team.run(query)`.
2. Returns `response.content` if it exists, else `str(response)`.
3. **Error handling:**
   - If `"tool_use_failed"` in error message → builds a **simplified query** and retries.
   - If retry fails → re-raises.
   - Other errors → re-raises immediately.

---

## 3️⃣ `app.py` — Streamlit User Interface

**Purpose:** The frontend — renders the UI, handles user interactions, and wires everything together.

### Session State Variables

```python
st.session_state.chat_history  # list[dict] — {"query", "response", "timestamp"}
st.session_state.total_queries # int — counter
st.session_state.process_query # bool — flag to trigger query processing
st.session_state.current_query # str — the query to process
```

### `render_sidebar()`
1. Shows agent team descriptions (Web Agent, Finance Agent, Team Coordinator) in styled cards.
2. Session stats: `st.metric("Queries", total_queries)` and `st.metric("History", len(chat_history))`.
3. "Clear History" button → resets both, logs, `st.rerun()`.

### `_get_popular_stocks(limit=8)`
1. Calls `nepse_data.get_all_stocks()`.
2. Sorts by `amount` (turnover) descending.
3. Returns `[{"symbol", "company", "change"}, ...]` for the top 8.

### `render_live_market_cards()`
1. Calls `nepse_data.get_market_snapshot()`.
2. Renders 5 columns of `st.metric()`: Avg Change, Turnover, Shares, Top Gainer, Top Loser.
3. Caption shows trade date, decliners, unchanged, total stocks.

### `render_quick_actions()`
**Renders 3 groups of buttons:**

1. **Popular Stocks** (dynamic, top 8 by turnover):
   - 2 rows × 4 buttons.
   - Each button: `SYMBOL ▲ (+X.XX%)` with company tooltip.
   - Fallback: hardcoded NABIL, EBL, NRIC, ADBL, SHIVM, CHCL, NMB, CIT.

2. **Market Scans** (4 buttons):
   - Top Gainers, Top Losers, Most Traded, Market Overview.

3. **Sector Analysis** (4 buttons):
   - Banking, Hydropower, Insurance, Microfinance.

Each button calls `_trigger_query(query, label)`.

### `_trigger_query(query, label)`
```python
st.session_state.current_query = query
st.session_state.process_query = True
```

### `render_query_input()`
- Text input with placeholder.
- "🚀 Analyze" button → sets `current_query` + `process_query = True`.

### `process_query()`
**The main query execution pipeline:**

1. Check `process_query` flag and `current_query`.
2. Increment `total_queries`, reset `process_query = False`.
3. Show spinner: `"🤖 Agent team is analyzing your query..."`.
4. Call `initialize_agents()`.
5. Timestamp the query.
6. Render query in a `.query-box` div.
7. Call `process_agent_query(agent_team, query)`.
8. Render response in a `.agent-response` styled div.
9. Append to `st.session_state.chat_history`.
10. On error: show `st.error()`, tool-specific warning, and troubleshooting tips.

### `render_chat_history()`
- Iterates `st.session_state.chat_history` in reverse.
- Each entry is an `st.expander` with the query preview and timestamp.
- Inside: full query, timestamp, and response in `.agent-response` div.

### `render_market_trends()`
- 2 columns: `get_market_trend()` (breadth) and `get_sector_trends()` (sectors).
- Both displayed in `st.code()` blocks.

### `render_all_stocks()`
1. Calls `get_all_stocks_table()`.
2. Shows total count.
3. **Filters:** text search, sort by column, ascending/descending.
4. **Color-coding:** positive → green, negative → red, zero → gray (via pandas `Styler.map`).
5. Renders `st.dataframe()`.

### `main()` — The Orchestrator
```python
def main():
    render_sidebar()
    st.title("🏦 NEPSE AI Finance Agent")
    render_quick_actions()    # includes live market cards
    render_query_input()
    process_query()
    render_chat_history()
    render_market_trends()
    render_all_stocks()
```

---

## 4️⃣ Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│  app.py (Streamlit UI)                                                  │
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐   │
│  │ Live Market      │    │ Quick Actions    │    │ Custom Query     │   │
│  │ Snapshot Cards   │    │ (Popular Stocks, │    │ Text Input +     │   │
│  │ (5 metrics)      │    │  Market Scans,   │    │ Analyze Button   │   │
│  │                  │    │  Sector Analysis)│    │                  │   │
│  └───────┬──────────┘    └────────┬─────────┘    └────────┬─────────┘   │
│          │                       │                       │             │
│          ▼                       ▼                       ▼             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    process_query()                                │   │
│  │  1. Set flag, increment counter                                  │   │
│  │  2. Show spinner                                                 │   │
│  │  3. Call initialize_agents()  ─────────────────────────────┐     │   │
│  │  4. Call process_agent_query()                              │     │   │
│  │  5. Render response                                         │     │   │
│  │  6. Save to chat_history                                    │     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                          │                             │
│  ┌──────────────────────────────┐        │                             │
│  │ Market Trends + All Stocks   │        │                             │
│  │ (rendered below query area)  │        │                             │
│  └──────┬───────────────────────┘        │                             │
│         │                                │                             │
└─────────┼────────────────────────────────┼─────────────────────────────┘
          │                                │
          ▼                                ▼
┌─────────────────────┐    ┌─────────────────────────────────────────────┐
│  nepse_data.py      │    │  main.py (Agent System)                     │
│                     │    │                                             │
│  get_market_        │    │  initialize_agents()                        │
│  snapshot()         │    │   ├── Web Agent (SerpAPI)                   │
│  get_all_stocks_    │    │   ├── Finance Agent (12 NEPSE tools)        │
│  table()            │    │   └── Team Coordinator                      │
│  get_market_trend() │    │                                             │
│  get_sector_trends()│    │  process_agent_query()                      │
│                     │    │   ├── agent_team.run(query)                 │
│  (all call          │    │   ├── Parse response.content                │
│   _fetch_live_      │    │   └── Error → simplified retry              │
│   data())           │    │                                             │
└─────────────────────┘    └─────────────────────────────────────────────┘
```

---

## 5️⃣ Key Code Patterns

### Pattern 1: TTL Cache with Stale Fallback
```python
_cache = {"timestamp": 0.0, "data": None}

def _fetch_live_data(force_refresh=False):
    now = time.time()
    if (not force_refresh and _cache["data"] is not None
        and (now - _cache["timestamp"]) < CACHE_TTL_SECONDS):
        return _cache["data"]
    try:
        # fetch new data...
        _cache["data"] = data
        _cache["timestamp"] = now
        return data
    except Exception:
        if _cache["data"] is not None:
            return _cache["data"]  # stale fallback
        raise
```

### Pattern 2: Streamlit Session State (One-Time Init)
```python
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
```
This pattern ensures state is initialized only once, since Streamlit reruns the script on every interaction.

### Pattern 3: Trigger-Process Pattern (Avoids Rerun Issues)
```python
# Trigger (button click)
def _trigger_query(query, label):
    st.session_state.current_query = query
    st.session_state.process_query = True

# Process (called in main())
def process_query():
    if st.session_state.process_query and st.session_state.current_query:
        query = st.session_state.current_query
        st.session_state.process_query = False  # reset immediately
        # ... process ...
```
This decouples the button click from the processing, ensuring the query is processed exactly once despite Streamlit's rerun behavior.

### Pattern 4: Agent Tool Registry
```python
NEPSE_TOOLS = [
    nepse_data.get_market_overview,  # function reference, not call
    nepse_data.get_top_gainers,
    # ... 12 functions total
]
```
The Phi framework introspects these function signatures and makes them available to the LLM as callable tools.

### Pattern 5: Error Retry with Simplified Query
```python
try:
    response = agent_team.run(query)
except Exception as e:
    if "tool_use_failed" in str(e):
        simplified_query = f"Provide information about {query.split('for')[-1] if 'for' in query else query}"
        response = agent_team.run(simplified_query)
    else:
        raise
```

---

## 6️⃣ Execution Order (When `streamlit run app.py`)

| Step | What Happens | File |
|------|-------------|------|
| 1 | Python starts, imports modules | `app.py` top-level |
| 2 | `main.py` configures logging, loads `.env`, defines `NEPSE_TOOLS` | `main.py` top-level |
| 3 | `st.set_page_config()` — page title, icon, layout | `app.py` |
| 4 | Custom CSS injected via `st.markdown()` | `app.py` |
| 5 | Session state initialized (if first run) | `app.py` |
| 6 | `main()` called → `render_sidebar()` | `app.py` |
| 7 | `render_quick_actions()` → `render_live_market_cards()` | `app.py` |
| 8 | `_get_popular_stocks()` → `nepse_data.get_all_stocks()` → `_fetch_live_data()` | `app.py` → `nepse_data.py` |
| 9 | API call to NepalIPaisa (first fetch, cache miss) | `nepse_data.py` |
| 10 | Data cached for 60s | `nepse_data.py` |
| 11 | Quick action buttons rendered | `app.py` |
| 12 | Query input rendered | `app.py` |
| 13 | `process_query()` — checks flag (no-op on first load) | `app.py` |
| 14 | `render_chat_history()` — empty on first load | `app.py` |
| 15 | `render_market_trends()` → `get_market_trend()` + `get_sector_trends()` | `app.py` → `nepse_data.py` |
| 16 | `render_all_stocks()` → `get_all_stocks_table()` → cached data used | `app.py` → `nepse_data.py` |
| 17 | User clicks a button → `_trigger_query()` → `process_query=True` | `app.py` |
| 18 | Streamlit reruns → `process_query()` fires → agents initialized | `app.py` → `main.py` |
| 19 | Query sent to Team Coordinator → delegates to sub-agents | `main.py` |
| 20 | Finance Agent calls NEPSE tools → `_fetch_live_data()` (cache hit) | `nepse_data.py` |
| 21 | Web Agent calls SerpAPI → news search | `main.py` |
| 22 | LLaMA 3.3 70B synthesizes response | `main.py` |
| 23 | Response rendered in UI, saved to chat history | `app.py` |
| 24 | User can continue with more queries (cached data serves until 60s expires) | All |

---

## 7️⃣ Error Handling Map

| Failure Point | Error Type | How It's Handled | User Sees |
|--------------|------------|------------------|-----------|
| API fetch fails | `urllib.error` | Stale cache fallback or `RuntimeError` | Normal data from cache, or "⏳ Market data is loading..." |
| Missing GROQ key | `Exception` | Raised from `initialize_agents()` | "❌ Failed to initialize agent team" |
| SerpAPI fails | `Exception` with "tool_use_failed" | Simplified query retry | Warning about tool failure, then retry |
| Any query error | `Exception` | Caught in `process_query()` | Error message + troubleshooting tips |
| Invalid stock symbol | Not found | `get_stock_info()` returns "Stock symbol 'X' not found" | Agent responds with "not found" |
| No stocks in sector | Empty list | `get_sector_stocks()` returns "No NEPSE stocks matched" | Agent responds with "no matches" |

---

## 8️⃣ Quick Reference: Key Function Signatures

### `nepse_data.py`
```python
get_market_summary()                    → dict
get_all_stocks()                        → list[dict]
get_market_overview(limit=5)            → str
get_top_gainers(limit=10)               → str
get_top_losers(limit=10)                → str
get_top_volume(limit=10)                → str
get_top_traded(limit=10)                → str
get_stock_info(symbol: str)             → str
search_stock(query: str)                → str
get_company_list()                      → str
get_sector_stocks(keyword: str)         → str
get_all_stocks_table()                  → list[dict]
get_market_snapshot()                   → dict | None
get_market_trend()                      → str
get_sector_trends()                     → str
```

### `main.py`
```python
initialize_agents()                     → Agent (team coordinator)
process_agent_query(agent_team, query)  → str
```

### `app.py`
```python
render_sidebar()                        → None (renders Streamlit)
render_live_market_cards()              → None
render_quick_actions()                  → None
render_query_input()                    → None
process_query()                         → None
render_chat_history()                   → None
render_market_trends()                  → None
render_all_stocks()                     → None
main()                                  → None

# 🏦 NEPSE Multi-Agent AI System

A professional Streamlit-based application showcasing a multi-agent AI system that analyzes the **Nepali Stock Market (NEPSE)** with a Web Agent and a Finance Agent working together. It is powered by the Phi Agent Framework, Groq LLM (LLaMA 3.3 70B), and SerpAPI web search, and pulls **LIVE NEPSE market data** from the NepalIPaisa public API.

## 🌟 Features

- **Multi-Agent Collaboration**: Web Agent + Finance Agent + Team Coordinator
- **LIVE NEPSE Data**: Real-time prices, top gainers, top losers, high volume & high turnover stocks
- **Live Market Snapshot**: Dashboard cards showing average market change, total turnover, shares traded, top gainer & top loser
- **Popular Stocks**: Dynamically updated quick-access buttons for the most actively traded stocks (by turnover)
- **Market Scans & Sector Analysis**: One-click buttons for Top Gainers, Top Losers, Most Traded, Market Overview, Banking, Hydropower, Insurance, and Microfinance
- **All NEPSE Stocks Table**: Browse, search, and sort all 300+ listed stocks with live prices
- **Market Trend Analysis**: Market breadth, advancing/declining stocks, sentiment, and sector performance
- **Sector Performance**: Banking, Development Banks, Finance, Insurance, Microfinance, Hydropower, Hotel & Tourism, Manufacturing, Trading, Investment, and Mutual Funds
- **Real-time Analysis**: Get instant market insights and comprehensive information
- **Interactive UI**: Modern, responsive design with quick-access buttons
- **Chat History**: Track all your queries and responses
- **Professional Dashboard**: Polished application with clean UX/UI
- **Error Handling**: Robust logging, error recovery, and TTL-cached data

## 📁 Project Structure

```
FinSight-AI-Financial-Agent/
├── app.py                 # Streamlit UI and interface logic
├── main.py                # Agent initialization and business logic
├── nepse_data.py          # LIVE NEPSE data module (stdlib only, TTL cache)
├── requirements.txt       # Python dependencies
├── readme.md              # This file
├── .gitignore             # Git ignore rules (.env, __pycache__, etc.)


## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API Key (Get one free at [console.groq.com](https://console.groq.com/))
- SerpAPI Key (Get one free at [serpapi.com](https://serpapi.com/)) — used by the Web Agent for market news search

### Installation

1. **Clone or download this repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the project root (it is gitignored) with the following keys:
```bash
# .env
GROQ_API_KEY=your_groq_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here
```

> ⚠️ The app needs a **GROQ_API_KEY** to run the agents. The **SERPAPI_API_KEY** powers the Web Agent's web search — without it, news/news queries will degrade (the team coordinator falls back to the Finance Agent's live data and general knowledge).

4. **Test the NEPSE data module (optional)**
```bash
python nepse_data.py
```
5. **Run the application**
The app run on port **8501** , so just run:
```bash
streamlit run app.py
```
(Or override the port explicitly with `streamlit run app.py --server.port 8080`.)

6. **Open your browser**
The app will automatically open at `http://localhost:8501`

## 📖 How to Use

### Live Market Snapshot
At the top of the app, five live cards show the current market state:
- **Avg Market Change** (with advancer count)
- **Total Turnover**
- **Shares Traded**
- **Top Gainer**
- **Top Loser**

### Quick Analysis
Click any quick-access button for instant analysis:

- **Popular Stocks** (top 8 most-traded stocks, dynamically fetched from live data — updates automatically)
- **Market Scans**: Top Gainers, Top Losers, Most Traded, Market Overview
- **Sector Analysis**: Banking, Hydropower, Insurance, Microfinance

If live data is unavailable, the app falls back to a default set of well-known stocks (NABIL, EBL, NRIC, ADBL, SHIVM, CHCL, NMB, CIT).

### Custom Query
Type your own query in the search box for customized analysis.
Example: "Analyze NABIL stock" or "Show today's top gainers in NEPSE"

### View History
Review past queries in the expandable chat history section (also shows session stats in the sidebar).

### All NEPSE Stocks & Trends
Scroll below the query area to explore:
- **📊 All NEPSE Stocks**: A live, searchable, sortable table of every listed stock (search by symbol or company name, sort by change %, LTP, volume, or turnover).
- **📈 NEPSE Market Trend Analysis**: Market breadth (advancers/decliners), sentiment, and sector-wise performance breakdown.

## 🛠️ File Descriptions

### `nepse_data.py` — Live NEPSE Data Module
Fetches real NEPSE data from the NepalIPaisa public API (`https://nepalipaisa.com/api/GetStockLive`) using only the Python standard library (`urllib`). Features:
- In-memory caching with a 60-second TTL (stale data fallback on API failure)
- Market overview, top gainers/losers, top volume, top turnover
- Single stock lookup, company search, sector keyword analysis
- Structured market snapshot and market trend/sentiment computation
- All amounts in Nepalese Rupees (NPR)

**Functions:**
| Function | Description |
|----------|-------------|
| `get_market_summary()` | Market summary dict (totalAmount, totalShares, totalTxns) |
| `get_all_stocks()` | Full list of live NEPSE stock quotes |
| `get_market_overview(limit)` | Text summary: overview + top gainers/losers/volume/turnover |
| `get_top_gainers(limit)` | Top gainers by % change |
| `get_top_losers(limit)` | Top losers by % change |
| `get_top_volume(limit)` | Highest volume stocks |
| `get_top_traded(limit)` | Highest turnover stocks |
| `get_stock_info(symbol)` | Live quote for a specific symbol (e.g. NABIL) |
| `search_stock(query)` | Search by symbol or company name keyword |
| `get_company_list()` | All NEPSE company symbols |
| `get_sector_stocks(keyword)` | Sector analysis (bank, hydropower, insurance, etc.) |
| `get_all_stocks_table()` | Full table of all NEPSE stocks for dataframes |
| `get_market_snapshot()` | Structured dict for dashboard snapshot cards |
| `get_market_trend()` | Market breadth + sentiment analysis |
| `get_sector_trends()` | Sector-wise average performance |
| `test_nepse_data()` | Command-line smoke test (run via `python nepse_data.py`) |

### `main.py` — Agent Business Logic
Contains all agent-related functionality:
- `NEPSE_TOOLS`: List of 12 NEPSE data functions registered as callable tools for the Finance Agent
- `initialize_agents()`: Creates the Web Agent (with `SerpApiTools`), Finance Agent (with NEPSE tools), and Team Coordinator — all powered by Groq (`llama-3.3-70b-versatile`)
- `process_agent_query(agent_team, query)`: Handles query processing with tool-error retry/simplification logic
- Loads `.env` variables via `python-dotenv`

### `app.py` — Streamlit UI
Contains all Streamlit UI components:
- `render_sidebar()`: Sidebar with agent info and session stats (queries + history count)
- `_trigger_query()`: Sets the current query and processing flag for quick actions
- `_get_popular_stocks()`: Fetches top N most-traded stocks by turnover for quick buttons
- `render_live_market_cards()`: Live NEPSE market snapshot metric cards
- `render_quick_actions()`: Popular stocks, market scans, and sector analysis buttons
- `render_market_trends()`: Market breadth + sector performance display
- `render_all_stocks()`: Searchable/sortable dataframe of all NEPSE stocks
- `render_query_input()`: Custom query input section
- `process_query()`: Query processing workflow (spinner, error handling, troubleshooting tips)
- `render_chat_history()`: Expandable chat history display
- `main()`: Main application layout orchestration

## 🎯 Agent Architecture

### Web Agent 🌐
- Searches the web for Nepali market news & NEPSE developments (powered by SerpAPI)
- Provides company fundamentals, announcements, and sources/URLs

### Finance Agent 💰
- Calls **LIVE NEPSE tools** to fetch real market data
- Analyzes stock prices, gainers/losers, volume, turnover, and sectors
- Creates formatted tables with Rs (NPR) amounts
- Falls back to general knowledge if live data tools fail

### Team Coordinator 🤝
- Orchestrates agent collaboration
- Handles agent failures gracefully
- Provides comprehensive answers with actionable insights
- Prefers Finance Agent's live data for numbers and Web Agent for news/fundamentals

## 📊 NEPSE Tools Exposed to the Finance Agent

The following 12 functions from `nepse_data.py` are registered in `NEPSE_TOOLS` and available to the Finance Agent as callable tools:

| Tool | Description |
|------|-------------|
| `get_market_overview()` | Overall NEPSE market snapshot |
| `get_top_gainers(n)` | Top gainers by % change |
| `get_top_losers(n)` | Top losers by % change |
| `get_top_volume(n)` | Highest volume stocks |
| `get_top_traded(n)` | Highest turnover stocks |
| `get_stock_info(symbol)` | Live quote for a specific symbol (e.g. NABIL) |
| `search_stock(query)` | Search by symbol or company name |
| `get_company_list()` | All NEPSE company symbols |
| `get_sector_stocks(keyword)` | Sector analysis (bank, hydropower, insurance, etc.) |
| `get_all_stocks_table()` | Full table of all NEPSE stocks for dataframes |
| `get_market_trend()` | Market breadth + sentiment analysis |
| `get_sector_trends()` | Sector-wise average performance |

> Note: `get_market_summary()`, `get_all_stocks()`, and `get_market_snapshot()` exist in `nepse_data.py` but are used by the **UI layer** (sidebar cards, popular stocks) rather than exposed as agent tools.

## 📊 Example Queries

Try these queries to explore the system's capabilities:

- "Provide detailed analysis and recent information about NABIL stock"
- "Show today's top gainers and top losers in NEPSE"
- "Analyze the banking sector using live NEPSE data"
- "What is the current NEPSE market overview?"
- "Compare ADBL and NABIL performance using live data"
- "What are the latest important NEPSE news and developments?"

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **LLM**: Groq (LLaMA 3.3 70B Versatile)
- **Web Search**: SerpAPI (`SerpApiTools`)
- **Market Data**: NepalIPaisa NEPSE API (live, 60s TTL cache)
- **Language**: Python 3.8+
- **Logging**: Python logging module
- **Env Management**: python-dotenv

## 🎓 Highlights

This project demonstrates:

✅ **Modular code architecture** (separate UI, business logic, and data layers)  
✅ **Multi-agent AI system design**  
✅ **Live financial data integration** (NEPSE via public API)  
✅ **Professional error handling and logging** (stale-cache fallback, retry logic)  
✅ **State management in Streamlit**  
✅ **API integration best practices**  
✅ **Clean code principles**  
✅ **Professional UI/UX design**  


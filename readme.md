# 🏦 NEPSE Multi-Agent AI System

A professional Streamlit-based application showcasing a multi-agent AI system that analyzes the **Nepali Stock Market (NEPSE)** with a Web Agent and a Finance Agent working together. It is powered by the Phi Agent Framework and Groq LLM, and pulls **LIVE NEPSE market data** from the NepalIPaisa public API.

## 🌟 Features

- **Multi-Agent Collaboration**: Web Agent + Finance Agent + Team Coordinator
- **LIVE NEPSE Data**: Real-time prices, top gainers, top losers, high volume & high turnover stocks
- **All NEPSE Stocks Table**: Browse, search, and sort all 337+ listed stocks with live prices
- **Market Trend Analysis**: Market breadth, advancing/declining stocks, sentiment, and sector performance
- **Sector Analysis**: Banking, Hydropower, Insurance, Microfinance, and more
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
├── .env.example          # Environment variable template
├── .env                  # Your API keys (gitignored)
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API Key (Get one free at [console.groq.com](https://console.groq.com/))

### Installation

1. **Clone or download this repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_actual_api_key_here
```

4. **Test the NEPSE data module (optional)**
```bash
python nepse_data.py
```
5. **Run the application**
```bash
streamlit run app.py --server.port 8080
```

6. **Open your browser**
The app will automatically open at `http://localhost:8080`

## 📖 How to Use

### Quick Analysis
Click any of the quick-access buttons for instant analysis:
- **NABIL Analysis**: Nabil Bank stock information
- **NRIC Insights**: Nepal Reinsurance stock insights
- **ADBL Report**: Agricultural Development Bank stock report
- **Analysis Types**: Banking Sector, Market Overview, Hydropower, Top Movers

### Custom Query
Type your own query in the search box for customized analysis.
Example: "Analyze NABIL stock" or "Show today's top gainers in NEPSE"

### View History
Review past queries in the expandable chat history section.

### All NEPSE Stocks & Trends
Scroll below the query area to explore:
- **📊 All NEPSE Stocks**: A live, searchable, sortable table of every listed stock (search by symbol or company name, sort by change %, LTP, volume, or turnover).
- **📈 NEPSE Market Trend Analysis**: Market breadth (advancers/decliners), sentiment, and sector-wise performance breakdown.

## 🛠️ File Descriptions

### `nepse_data.py` - Live NEPSE Data Module
Fetches real NEPSE data from the NepalIPaisa public API (`https://nepalipaisa.com/api/GetStockLive`) using only the Python standard library. Features:
- In-memory caching with a 60-second TTL
- Market overview, top gainers/losers, top volume, top turnover
- Single stock lookup, company search, sector keyword analysis
- All amounts in Nepalese Rupees (NPR)

### `main.py` - Business Logic
Contains all agent-related functionality:
- `initialize_agents()`: Creates Web Agent, Finance Agent (with NEPSE tools), and Team Coordinator
- `process_agent_query()`: Handles query processing with error recovery
- Registers NEPSE data functions as callable tools for the Finance Agent

### `app.py` - User Interface
Contains all Streamlit UI components:
- `render_sidebar()`: Sidebar with agent info and stats
- `render_quick_actions()`: NEPSE quick analysis buttons
- `render_query_input()`: Custom query input section
- `process_query()`: Query processing workflow
- `render_chat_history()`: Chat history display

## 🎯 Agent Architecture

### Web Agent 🌐
- Searches the web for Nepali market news & NEPSE developments
- Provides company fundamentals, announcements, and sources/URLs

### Finance Agent 💰
- Calls **LIVE NEPSE tools** to fetch real market data
- Analyzes stock prices, gainers/losers, volume, turnover, and sectors
- Creates formatted tables with Rs (NPR) amounts

### Team Coordinator 🤝
- Orchestrates agent collaboration
- Handles agent failures gracefully
- Provides comprehensive answers with actionable insights

## 📊 NEPSE Tools Available

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
- **AI Framework**: Phi Agent Framework
- **LLM**: Groq (LLaMA 3.3 70B)
- **Market Data**: NepalIPaisa NEPSE API (live)
- **Language**: Python 3.8+
- **Logging**: Python logging module

## 🎓 Highlights

This project demonstrates:

✅ **Modular code architecture** (separate UI, business logic, and data layers)  
✅ **Multi-agent AI system design**  
✅ **Live financial data integration** (NEPSE via public API)  
✅ **Professional error handling and logging**  
✅ **State management in Streamlit**  
✅ **API integration best practices**  
✅ **Clean code principles**  
✅ **Professional UI/UX design**



# NEPSE-AI-Finance-Agent

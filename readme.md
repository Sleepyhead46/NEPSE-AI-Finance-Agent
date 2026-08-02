# 🏦 NEPSE Multi-Agent AI System

A Streamlit application that analyzes the **Nepali Stock Market (NEPSE)** using a multi-agent AI system — a Web Agent and a Finance Agent working together. Powered by the Phi Agent Framework, Groq LLM (LLaMA 3.3 70B), and SerpAPI, with **LIVE NEPSE market data** from the NepalIPaisa public API.

## ✨ Features

- **Multi-Agent Collaboration**: Web Agent + Finance Agent + Team Coordinator
- **LIVE NEPSE Data**: Real-time prices, top gainers/losers, volume & turnover
- **Live Market Snapshot**: Dashboard cards with avg change, turnover, top gainer/loser
- **Quick Actions**: One-click analysis for popular stocks, market scans, and sectors
- **All NEPSE Stocks Table**: Browse, search, and sort all 300+ listed stocks
- **Market Trends & Sector Performance**: Breadth, sentiment, and sector breakdowns
- **Chat History & Error Handling**: Query history, robust logging, and TTL-cached data

## 📁 Project Structure

```
FinSight-AI-Financial-Agent/
├── app.py                 # Streamlit UI and interface logic
├── main.py                # Agent initialization and business logic
├── nepse_data.py          # LIVE NEPSE data module (stdlib only, TTL cache)
├── requirements.txt       # Python dependencies
├── readme.md              # This file
├── .gitignore             # Git ignore rules (.env, __pycache__, etc.)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API Key ([console.groq.com](https://console.groq.com/))
- SerpAPI Key ([serpapi.com](https://serpapi.com/)) — used by the Web Agent for market news

### Installation

1. Clone or download this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file in the project root:

```bash
# .env
GROQ_API_KEY=your_groq_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here
```

> ⚠️ The app needs a **GROQ_API_KEY** to run. The **SERPAPI_API_KEY** powers web search — without it, news queries will degrade to the Finance Agent's live data and general knowledge.

4. (Optional) Test the NEPSE data module: `python nepse_data.py`
5. Run the app: `streamlit run app.py`
6. Open http://localhost:8501 (the app auto-opens)

## 📖 How to Use

- **Live Market Snapshot**: Five cards at the top show avg market change, total turnover, shares traded, top gainer, and top loser.
- **Quick Analysis**: Click any button for instant AI analysis — popular stocks, market scans (Top Gainers, Top Losers, Most Traded, Market Overview), and sector analysis (Banking, Hydropower, Insurance, Microfinance).
- **Custom Query**: Type your own query, e.g. "Analyze NABIL stock" or "Show today's top gainers in NEPSE".
- **History & Trends**: Review past queries in the chat history; scroll down for the searchable **All NEPSE Stocks** table and **Market Trend Analysis**.

## 🛠️ Architecture

- **Web Agent 🌐**: Searches the web for Nepali market news and developments (SerpAPI)
- **Finance Agent 💰**: Calls LIVE NEPSE tools for real market data and analysis
- **Team Coordinator 🤝**: Orchestrates both agents, preferring live data for numbers and web results for news/fundamentals

`main.py` exposes 12 NEPSE data functions (market overview, gainers/losers, volume/turnover, stock info, search, sectors, trends) as tools for the Finance Agent. `nepse_data.py` fetches from the NepalIPaisa API (`https://nepalipaisa.com/api/GetStockLive`) with a 60-second TTL cache and stale-data fallback.

## 💬 Example Queries

- "Provide detailed analysis and recent information about NABIL stock"
- "Show today's top gainers and top losers in NEPSE"
- "Analyze the banking sector using live NEPSE data"
- "Compare ADBL and NABIL performance using live data"
- "What are the latest important NEPSE news and developments?"

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **LLM**: Groq (LLaMA 3.3 70B Versatile)
- **Web Search**: SerpAPI (`SerpApiTools`)
- **Market Data**: NepalIPaisa NEPSE API (live, 60s TTL cache)
- **Language**: Python 3.8+
- **Env Management**: python-dotenv


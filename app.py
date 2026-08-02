import streamlit as st
from datetime import datetime
import logging
import nepse_data
from main import initialize_agents, process_agent_query

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="NEPSE Multi-Agent AI System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    
    .agent-response {
        background-color: rgba(28, 131, 225, 0.1);
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid #4CAF50;
        color: inherit;
    }
    
    .agent-response h1, .agent-response h2, .agent-response h3,
    .agent-response h4, .agent-response h5, .agent-response h6,
    .agent-response p, .agent-response li, .agent-response td, 
    .agent-response th, .agent-response span {
        color: inherit !important;
    }
    
    .agent-response table {
        color: inherit !important;
        border-collapse: collapse;
        width: 100%;
        margin: 10px 0;
    }
    
    .agent-response table th {
        background-color: rgba(28, 131, 225, 0.2);
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .agent-response table td {
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .query-box {
        background-color: rgba(28, 131, 225, 0.05);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 3px solid #1f77b4;
    }
    
    .agent-card {
        background-color: rgba(76, 175, 80, 0.1);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 3px solid #4CAF50;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0
if 'process_query' not in st.session_state:
    st.session_state.process_query = False
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""

def render_sidebar():
    """Render sidebar content"""
    with st.sidebar:
        st.markdown("## 🏦 NEPSE Multi-Agent AI")
        st.markdown("---")
        
        st.markdown("""
        ### 🎯 Agent Team
        This system analyzes the **Nepali Stock Market (NEPSE)** using multiple specialized AI agents:
        """)
        
        st.markdown("""
        <div class='agent-card'>
            <strong>🌐 Web Agent</strong><br>
            <small>Searches the web for Nepali market news & NEPSE developments</small>
        </div>
        <div class='agent-card'>
            <strong>💰 Finance Agent</strong><br>
            <small>Fetches LIVE NEPSE data (prices, gainers, losers, sectors)</small>
        </div>
        <div class='agent-card'>
            <strong>🤝 Team Coordinator</strong><br>
            <small>Orchestrates agent collaboration</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 📊 Session Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Queries", st.session_state.total_queries)
        with col2:
            st.metric("History", len(st.session_state.chat_history))
        
        st.markdown("---")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.total_queries = 0
            logger.info("Chat history cleared")
            st.rerun()

def _trigger_query(query, label):
    """Set the current query and process flag."""
    st.session_state.current_query = query
    st.session_state.process_query = True
    logger.info(f"Quick query triggered: {label}")

def _get_popular_stocks(limit=8):
    """Fetch the most actively traded NEPSE stocks from live data (by turnover)."""
    try:
        stocks = nepse_data.get_all_stocks()
        if not stocks:
            logger.warning("No live NEPSE stocks available for popular list")
            return []
        # Sort by turnover (amount) descending to get the most popular/traded stocks
        popular = sorted(
            stocks,
            key=lambda s: float(s.get("amount") or 0),
            reverse=True
        )[:limit]
        return [
            {
                "symbol": s.get("stockSymbol", ""),
                "company": s.get("companyName", ""),
                "change": float(s.get("percentChange") or 0),
            }
            for s in popular
            if s.get("stockSymbol")
        ]
    except Exception as e:
        logger.error(f"Error fetching popular stocks: {str(e)}", exc_info=True)
        return []

def render_live_market_cards():
    """Render live NEPSE market snapshot cards at the top."""
    st.markdown("### 📌 Live NEPSE Market Snapshot")
    try:
        snap = nepse_data.get_market_snapshot()
        if not snap:
            st.info("⏳ Market data is loading...")
            return
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        avg = snap.get("avg_change", 0)
        arrow = "▲" if avg >= 0 else "▼"
        color = "normal" if avg >= 0 else "inverse"
        with col1:
            st.metric(
                "Avg Market Change",
                f"{arrow} {avg:+.2f}%",
                delta=f"{snap.get('advancers', 0)} advancers",
                delta_color=color,
            )
        with col2:
            st.metric("Total Turnover", f"Rs {snap.get('total_amount', 0):,.0f}")
        with col3:
            st.metric("Shares Traded", f"{snap.get('total_shares', 0):,.0f}")
        with col4:
            st.metric("Top Gainer", f"{snap.get('top_gainer', 'N/A')} {snap.get('top_gainer_change', 0):+.2f}%")
        with col5:
            st.metric("Top Loser", f"{snap.get('top_loser', 'N/A')} {snap.get('top_loser_change', 0):+.2f}%")
        
        st.caption(f"Trade Date: {snap.get('trade_date', 'N/A')} | {snap.get('decliners', 0)} decliners | {snap.get('unchanged', 0)} unchanged | {snap.get('total_stocks', 0)} stocks tracked")
    except Exception as e:
        logger.error(f"Error loading market snapshot: {str(e)}", exc_info=True)
        st.info("⏳ Market data is loading...")

def render_quick_actions():
    """Render quick action buttons for better market representation."""
    render_live_market_cards()
    
    st.markdown("---")
    st.markdown("### 🔥 Quick Analysis")
    st.caption("Click any button to run an instant AI analysis using live NEPSE data")
    
    # Row 1: Popular stocks (dynamically updated based on live NEPSE data)
    st.markdown("**🏢 Popular Stocks**")
    st.caption("Top actively traded stocks based on live NEPSE data")
    popular_stocks = _get_popular_stocks(limit=8)
    
    if popular_stocks:
        # Group into rows of 4
        for row_start in range(0, len(popular_stocks), 4):
            cols = st.columns(4)
            for i, col in enumerate(cols):
                idx = row_start + i
                if idx < len(popular_stocks):
                    stock = popular_stocks[idx]
                    symbol = stock["symbol"]
                    change = stock["change"]
                    arrow = "▲" if change >= 0 else "▼"
                    label = f"{symbol} {arrow} ({change:+.2f}%)"
                    with col:
                        if st.button(
                            label,
                            use_container_width=True,
                            key=f"popular_{symbol}",
                            help=f"{stock['company']}",
                        ):
                            _trigger_query(
                                f"Provide detailed analysis and recent information about {symbol} stock (Nepal Stock Exchange)",
                                symbol,
                            )
    else:
        st.info("⚠️ Live data unavailable. Showing default popular stocks.")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🏦 NABIL (Bank)", use_container_width=True):
                _trigger_query("Provide detailed analysis and recent information about NABIL stock (Nepal Stock Exchange)", "NABIL")
        with col2:
            if st.button("🏦 EBL (Bank)", use_container_width=True):
                _trigger_query("Provide detailed analysis and recent information about EBL stock (Everest Bank Limited)", "EBL")
        with col3:
            if st.button("🛡️ NRIC (Insurance)", use_container_width=True):
                _trigger_query("Provide detailed analysis and recent information about NRIC stock (Nepal Reinsurance)", "NRIC")
        with col4:
            if st.button("🌾 ADBL (Bank)", use_container_width=True):
                _trigger_query("Provide detailed analysis and recent information about ADBL stock (Agricultural Development Bank)", "ADBL")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("⚡ SHIVM (Hydropower)", use_container_width=True):
                _trigger_query("Provide detailed analysis and recent information about SHIVM stock (Shivam Cement Hydropower)", "SHIVM")
        with col2:
            if st.button("⚡ CHCL (Hydropower)", use_container_width=True):
                _trigger_query("Provide detailed analysis and recent information about CHCL stock (Chilime Hydropower)", "CHCL")
        with col3:
            if st.button("💳 NMB (Bank)", use_container_width=True):
                _trigger_query("Provide detailed analysis and recent information about NMB stock (NMB Bank)", "NMB")
        with col4:
            if st.button("💹 CIT (Investment)", use_container_width=True):
                _trigger_query("Provide detailed analysis and recent information about CIT stock (Citizen Investment Trust)", "CIT")
    
    st.markdown("---")
    
    # Row 2: Market scans
    st.markdown("**🔎 Market Scans**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🚀 Top Gainers", use_container_width=True):
            _trigger_query("What are today's top gainers in NEPSE? Use live data and show a table.", "Top Gainers")
    with col2:
        if st.button("📉 Top Losers", use_container_width=True):
            _trigger_query("What are today's top losers in NEPSE? Use live data and show a table.", "Top Losers")
    with col3:
        if st.button("📊 Most Traded", use_container_width=True):
            _trigger_query("Which NEPSE stocks have the highest volume and turnover today? Use live data.", "Most Traded")
    with col4:
        if st.button("💰 Market Overview", use_container_width=True):
            _trigger_query("Provide a complete overview of current NEPSE market conditions using live data.", "Market Overview")
    
    st.markdown("---")
    
    # Row 3: Sector analysis
    st.markdown("**🏭 Sector Analysis**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🏦 Banking", use_container_width=True):
            _trigger_query("Analyze the banking sector stocks in NEPSE using live data and show key metrics.", "Banking")
    with col2:
        if st.button("⚡ Hydropower", use_container_width=True):
            _trigger_query("Analyze the hydropower sector stocks in NEPSE using live data and show key metrics.", "Hydropower")
    with col3:
        if st.button("🛡️ Insurance", use_container_width=True):
            _trigger_query("Analyze the insurance sector stocks in NEPSE using live data and show key metrics.", "Insurance")
    with col4:
        if st.button("💳 Microfinance", use_container_width=True):
            _trigger_query("Analyze the microfinance sector stocks in NEPSE using live data and show key metrics.", "Microfinance")

def render_market_trends():
    """Render live NEPSE market trend and sector analysis."""
    st.markdown("---")
    st.markdown("## 📈 NEPSE Market Trend Analysis")
    
    try:
        trend = nepse_data.get_market_trend()
        sector = nepse_data.get_sector_trends()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🧭 Market Breadth")
            st.code(trend, language=None)
        with col2:
            st.markdown("### 🏭 Sector Performance")
            st.code(sector, language=None)
    except Exception as e:
        logger.error(f"Error loading market trends: {str(e)}", exc_info=True)
        st.warning("⚠️ Could not load live trend data. Try again shortly.")

def render_all_stocks():
    """Render a searchable/filterable table of ALL NEPSE stocks."""
    st.markdown("---")
    st.markdown("## 📊 All NEPSE Stocks")
    st.caption("Live data from NepalIPaisa NEPSE API (refreshes every 60s)")
    
    try:
        rows = nepse_data.get_all_stocks_table()
        if not rows:
            st.warning("⚠️ No live data available right now.")
            return
        
        st.markdown(f"### Total: {len(rows)} listed stocks")
        
        # Filters
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            search = st.text_input("🔍 Search by symbol or company:", key="stock_search")
        with col2:
            sort_by = st.selectbox(
                "Sort by:",
                ["Change (%)", "LTP (Rs)", "Volume", "Turnover (Rs)", "Symbol"],
                key="sort_by"
            )
        with col3:
            direction = st.selectbox("Order:", ["Descending", "Ascending"], key="sort_dir")
        
        # Apply search
        if search:
            s = search.strip().lower()
            rows = [r for r in rows if s in r["Symbol"].lower() or s in r["Company"].lower()]
        
        # Apply sort
        reverse = direction == "Descending"
        if sort_by == "Symbol":
            rows = sorted(rows, key=lambda r: r["Symbol"], reverse=reverse)
        else:
            rows = sorted(rows, key=lambda r: r[sort_by], reverse=reverse)
        
        # Color-code the change column
        def color_change(val):
            if val > 0:
                return f"color: green"
            elif val < 0:
                return f"color: red"
            return f"color: gray"
        
        try:
            import pandas as pd
            df = pd.DataFrame(rows)
            st.dataframe(
                df.style.map(color_change, subset=["Change (%)"]),
                use_container_width=True,
                height=500,
                hide_index=True,
            )
        except ImportError:
            st.dataframe(rows, use_container_width=True, height=500)
    except Exception as e:
        logger.error(f"Error loading all stocks: {str(e)}", exc_info=True)
        st.warning("⚠️ Could not load live stock data. Try again shortly.")

def render_query_input():
    """Render main query input section"""
    st.markdown("### 🔍 Custom Query")
    col_input, col_button = st.columns([4, 1])
    
    with col_input:
        user_query = st.text_input(
            "Enter your query:",
            value="",
            placeholder="e.g., Analyze NABIL stock or show today's top gainers in NEPSE",
            label_visibility="collapsed",
            key="user_input"
        )
    
    with col_button:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Analyze", use_container_width=True, type="primary"):
            if user_query:
                st.session_state.current_query = user_query
                st.session_state.process_query = True
                logger.info(f"Custom query submitted: {user_query}")

def process_query():
    """Process the current query"""
    if st.session_state.process_query and st.session_state.current_query:
        query_to_process = st.session_state.current_query
        st.session_state.total_queries += 1
        logger.info(f"Processing query #{st.session_state.total_queries}: {query_to_process}")
        
        # Reset flag
        st.session_state.process_query = False
        
        with st.spinner("🤖 Agent team is analyzing your query..."):
            try:
                # Initialize agents
                logger.info("Initializing agent team...")
                agent_team = initialize_agents()
                
                if agent_team:
                    # Display query
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    st.markdown(f'<div class="query-box"><strong>📝 Query:</strong> {query_to_process}<br><small>⏰ {timestamp}</small></div>', unsafe_allow_html=True)
                    
                    st.markdown("**🤖 Agent Response:**")
                    
                    # Get response with error handling
                    logger.info("Processing query through agent team...")
                    full_response = process_agent_query(agent_team, query_to_process)
                    logger.info(f"Response received: {len(full_response)} characters")
                    
                    # Display response
                    st.markdown(f'<div class="agent-response">', unsafe_allow_html=True)
                    st.markdown(full_response)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "query": query_to_process,
                        "response": full_response,
                        "timestamp": timestamp
                    })
                    logger.info("Query added to chat history")
                    
                    st.success("✅ Analysis complete!")
                    
                else:
                    logger.error("Agent team initialization failed")
                    st.error("❌ Failed to initialize agent team. Check logs for details.")
                    
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}", exc_info=True)
                st.error(f"❌ Error: {str(e)}")
                
                if "tool_use_failed" in str(e):
                    st.warning("⚠️ The web search tool encountered an issue. The agents will try to provide information from their knowledge base.")
                
                st.info("💡 **Troubleshooting Tips:**")
                st.markdown("""
                - Try rephrasing your query more simply
                - Check your GROQ_API_KEY in .env file
                - Verify internet connection
                - Try asking about a single topic instead of multiple topics
                """)

def render_chat_history():
    """Render chat history section"""
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("## 📜 Analysis History")
        
        for idx, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"💬 Query {len(st.session_state.chat_history) - idx}: {chat['query'][:60]}... ({chat['timestamp']})"):
                st.markdown(f"**📝 Query:** {chat['query']}")
                st.markdown(f"**⏰ Timestamp:** {chat['timestamp']}")
                st.markdown("**🤖 Response:**")
                st.markdown(f'<div class="agent-response">', unsafe_allow_html=True)
                st.markdown(chat["response"])
                st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    render_sidebar()
    
    st.title("🏦 NEPSE AI Finance Agent")
    st.markdown("Powered by Web Agent + Finance Agent (LIVE NEPSE data) working together")
    
    render_quick_actions()
    st.markdown("---")
    render_query_input()
    
    process_query()
    render_chat_history()
    
    render_market_trends()
    render_all_stocks()

if __name__ == "__main__":
    try:
        logger.info("Starting Multi-Agent AI System application")
        main()
    except Exception as e:
        logger.critical(f"Critical error in main application: {str(e)}", exc_info=True)
        st.error(f"❌ Critical Error: {str(e)}")

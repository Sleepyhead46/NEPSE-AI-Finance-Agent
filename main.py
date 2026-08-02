from phi.agent import Agent
from phi.tools.serpapi_tools import SerpApiTools
from phi.model.groq import Groq
from dotenv import load_dotenv
import os
import logging

# NEPSE (Nepal Stock Exchange) live data tools
import nepse_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# NEPSE tools exposed to the Finance Agent
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

def initialize_agents():
    """Initialize all AI agents with error handling"""
    try:
        logger.info("Initializing Web Agent...")
        web_agent = Agent(
            name="Web Agent",
            role="Search the web for information about the Nepali stock market (NEPSE)",
            model=Groq(id="llama-3.3-70b-versatile"),
            tools=[SerpApiTools()],
            instructions=[
                "Always include sources",
                "Provide latest information using search results",
                "Provide URLs when available",
                "Focus on Nepali market news, NEPSE developments, and Nepalese economy",
            ],
            show_tool_calls=True,
            markdown=True,
        )
        logger.info("Web Agent initialized successfully")
        
        logger.info("Initializing Finance Agent with NEPSE tools...")
        finance_agent = Agent(
            name="Finance Agent",
            role="Get live NEPSE financial data and provide analysis for the Nepali stock market",
            model=Groq(id="llama-3.3-70b-versatile"),
            tools=NEPSE_TOOLS,
            instructions=[
                "Use tables to display data",
                "Provide clear financial analysis of the Nepali stock market",
                "Include relevant metrics and statistics",
                "Format numbers properly with commas",
                "Use the NEPSE tools to get REAL live data from the Nepal Stock Exchange",
                "Prices are in Nepalese Rupees (NPR). Always state 'Rs' for amounts.",
                "Use get_stock_info() for a single stock's details, search_stock() to find a company by name",
                "Use get_top_gainers(), get_top_losers(), get_top_volume(), get_top_traded() for market movers",
                "Use get_sector_stocks() to analyze a sector (e.g. bank, insurance, hydropower, microfinance)",
                "Use get_market_overview() for the overall market snapshot",
                "If the NEPSE tool fails, say that live data is unavailable and fall back to general knowledge",
            ],
            show_tool_calls=True,
            markdown=True,
        )
        logger.info("Finance Agent initialized successfully")
        
        logger.info("Initializing Agent Team...")
        agent_team = Agent(
            name="Team Coordinator",
            model=Groq(id="llama-3.3-70b-versatile"),
            team=[web_agent, finance_agent],
            instructions=[
                "Always include sources", 
                "Use tables to display data",
                "Coordinate between agents to provide comprehensive answers",
                "If one agent fails, use the other agent's information",
                "Provide actionable insights",
                "This system analyzes the NEPALI STOCK MARKET (NEPSE)",
                "Prefer the Finance Agent's live NEPSE data for numbers",
                "Use the Web Agent for news, announcements, and company fundamentals",
                "Report prices in Nepalese Rupees (Rs/NPR)",
                "Mention that data is as per NEPSE trading date when available",
            ],
            show_tool_calls=True,
            markdown=True,
        )
        logger.info("Agent Team initialized successfully")
        
        return agent_team
        
    except Exception as e:
        logger.error(f"Error initializing agents: {str(e)}", exc_info=True)
        raise e

def process_agent_query(agent_team, query):
    """Process query with better error handling and retries"""
    try:
        logger.info(f"Attempting to process query: {query}")
        response = agent_team.run(query)
        
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in agent query: {error_msg}", exc_info=True)
        
        # Check if it's a tool use error
        if "tool_use_failed" in error_msg:
            logger.info("Tool error detected, retrying with simpler query...")
            try:
                # Retry with a simpler approach
                simplified_query = f"Provide information about {query.split('for')[-1] if 'for' in query else query}"
                logger.info(f"Simplified query: {simplified_query}")
                response = agent_team.run(simplified_query)
                
                if hasattr(response, 'content'):
                    return response.content
                else:
                    return str(response)
            except Exception as retry_error:
                logger.error(f"Retry also failed: {str(retry_error)}", exc_info=True)
                raise retry_error
        else:
            raise e


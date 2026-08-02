"""
NEPSE (Nepal Stock Exchange) data module.

Fetches live market data from the NepalIPaisa public API using only the
Python standard library (urllib). Results are cached in-memory with a
short TTL to avoid hammering the API.

Verified API endpoint:
    https://nepalipaisa.com/api/GetStockLive
"""
import json
import logging
import time
import urllib.request

logger = logging.getLogger(__name__)

API_URL = "https://nepalipaisa.com/api/GetStockLive"
CACHE_TTL_SECONDS = 60

_cache = {"timestamp": 0.0, "data": None}


def _fetch_live_data(force_refresh=False):
    """Fetch and cache the full live NEPSE dataset."""
    now = time.time()
    if (
        not force_refresh
        and _cache["data"] is not None
        and (now - _cache["timestamp"]) < CACHE_TTL_SECONDS
    ):
        return _cache["data"]

    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
        payload = json.loads(raw)
        result = payload.get("result") or {}
        data = {
            "stocks": result.get("stocks", []),
            "summary": result.get("summary", {}),
        }
        _cache["data"] = data
        _cache["timestamp"] = now
        logger.info("Fetched %d stocks from NEPSE API", len(data["stocks"]))
        return data
    except Exception as e:
        logger.error("Failed to fetch NEPSE data: %s", e, exc_info=True)
        if _cache["data"] is not None:
            logger.info("Returning stale cached NEPSE data")
            return _cache["data"]
        raise RuntimeError(f"Could not fetch NEPSE data: {e}")


def _as_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def get_market_summary():
    """Return the market summary dict (totalAmount, totalShares, totalTxns)."""
    return _fetch_live_data().get("summary", {})


def get_all_stocks():
    """Return the full list of live NEPSE stock quotes."""
    return _fetch_live_data().get("stocks", [])


def _fmt_stock(s):
    return (
        f"{s.get('stockSymbol', 'N/A')} - {s.get('companyName', '')} | "
        f"LTP: Rs {_as_float(s.get('closingPrice')):,.2f} | "
        f"Change: {_as_float(s.get('differenceRs')):+,.2f} "
        f"({_as_float(s.get('percentChange')):+.2f}%) | "
        f"Prev Close: Rs {_as_float(s.get('previousClosing')):,.2f} | "
        f"Open: Rs {_as_float(s.get('openingPrice')):,.2f} | "
        f"High: Rs {_as_float(s.get('maxPrice')):,.2f} | "
        f"Low: Rs {_as_float(s.get('minPrice')):,.2f} | "
        f"Volume: {int(_as_float(s.get('volume'))):,} | "
        f"Turnover: Rs {_as_float(s.get('amount')):,.2f} | "
        f"Txn: {int(_as_float(s.get('noOfTransactions'))):,}"
    )


def get_market_overview(limit=5):
    """Return a text summary of the NEPSE market (overview + top gainers/losers/traded)."""
    data = _fetch_live_data()
    summary = data.get("summary", {})
    stocks = data.get("stocks", [])
    if not stocks:
        return "No NEPSE data available right now."

    lines = []
    lines.append("NEPSE MARKET OVERVIEW")
    lines.append("=" * 50)
    lines.append(
        f"Total Turnover: Rs {_as_float(summary.get('totalAmount')):,.2f} | "
        f"Total Shares Traded: {int(_as_float(summary.get('totalShares'))):,} | "
        f"Total Transactions: {int(_as_float(summary.get('totalTxns'))):,}"
    )
    trade_date = stocks[0].get('tradeDate') or stocks[0].get('asOfDateString') or 'N/A'
    lines.append(f"Trade Date: {trade_date}")
    lines.append("")

    gainers = sorted(
        stocks, key=lambda x: _as_float(x.get("percentChange")), reverse=True
    )[:limit]
    losers = sorted(stocks, key=lambda x: _as_float(x.get("percentChange")))[:limit]
    by_volume = sorted(stocks, key=lambda x: _as_float(x.get("volume")), reverse=True)[:limit]
    by_turnover = sorted(stocks, key=lambda x: _as_float(x.get("amount")), reverse=True)[:limit]

    def block(title, items):
        block_lines = [title, "-" * 50]
        block_lines.extend(f"{i}. {_fmt_stock(s)}" for i, s in enumerate(items, 1))
        block_lines.append("")
        return block_lines

    lines.extend(block("TOP GAINERS", gainers))
    lines.extend(block("TOP LOSERS", losers))
    lines.extend(block("HIGHEST VOLUME", by_volume))
    lines.extend(block("HIGHEST TURNOVER", by_turnover))

    return "\n".join(lines)


def get_top_gainers(limit=10):
    """Return a text list of the top NEPSE gainers by % change."""
    stocks = _fetch_live_data().get("stocks", [])
    top = sorted(
        stocks, key=lambda x: _as_float(x.get("percentChange")), reverse=True
    )[:limit]
    lines = ["TOP NEPSE GAINERS", "-" * 50]
    lines.extend(f"{i}. {_fmt_stock(s)}" for i, s in enumerate(top, 1))
    return "\n".join(lines)


def get_top_losers(limit=10):
    """Return a text list of the top NEPSE losers by % change."""
    stocks = _fetch_live_data().get("stocks", [])
    top = sorted(stocks, key=lambda x: _as_float(x.get("percentChange")))[:limit]
    lines = ["TOP NEPSE LOSERS", "-" * 50]
    lines.extend(f"{i}. {_fmt_stock(s)}" for i, s in enumerate(top, 1))
    return "\n".join(lines)


def get_top_volume(limit=10):
    """Return a text list of NEPSE stocks with the highest traded volume."""
    stocks = _fetch_live_data().get("stocks", [])
    top = sorted(stocks, key=lambda x: _as_float(x.get("volume")), reverse=True)[:limit]
    lines = ["HIGHEST VOLUME NEPSE STOCKS", "-" * 50]
    lines.extend(f"{i}. {_fmt_stock(s)}" for i, s in enumerate(top, 1))
    return "\n".join(lines)


def get_top_traded(limit=10):
    """Return a text list of NEPSE stocks with the highest turnover (Rs)."""
    stocks = _fetch_live_data().get("stocks", [])
    top = sorted(stocks, key=lambda x: _as_float(x.get("amount")), reverse=True)[:limit]
    lines = ["HIGHEST TURNOVER NEPSE STOCKS", "-" * 50]
    lines.extend(f"{i}. {_fmt_stock(s)}" for i, s in enumerate(top, 1))
    return "\n".join(lines)


def get_stock_info(symbol):
    """Return detailed live information for a specific NEPSE stock by symbol (e.g. NABIL, NRIC)."""
    symbol = (symbol or "").strip().upper()
    stocks = _fetch_live_data().get("stocks", [])
    match = next(
        (s for s in stocks if s.get("stockSymbol", "").upper() == symbol), None
    )
    if match:
        return f"STOCK INFO: {symbol}\n" + "-" * 50 + "\n" + _fmt_stock(match)
    return f"Stock symbol '{symbol}' not found. Use search_stock() to find matching companies."


def search_stock(query):
    """Search NEPSE stocks by symbol or company name keyword and return matching quotes."""
    q = (query or "").strip().lower()
    if not q:
        return "Please provide a search keyword."
    stocks = _fetch_live_data().get("stocks", [])
    matches = [
        s
        for s in stocks
        if q in s.get("stockSymbol", "").lower() or q in s.get("companyName", "").lower()
    ][:10]
    if not matches:
        return f"No NEPSE stocks matched '{query}'."
    lines = [f"SEARCH RESULTS FOR '{query}'", "-" * 50]
    lines.extend(f"{i}. {_fmt_stock(s)}" for i, s in enumerate(matches, 1))
    return "\n".join(lines)


def get_company_list():
    """Return a text list of all NEPSE company symbols."""
    stocks = _fetch_live_data().get("stocks", [])
    symbols = sorted(s.get("stockSymbol", "") for s in stocks if s.get("stockSymbol"))
    return f"Total NEPSE companies: {len(symbols)}\n" + ", ".join(symbols)


def get_sector_stocks(sector_keyword):
    """Return live quotes for NEPSE stocks whose company name contains a sector keyword."""
    q = (sector_keyword or "").strip().lower()
    if not q:
        return "Please provide a sector keyword (e.g. 'bank', 'insurance', 'microfinance', 'hydropower')."
    stocks = _fetch_live_data().get("stocks", [])
    matches = [
        s
        for s in stocks
        if q in s.get("companyName", "").lower() or q in s.get("stockSymbol", "").lower()
    ]
    if not matches:
        return f"No NEPSE stocks matched sector keyword '{sector_keyword}'."
    lines = [
        f"SECTOR MATCHES FOR '{sector_keyword}' ({len(matches)} companies)",
        "-" * 50,
    ]
    lines.extend(f"{i}. {_fmt_stock(s)}" for i, s in enumerate(matches[:20], 1))
    return "\n".join(lines)


def get_all_stocks_table():
    """Return a list of dicts for ALL NEPSE stocks, ready for a dataframe/table."""
    stocks = _fetch_live_data().get("stocks", [])
    rows = []
    for s in stocks:
        rows.append({
            "Symbol": s.get("stockSymbol", ""),
            "Company": s.get("companyName", ""),
            "LTP (Rs)": round(_as_float(s.get("closingPrice")), 2),
            "Change (Rs)": round(_as_float(s.get("differenceRs")), 2),
            "Change (%)": round(_as_float(s.get("percentChange")), 2),
            "Open (Rs)": round(_as_float(s.get("openingPrice")), 2),
            "High (Rs)": round(_as_float(s.get("maxPrice")), 2),
            "Low (Rs)": round(_as_float(s.get("minPrice")), 2),
            "Prev Close (Rs)": round(_as_float(s.get("previousClosing")), 2),
            "Volume": int(_as_float(s.get("volume"))),
            "Turnover (Rs)": round(_as_float(s.get("amount")), 2),
            "Txn": int(_as_float(s.get("noOfTransactions"))),
        })
    return rows


def get_market_snapshot():
    """Return a structured dict snapshot of the NEPSE market for dashboard cards."""
    data = _fetch_live_data()
    summary = data.get("summary", {})
    stocks = data.get("stocks", [])
    if not stocks:
        return None
    advancers = sum(1 for s in stocks if _as_float(s.get("percentChange")) > 0)
    decliners = sum(1 for s in stocks if _as_float(s.get("percentChange")) < 0)
    unchanged = len(stocks) - advancers - decliners
    avg_change = sum(_as_float(s.get("percentChange")) for s in stocks) / len(stocks)
    top_gainer = max(stocks, key=lambda x: _as_float(x.get("percentChange")), default=None)
    top_loser = min(stocks, key=lambda x: _as_float(x.get("percentChange")), default=None)
    return {
        "total_amount": summary.get("totalAmount", 0),
        "total_shares": summary.get("totalShares", 0),
        "total_txns": summary.get("totalTxns", 0),
        "advancers": advancers,
        "decliners": decliners,
        "unchanged": unchanged,
        "avg_change": avg_change,
        "total_stocks": len(stocks),
        "top_gainer": top_gainer.get("stockSymbol") if top_gainer else None,
        "top_gainer_change": _as_float(top_gainer.get("percentChange")) if top_gainer else 0,
        "top_loser": top_loser.get("stockSymbol") if top_loser else None,
        "top_loser_change": _as_float(top_loser.get("percentChange")) if top_loser else 0,
        "trade_date": stocks[0].get('tradeDate') or stocks[0].get('asOfDateString') or 'N/A',
    }


def get_market_trend():
    """Compute a market trend snapshot (breadth + sentiment) from live data."""
    stocks = _fetch_live_data().get("stocks", [])
    if not stocks:
        return "No NEPSE data available right now."
    total = len(stocks)
    advancers = sum(1 for s in stocks if _as_float(s.get("percentChange")) > 0)
    decliners = sum(1 for s in stocks if _as_float(s.get("percentChange")) < 0)
    unchanged = total - advancers - decliners
    avg_change = sum(_as_float(s.get("percentChange")) for s in stocks) / total
    total_turnover = sum(_as_float(s.get("amount")) for s in stocks)
    total_volume = sum(_as_float(s.get("volume")) for s in stocks)

    if avg_change > 0.5:
        sentiment = "STRONGLY BULLISH"
    elif avg_change > 0:
        sentiment = "MILDLY BULLISH"
    elif avg_change > -0.5:
        sentiment = "MILDLY BEARISH"
    else:
        sentiment = "STRONGLY BEARISH"

    lines = ["NEPSE MARKET TREND ANALYSIS", "=" * 50]
    lines.append(f"Total Stocks Tracked: {total}")
    lines.append(f"Advancing: {advancers} ({advancers/total*100:.1f}%)")
    lines.append(f"Declining: {decliners} ({decliners/total*100:.1f}%)")
    lines.append(f"Unchanged: {unchanged}")
    lines.append(f"Average % Change: {avg_change:+.2f}%")
    lines.append(f"Total Volume: {int(total_volume):,} shares")
    lines.append(f"Total Turnover: Rs {total_turnover:,.2f}")
    lines.append(f"Market Sentiment: {sentiment}")
    return "\n".join(lines)


def get_sector_trends():
    """Aggregate NEPSE sector performance by matching company-name keywords."""
    stocks = _fetch_live_data().get("stocks", [])
    sectors = {
        "Commercial Banks": ["bank"],
        "Development Banks": ["development bank"],
        "Finance": ["finance"],
        "Insurance": ["insurance"],
        "Microfinance": ["laghubitta", "microfinance"],
        "Hydropower": ["hydropower", "khola", "power"],
        "Hotel & Tourism": ["hotel", "resort", "tourism"],
        "Manufacturing & Processing": ["mills", "manufacturing", "distillery", "bottlers", "cement"],
        "Trading": ["trading"],
        "Investment": ["investment"],
        "Mutual Funds": ["fund"],
    }
    lines = ["NEPSE SECTOR PERFORMANCE (average % change)", "-" * 50]
    for sector, keywords in sectors.items():
        matches = [
            s for s in stocks
            if any(k in s.get("companyName", "").lower() for k in keywords)
        ]
        if not matches:
            continue
        avg_chg = sum(_as_float(s.get("percentChange")) for s in matches) / len(matches)
        avg_turnover = sum(_as_float(s.get("amount")) for s in matches)
        lines.append(
            f"{sector}: {len(matches)} stocks | Avg {avg_chg:+.2f}% | "
            f"Turnover Rs {avg_turnover:,.2f}"
        )
    return "\n".join(lines)


def test_nepse_data():
    """Simple command-line smoke test for the module."""
    print(get_market_overview(limit=5))
    print()
    print(get_stock_info("NABIL"))
    print()
    print(search_stock("bank")[:800])
    print()
    print(get_market_trend())
    print()
    print(get_sector_trends())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_nepse_data()


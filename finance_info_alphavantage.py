import streamlit as st
import requests
import json
import time
from datetime import datetime
import pytz
import random  # For fallback mode

# Set page configuration
st.set_page_config(
    page_title="Stock Information Viewer",
    page_icon="📈",
    layout="centered"
)

# Custom CSS to improve the look and feel
st.markdown("""
<style>
    .main-header {
        font-size: 28px;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 20px;
    }
    .stock-price {
        font-size: 24px;
        font-weight: bold;
    }
    .stock-change-positive {
        font-size: 18px;
        color: #00C853;
    }
    .stock-change-negative {
        font-size: 18px;
        color: #D50000;
    }
    .info-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .data-timestamp {
        font-size: 14px;
        color: #616161;
    }
    .api-key-input {
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .fallback-message {
        background-color: #E8F5E9;
        padding: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<div class="main-header">Stock Information Viewer</div>', unsafe_allow_html=True)
st.markdown("Enter a stock symbol to get real-time information.")

# Sidebar for API key configuration
with st.sidebar:
    st.header("Configuration")
    st.write("This app can use Alpha Vantage API for live data or work in demo mode.")
    
    api_key = st.text_input("Alpha Vantage API Key (optional)", 
                           help="Get a free API key from https://www.alphavantage.co/support/#api-key")
    
    use_demo_mode = st.checkbox("Use Demo Mode", 
                               value=not api_key,
                               help="Use pre-defined stock data for demonstration")
    
    if not api_key and not use_demo_mode:
        st.warning("No API key provided. Switching to Demo Mode.")
        use_demo_mode = True

# Demo data for fallback mode
DEMO_STOCKS = {
    "AAPL": {
        "name": "Apple Inc.",
        "price": 188.5,
        "change": 2.75,
        "change_percent": 1.48
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "price": 420.2,
        "change": -1.35,
        "change_percent": -0.32
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "price": 165.8,
        "change": 1.25,
        "change_percent": 0.76
    },
    "AMZN": {
        "name": "Amazon.com Inc.",
        "price": 172.4,
        "change": -0.89,
        "change_percent": -0.51
    },
    "META": {
        "name": "Meta Platforms Inc.",
        "price": 468.15,
        "change": 5.43,
        "change_percent": 1.17
    },
    "TSLA": {
        "name": "Tesla Inc.",
        "price": 243.75,
        "change": -3.25,
        "change_percent": -1.32
    },
    "NFLX": {
        "name": "Netflix Inc.",
        "price": 628.9,
        "change": 2.15,
        "change_percent": 0.34
    },
    "JPM": {
        "name": "JPMorgan Chase & Co.",
        "price": 192.6,
        "change": 1.05,
        "change_percent": 0.55
    }
}

# Function to get stock data from Alpha Vantage
def get_alphavantage_data(symbol, api_key):
    try:
        # Check if the symbol is empty or invalid format
        if not symbol or not symbol.strip():
            return None, "Error: Please enter a valid stock symbol."
        
        if not symbol.isalnum() and '-' not in symbol and '.' not in symbol:
            return None, "Error: Stock symbol should only contain letters, numbers, hyphens, or periods."
        
        # API URL for getting stock quote
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        
        # Make the API request
        response = requests.get(url, timeout=10)
        
        # Check if the response is successful
        if response.status_code != 200:
            return None, f"Error: API returned status code {response.status_code}"
        
        # Parse the response
        data = response.json()
        
        # Check for error messages in the response
        if "Error Message" in data:
            return None, f"API Error: {data['Error Message']}"
        
        if "Note" in data and "API call frequency" in data["Note"]:
            return None, "Rate limit exceeded. Please try again later or use Demo Mode."
        
        # Extract the data from the response
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            
            # Check if the response contains the necessary data
            if not quote or "05. price" not in quote:
                return None, f"Error: No data found for symbol '{symbol}'"
            
            # Get company name (this requires another API call)
            company_name = get_company_name(symbol, api_key) or symbol
            
            # Prepare the result
            result = {
                "symbol": symbol,
                "name": company_name,
                "price": float(quote["05. price"]),
                "change": float(quote["09. change"]),
                "change_percent": float(quote["10. change percent"].strip("%"))
            }
            
            return result, None
        
        return None, f"Error: Unable to fetch data for symbol '{symbol}'"
    
    except requests.exceptions.Timeout:
        return None, "Error: Request timed out. Please try again later."
    except requests.exceptions.ConnectionError:
        return None, "Error: Connection error. Please check your internet connection."
    except requests.exceptions.RequestException as e:
        return None, f"Error: {str(e)}"
    except ValueError as e:
        return None, f"Error: Invalid response from API. {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"

# Function to get company name
def get_company_name(symbol, api_key):
    try:
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "Name" in data:
                return data["Name"]
        return None
    except:
        return None

# Function to get demo data
def get_demo_data(symbol):
    """Get demo data for the specified symbol"""
    symbol = symbol.upper()
    
    # Check if symbol exists in our demo data
    if symbol in DEMO_STOCKS:
        return DEMO_STOCKS[symbol], None
    
    # Generate random data for unknown symbols to provide a better user experience
    if symbol and symbol.isalnum():
        # Generate realistic-looking random data
        price = round(random.uniform(50, 500), 2)
        change = round(random.uniform(-10, 10), 2)
        change_percent = round((change / price) * 100, 2)
        
        return {
            "symbol": symbol,
            "name": f"{symbol} Corporation",
            "price": price,
            "change": change,
            "change_percent": change_percent
        }, None
    
    return None, f"Error: Symbol '{symbol}' not recognized in demo mode. Try AAPL, MSFT, GOOGL, etc."

# Get stock data based on mode (API or Demo)
def get_stock_data(symbol, api_key=None, use_demo=False):
    """Get stock data from API or demo mode"""
    if use_demo:
        return get_demo_data(symbol)
    else:
        return get_alphavantage_data(symbol, api_key)

# Input for stock symbol
symbol = st.text_input("Please enter a symbol:", "")
symbol = symbol.upper()

# Process when symbol is provided
if symbol:
    # Get stock data
    with st.spinner(f"Fetching data for {symbol}..."):
        stock_data, error = get_stock_data(symbol, api_key, use_demo_mode)
    
    if error:
        st.error(error)
        
        # If API error and not in demo mode, suggest demo mode
        if not use_demo_mode and "API" in error:
            st.info("Consider using Demo Mode in the sidebar if you're encountering API issues.")
    
    elif stock_data:
        # Format current timestamp
        now = datetime.now(pytz.timezone("US/Pacific"))
        formatted_time = now.strftime("%a %b %d %H:%M:%S %Z %Y")
        
        # Show demo mode notice if applicable
        if use_demo_mode:
            st.markdown("""
            <div class="fallback-message">
            <strong>Demo Mode:</strong> Showing demonstration data. For real-time data, add an Alpha Vantage API key in the sidebar.
            </div>
            """, unsafe_allow_html=True)
        
        # Display stock information
        st.markdown(f"<div class='data-timestamp'>{formatted_time}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'>", unsafe_allow_html=True)
        
        # Company name and symbol
        company_name = stock_data.get("name", symbol)
        st.markdown(f"### {company_name} ({symbol})")
        
        # Format price and change with color
        price = stock_data["price"]
        change = stock_data["change"]
        change_percent = stock_data["change_percent"]
        
        # Add + sign if change is positive
        sign = "+" if change >= 0 else ""
        change_class = "stock-change-positive" if change >= 0 else "stock-change-negative"
        
        st.markdown(f"<div class='stock-price'>${price:.2f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='{change_class}'>{sign}{change:.2f} ({sign}{change_percent:.2f}%)</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Failed to retrieve stock data. Please check the symbol and try again.")

# Display instructions if no symbol entered
else:
    st.info("Enter a stock symbol above (like AAPL, MSFT, GOOGL) and press Enter to see information.")
    
    # Show examples of common stock symbols
    st.markdown("### Common Stock Symbols")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("- **AAPL** (Apple)")
        st.markdown("- **MSFT** (Microsoft)")
        st.markdown("- **GOOGL** (Google)")
        st.markdown("- **AMZN** (Amazon)")
    with col2:
        st.markdown("- **META** (Meta/Facebook)")
        st.markdown("- **TSLA** (Tesla)")
        st.markdown("- **NFLX** (Netflix)")
        st.markdown("- **JPM** (JP Morgan Chase)")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666;">
        Python Finance Info Homework | Stock Information Viewer
    </div>
    """, 
    unsafe_allow_html=True
)

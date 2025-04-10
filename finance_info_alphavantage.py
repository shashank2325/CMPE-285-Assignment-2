import streamlit as st
import requests
from datetime import datetime
import pytz

# Set page configuration
st.set_page_config(
    page_title="Stock Information Viewer",
    page_icon="📈",
    layout="centered"
)

# API Key hardcoded - Replace this with your actual API key
API_KEY = "4Qwr6xvgmRNu9DrSs25tp5xFwpc4eJ1Z"  # Financial Modeling Prep API key

# Custom CSS
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
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<div class="main-header">Stock Information Viewer</div>', unsafe_allow_html=True)
st.markdown("Enter a stock symbol to get real-time information.")

# Function to get stock data from Financial Modeling Prep API
def get_stock_data(symbol):
    try:
        # Validate the symbol
        if not symbol or not isinstance(symbol, str):
            return None, "Error: Please enter a valid stock symbol."
        
        # Clean the symbol
        symbol = symbol.strip().upper()
        
        # Make request to Financial Modeling Prep API with API key
        url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={API_KEY}"
        response = requests.get(url, timeout=10)
        
        # Check response status
        if response.status_code != 200:
            return None, f"Error: API returned status code {response.status_code}"
        
        # Parse the response
        data = response.json()
        
        # Check if we got valid data
        if not data or len(data) == 0:
            return None, f"Error: No data found for symbol '{symbol}'. Please check the symbol."
        
        # Extract the required information
        stock_data = data[0]  # The API returns a list, but we only need the first item
        
        # Prepare the result
        result = {
            "symbol": stock_data.get("symbol", symbol),
            "name": stock_data.get("name", f"{symbol} Inc."),
            "price": stock_data.get("price", 0),
            "change": stock_data.get("change", 0),
            "change_percent": stock_data.get("changesPercentage", 0)
        }
        
        return result, None
    
    except requests.exceptions.ConnectionError:
        return None, "Error: Connection failed. Please check your internet connection."
    except requests.exceptions.Timeout:
        return None, "Error: Request timed out. The server took too long to respond."
    except Exception as e:
        return None, f"Error: {str(e)}"

# Input for stock symbol
symbol = st.text_input("Please enter a symbol:", "")

# Process when symbol is provided
if symbol:
    # Get stock data
    with st.spinner(f"Fetching data for {symbol}..."):
        stock_data, error = get_stock_data(symbol)
    
    if error:
        st.error(error)
    elif stock_data:
        # Format current timestamp
        now = datetime.now(pytz.timezone("US/Pacific"))
        formatted_time = now.strftime("%a %b %d %H:%M:%S %Z %Y")
        
        # Display stock information
        st.markdown(f"<div class='data-timestamp'>{formatted_time}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'>", unsafe_allow_html=True)
        
        # Company name and symbol
        company_name = stock_data["name"]
        st.markdown(f"### {company_name} ({stock_data['symbol']})")
        
        # Format price and change
        price = stock_data["price"]
        change = stock_data["change"]
        change_percent = stock_data["change_percent"]
        
        # Add + sign if change is positive
        sign = "+" if float(change) >= 0 else ""
        change_class = "stock-change-positive" if float(change) >= 0 else "stock-change-negative"
        
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
        Python Finance Info Homework | Data provided by Financial Modeling Prep API
    </div>
    """, 
    unsafe_allow_html=True
)

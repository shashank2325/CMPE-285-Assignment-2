import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz
import time
import requests
import traceback
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData

# Set page configuration
st.set_page_config(
    page_title="Stock Information Viewer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Alpha Vantage API Key - Get a free API key from https://www.alphavantage.co/support/#api-key
# You would need to replace this with your own API key
ALPHA_VANTAGE_API_KEY = "81YIZJRD7LSJ2L5T"  # Use 'demo' for testing, but it's very limited

# Custom CSS to improve the look and feel
st.markdown("""
<style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 20px;
    }
    .sub-header {
        font-size: 24px;
        font-weight: bold;
        color: #0D47A1;
    }
    .stock-price {
        font-size: 30px;
        font-weight: bold;
    }
    .stock-change-positive {
        font-size: 20px;
        color: #00C853;
    }
    .stock-change-negative {
        font-size: 20px;
        color: #D50000;
    }
    .info-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .data-timestamp {
        font-size: 14px;
        color: #616161;
        font-style: italic;
    }
    .api-warning {
        padding: 10px;
        background-color: #FFECB3;
        border-radius: 5px;
        margin-bottom: 10px;
        border-left: 5px solid #FFC107;
    }
    .api-error {
        padding: 10px;
        background-color: #FFEBEE;
        border-radius: 5px;
        margin-bottom: 10px;
        border-left: 5px solid #F44336;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<div class="main-header">Stock Information Viewer</div>', unsafe_allow_html=True)
st.markdown("Enter a stock symbol to get real-time information and historical data visualization.")

# API Key notice if using demo key
if ALPHA_VANTAGE_API_KEY == "demo":
    st.markdown(
        """
        <div class="api-warning">
            <strong>⚠️ API Key Notice:</strong> Using demo API key which has limited functionality.
            For full functionality, get a free API key from 
            <a href="https://www.alphavantage.co/support/#api-key" target="_blank">Alpha Vantage</a>
            and replace the ALPHA_VANTAGE_API_KEY variable in the code.
        </div>
        """, 
        unsafe_allow_html=True
    )

# Sidebar for inputs
with st.sidebar:
    st.markdown('<div class="sub-header">Stock Search</div>', unsafe_allow_html=True)
    
    # Input for stock symbol
    symbol = st.text_input("Enter Stock Symbol", value="IBM").upper()
    
    # Time period selection
    period_options = {
        "1 Day": "1d",
        "5 Days": "5d", 
        "1 Month": "1m", 
        "3 Months": "3m", 
        "6 Months": "6m", 
        "1 Year": "1y", 
        "5 Years": "5y"
    }
    
    period_display = st.selectbox("Select Time Period", list(period_options.keys()), index=3)
    period = period_options[period_display]
    
    # Interval selection
    interval_options = {
        "Daily": "daily",
        "Weekly": "weekly",
        "Monthly": "monthly"
    }
    
    # Only show intervals that make sense for the selected period
    if period in ["1d", "5d"]:
        interval_choices = [list(interval_options.keys())[0]]  # Daily only
    elif period in ["1m", "3m"]:
        interval_choices = list(interval_options.keys())[:2]  # Daily and Weekly
    else:
        interval_choices = list(interval_options.keys())  # All options
        
    interval_display = st.selectbox("Select Interval", interval_choices)
    interval = interval_options[interval_display]
    
    # Add a search button
    search_button = st.button("Get Stock Info", type="primary")
    
    # Add a note about API call limits
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This web application displays stock information and interactive charts.")
    st.markdown("Data provided by Alpha Vantage API.")
    st.markdown("Note: Alpha Vantage has a rate limit of 5 API calls per minute and 500 calls per day on the free tier.")

# Function to safely call the Alpha Vantage API with rate limiting
def safe_api_call(func, *args, **kwargs):
    """Make API calls with error handling and backoff"""
    try:
        result = func(*args, **kwargs)
        return result, None
    except requests.exceptions.ConnectionError:
        return None, "Network error: Unable to connect to Alpha Vantage. Please check your internet connection."
    except requests.exceptions.Timeout:
        return None, "Timeout error: The request to Alpha Vantage timed out. Please try again later."
    except requests.exceptions.RequestException as e:
        return None, f"Request error: {str(e)}"
    except Exception as e:
        error_message = str(e)
        # Check for rate limiting errors
        if "API call frequency" in error_message:
            return None, "Rate limit reached. Please wait a minute before trying again."
        else:
            return None, f"API Error: {error_message}"

# Function to get current stock price
@st.cache_data(ttl=60)  # Cache for 1 minute
def get_stock_price(symbol):
    try:
        # Check if the symbol is empty or invalid format
        if not symbol or not symbol.strip():
            return None, "Error: Please enter a valid stock symbol."
        
        if not symbol.isalnum():
            return None, "Error: Stock symbol should only contain letters and numbers."
        
        # Make API request with timeout to handle network issues
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        try:
            response = requests.get(url, timeout=10)  # 10 second timeout
        except requests.exceptions.ConnectionError:
            return None, "Network error: Unable to connect to Alpha Vantage. Please check your internet connection."
        except requests.exceptions.Timeout:
            return None, "Timeout error: The request to Alpha Vantage timed out. Please try again later."
        except requests.exceptions.RequestException as e:
            return None, f"Request error: {str(e)}"
        
        # Check if the response is valid JSON
        try:
            data = response.json()
        except ValueError:
            return None, "Error: Invalid response from Alpha Vantage API. The service might be down."
        
        # Check for empty response
        if not data:
            return None, "Error: Empty response from Alpha Vantage API. The service might be experiencing issues."
            
        if "Global Quote" in data and data["Global Quote"]:
            quote_data = data["Global Quote"]
            # Check if the response is empty (invalid symbol)
            if not quote_data or len(quote_data) <= 1:
                return None, f"Error: No data found for symbol '{symbol}'. Please check if the symbol is correct."
                
            if "05. price" in quote_data:
                try:
                    result = {
                        "price": float(quote_data["05. price"]),
                        "change": float(quote_data["09. change"]),
                        "change_percent": float(quote_data["10. change percent"].strip("%")) / 100,
                        "previous_close": float(quote_data["08. previous close"]),
                        "volume": int(quote_data["06. volume"]),
                        "latest_trading_day": quote_data["07. latest trading day"],
                        "open": float(quote_data["02. open"]),
                        "high": float(quote_data["03. high"]),
                        "low": float(quote_data["04. low"])
                    }
                    return result, None
                except (ValueError, TypeError) as e:
                    return None, f"Error: Could not parse stock data. {str(e)}"
        
        # Check for specific error messages
        if "Error Message" in data:
            if "Invalid API call" in data["Error Message"]:
                return None, f"Error: Invalid symbol '{symbol}'. Please enter a valid stock symbol."
            return None, data["Error Message"]
        
        if "Note" in data:
            if "API call frequency" in data["Note"]:
                return None, "Rate limit reached. Alpha Vantage allows only 5 API calls per minute on the free tier. Please wait a minute and try again."
            return None, data["Note"]
            
        # Generic error for other cases
        return None, f"Error: Could not fetch data for symbol '{symbol}'. The symbol may be invalid or there might be an issue with the API."
    except Exception as e:
        return None, f"Error: {str(e)}"

# Function to get historical stock data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_historical_data(symbol, interval="daily", outputsize="full"):
    try:
        # Check if the symbol is empty or invalid format
        if not symbol or not symbol.strip():
            return None, "Error: Please enter a valid stock symbol."
            
        # Set up TimeSeries with error handling
        try:
            ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
        except Exception as e:
            return None, f"Error initializing API connection: {str(e)}"
        
        # Call appropriate function based on interval with proper error handling
        try:
            if interval == "daily":
                data, meta_data = ts.get_daily(symbol=symbol, outputsize=outputsize)
            elif interval == "weekly":
                data, meta_data = ts.get_weekly(symbol=symbol)
            elif interval == "monthly":
                data, meta_data = ts.get_monthly(symbol=symbol)
            else:
                return None, f"Invalid interval: {interval}"
            
            # Check if data is empty
            if data.empty:
                return None, f"No historical data available for symbol '{symbol}'."
            
            # Rename columns to match our expected format
            data = data.rename(columns={
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close',
                '5. volume': 'Volume'
            })
            
            return data, None
            
        except ValueError as e:
            return None, f"Error: Invalid parameter - {str(e)}"
        except Exception as e:
            error_msg = str(e)
            if "Invalid API call" in error_msg:
                return None, f"Error: '{symbol}' is not a valid stock symbol."
            elif "API call frequency" in error_msg:
                return None, "Rate limit reached. Alpha Vantage allows only 5 API calls per minute on the free tier."
            else:
                return None, f"Error fetching historical data: {error_msg}"
    
    except requests.exceptions.ConnectionError:
        return None, "Network error: Unable to connect to Alpha Vantage. Please check your internet connection."
    except requests.exceptions.Timeout:
        return None, "Timeout error: The request to Alpha Vantage timed out. Please try again later."
    except Exception as e:
        return None, f"Error: {str(e)}"

# Function to get company overview
@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_company_overview(symbol):
    try:
        # Check if the symbol is empty
        if not symbol or not symbol.strip():
            return None, "Error: Please enter a valid stock symbol."
        
        # Make API request with timeout
        try:
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url, timeout=10)  # 10 second timeout
        except requests.exceptions.ConnectionError:
            return None, "Network error: Unable to connect to Alpha Vantage. Please check your internet connection."
        except requests.exceptions.Timeout:
            return None, "Timeout error: The request to Alpha Vantage timed out. Please try again later."
        except requests.exceptions.RequestException as e:
            return None, f"Request error: {str(e)}"
        
        # Check if the response is valid JSON
        try:
            data = response.json()
        except ValueError:
            return None, "Error: Invalid response from API. The service might be down."
        
        # Check if we got valid data
        if data and len(data) > 1 and "Symbol" in data and data["Symbol"] == symbol:
            return data, None
            
        # If data is empty or just has an error message (likely invalid symbol)
        if not data or len(data) <= 1:
            return None, f"Error: No company information found for symbol '{symbol}'. Please check if the symbol is correct."
        
        # Check for error messages
        if "Error Message" in data:
            if "Invalid API call" in data["Error Message"]:
                return None, f"Error: Invalid symbol '{symbol}'. Please enter a valid stock symbol."
            return None, data["Error Message"]
        
        if "Note" in data:
            if "API call frequency" in data["Note"]:
                return None, "Rate limit reached. Alpha Vantage allows only 5 API calls per minute on the free tier."
            return None, data["Note"]
            
        return None, f"Error: Could not fetch company data for symbol '{symbol}'."
    except Exception as e:
        return None, f"Error fetching company overview: {str(e)}"

# Function to filter historical data based on period
def filter_by_period(data, period):
    if data is None:
        return None
        
    now = datetime.now()
    
    if period == "1d":
        # Just the latest day
        return data.iloc[:1]
    elif period == "5d":
        # Last 5 trading days
        return data.iloc[:5]
    elif period == "1m":
        # Last month (approx 21 trading days)
        return data.iloc[:21]
    elif period == "3m":
        # Last 3 months (approx 63 trading days)
        return data.iloc[:63]
    elif period == "6m":
        # Last 6 months (approx 126 trading days)
        return data.iloc[:126]
    elif period == "1y":
        # Last year (approx 252 trading days)
        return data.iloc[:252]
    elif period == "5y":
        # Last 5 years (approx 1260 trading days)
        return data.iloc[:1260]
    else:
        # All data
        return data

# Function to create an interactive stock chart
def create_stock_chart(hist, symbol, period, interval):
    try:
        # Flip the dataframe to get ascending dates (Alpha Vantage returns most recent first)
        hist = hist.iloc[::-1]
        
        # Create a subplot with 2 rows
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.1, 
                            row_heights=[0.7, 0.3])
        
        # Check if required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in hist.columns for col in required_cols):
            # Use a simpler line chart if candlestick data is not available
            fig.add_trace(
                go.Scatter(
                    x=hist.index,
                    y=hist['Close'] if 'Close' in hist.columns else hist.iloc[:, 0],
                    name="Price",
                    line=dict(color='blue', width=2)
                ),
                row=1, col=1
            )
        else:
            # Add price trace
            fig.add_trace(
                go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name="Price"
                ),
                row=1, col=1
            )
            
            # Add volume trace if available
            if 'Volume' in hist.columns:
                colors = ['green' if close >= open else 'red' for open, close in zip(hist['Open'], hist['Close'])]
                fig.add_trace(
                    go.Bar(
                        x=hist.index,
                        y=hist['Volume'],
                        name="Volume",
                        marker=dict(color=colors, opacity=0.7)
                    ),
                    row=2, col=1
                )
            
            # Add moving averages if we have enough data points
            if len(hist) > 20:
                ma20 = hist['Close'].rolling(window=min(20, len(hist))).mean()
                fig.add_trace(
                    go.Scatter(
                        x=hist.index,
                        y=ma20,
                        name="20-day MA",
                        line=dict(color='orange', width=1)
                    ),
                    row=1, col=1
                )
            
            if len(hist) > 50:
                ma50 = hist['Close'].rolling(window=min(50, len(hist))).mean()
                fig.add_trace(
                    go.Scatter(
                        x=hist.index,
                        y=ma50,
                        name="50-day MA",
                        line=dict(color='purple', width=1)
                    ),
                    row=1, col=1
                )
        
        # Create properly formatted dates for the x-axis
        date_format = '%b %Y' if interval == 'monthly' else '%d %b' if interval == 'weekly' else '%d %b'
        formatted_dates = [pd.to_datetime(date).strftime(date_format) for date in hist.index]
        
        # Update layout with better formatting
        fig.update_layout(
            title=f"{symbol} Stock Price Chart ({period_display}, {interval_display})",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            height=600,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            xaxis_rangeslider_visible=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        # Fix x-axis date display
        fig.update_xaxes(
            tickmode='array',
            tickvals=hist.index[::max(1, len(hist)//10)],  # Show about 10 tick labels
            ticktext=[pd.to_datetime(date).strftime(date_format) for date in hist.index[::max(1, len(hist)//10)]],
            tickangle=-45,
            showgrid=True,
            gridcolor='rgba(211, 211, 211, 0.5)',
            row=1, col=1
        )
        
        fig.update_xaxes(
            tickmode='array',
            tickvals=hist.index[::max(1, len(hist)//10)],
            ticktext=[pd.to_datetime(date).strftime(date_format) for date in hist.index[::max(1, len(hist)//10)]],
            tickangle=-45,
            showgrid=True,
            gridcolor='rgba(211, 211, 211, 0.5)',
            row=2, col=1
        )
        
        # Update y-axis labels and grid
        fig.update_yaxes(
            title_text="Price ($)", 
            row=1, col=1,
            showgrid=True,
            gridcolor='rgba(211, 211, 211, 0.5)'
        )
        fig.update_yaxes(
            title_text="Volume", 
            row=2, col=1,
            showgrid=True,
            gridcolor='rgba(211, 211, 211, 0.5)'
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        st.error(f"Traceback: {traceback.format_exc()}")
        return None

# Main content - Only execute when search button is clicked or on first load
if search_button or 'first_load' not in st.session_state:
    st.session_state.first_load = True
    
    # Display a spinner while fetching data
    with st.spinner(f"Fetching data for {symbol}..."):
        # Validate the symbol before making API calls
        if not symbol or not symbol.strip():
            st.error("Error: Please enter a valid stock symbol.")
            display_stock_guide()
        elif not symbol.isalnum() and '-' not in symbol and '.' not in symbol:
            st.error("Error: Stock symbol should only contain letters, numbers, hyphens, or periods.")
            display_stock_guide()
        else:
            # Fetch current stock price
            price_data, price_error = get_stock_price(symbol)
            
            if price_error:
                st.error(price_error)
                # Show more helpful messages for different error types
                if "network" in price_error.lower() or "connect" in price_error.lower():
                    st.warning("⚠️ Network issue detected. Please check your internet connection and try again.")
                elif "timeout" in price_error.lower():
                    st.warning("⚠️ Server is taking too long to respond. The service might be experiencing high traffic.")
                elif "invalid symbol" in price_error.lower() or "not found" in price_error.lower():
                    st.warning(f"⚠️ '{symbol}' doesn't appear to be a valid stock symbol. Please check the spelling.")
                    display_stock_guide()
                elif "API call frequency" in price_error or "rate limit" in price_error.lower():
                    st.warning("⚠️ Alpha Vantage API rate limit reached. This free API allows only 5 calls per minute. Please wait a minute and try again.")
            elif price_data:
                # Format current timestamp
                now = datetime.now(pytz.timezone("US/Eastern"))  # Stock market uses Eastern Time
                formatted_time = now.strftime("%a %b %d %H:%M:%S %Z %Y")
                
                # Get company overview
                company_data, company_error = get_company_overview(symbol)
                if company_error and "rate limit" not in company_error.lower():
                    st.warning(f"Note: {company_error}")
                    
                company_name = company_data["Name"] if company_data and "Name" in company_data else symbol
                
                # Display main stock information
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    st.markdown(f"<div class='info-box'>", unsafe_allow_html=True)
                    st.markdown(f"### {company_name} ({symbol})")
                    
                    # Format price and change with color
                    price = price_data["price"]
                    change = price_data["change"]
                    change_percent = price_data["change_percent"]
                    
                    sign = "+" if change >= 0 else ""
                    change_class = "stock-change-positive" if change >= 0 else "stock-change-negative"
                    
                    st.markdown(f"<div class='stock-price'>${price:.2f}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='{change_class}'>{sign}{change:.2f} ({sign}{change_percent:.2f}%)</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='data-timestamp'>Last updated: {formatted_time}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='data-timestamp'>Last trading day: {price_data['latest_trading_day']}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Key Statistics
                    st.markdown("<div class='sub-header'>Key Statistics</div>", unsafe_allow_html=True)
                    
                    # Create two columns for statistics
                    stat_col1, stat_col2 = st.columns(2)
                    
                    # Display today's trading statistics
                    with stat_col1:
                        st.write(f"**Previous Close:** ${price_data['previous_close']:.2f}")
                        st.write(f"**Open:** ${price_data['open']:.2f}")
                        st.write(f"**Day High:** ${price_data['high']:.2f}")
                        st.write(f"**Day Low:** ${price_data['low']:.2f}")
                        st.write(f"**Volume:** {int(price_data['volume']):,}")
                    
                    # Display company fundamentals if available
                    with stat_col2:
                        if company_data:
                            if "MarketCapitalization" in company_data and company_data["MarketCapitalization"]:
                                market_cap = int(company_data["MarketCapitalization"])
                                if market_cap > 1000000000:
                                    st.write(f"**Market Cap:** ${market_cap/1000000000:.2f}B")
                                else:
                                    st.write(f"**Market Cap:** ${market_cap/1000000:.2f}M")
                            
                            if "PERatio" in company_data and company_data["PERatio"] and company_data["PERatio"] != "None":
                                st.write(f"**P/E Ratio:** {company_data['PERatio']}")
                                
                            if "EPS" in company_data and company_data["EPS"] and company_data["EPS"] != "None":
                                st.write(f"**EPS:** ${float(company_data['EPS']):.2f}")
                                
                            if "DividendYield" in company_data and company_data["DividendYield"] and company_data["DividendYield"] != "None":
                                dividend_yield = float(company_data["DividendYield"]) * 100
                                st.write(f"**Dividend Yield:** {dividend_yield:.2f}%")
                                
                            if "52WeekHigh" in company_data and company_data["52WeekHigh"]:
                                st.write(f"**52 Week High:** ${float(company_data['52WeekHigh']):.2f}")
                                
                            if "52WeekLow" in company_data and company_data["52WeekLow"]:
                                st.write(f"**52 Week Low:** ${float(company_data['52WeekLow']):.2f}")
                
                with col2:
                    # Get historical data
                    hist_data, hist_error = get_historical_data(symbol, interval)
                    
                    if hist_error:
                        st.error(f"Error fetching historical data: {hist_error}")
                        # Show placeholder message
                        st.info("Historical data unavailable. This could be due to API limitations or an invalid symbol.")
                    elif hist_data is not None:
                        # Filter data based on selected period
                        filtered_data = filter_by_period(hist_data, period)
                        
                        if filtered_data is not None and not filtered_data.empty:
                            # Create and display the stock chart
                            fig = create_stock_chart(filtered_data, symbol, period, interval)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error("No historical data available for the selected period and interval.")
                            # Show placeholder message
                            st.info("Try selecting a different time period or interval.")
                    else:
                        st.error("Failed to retrieve historical data.")
                        # Show placeholder message
                        st.info("Please check your internet connection and try again later.")
                
                # Display company information if available
                if company_data:
                    st.markdown("<div class='sub-header'>About the Company</div>", unsafe_allow_html=True)
                    
                    # Company description
                    if "Description" in company_data and company_data["Description"]:
                        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
                        st.write(company_data["Description"])
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Additional company info in columns
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if "Sector" in company_data and company_data["Sector"]:
                            st.write("**Sector:**", company_data["Sector"])
                    
                    with col2:
                        if "Industry" in company_data and company_data["Industry"]:
                            st.write("**Industry:**", company_data["Industry"])
                    
                    with col3:
                        if "FullTimeEmployees" in company_data and company_data["FullTimeEmployees"]:
                            st.write("**Employees:**", f"{int(company_data['FullTimeEmployees']):,}")
                    
                    with col4:
                        if "Exchange" in company_data and company_data["Exchange"]:
                            st.write("**Exchange:**", company_data["Exchange"])
            else:
                st.error("Failed to retrieve stock data. Please check the symbol and try again.")
                st.info("Try entering a valid stock symbol like AAPL, MSFT, GOOGL, or IBM.")
                display_stock_guide()

# Function to display stock guide - avoiding duplicate code
def display_stock_guide():
    # Display basic info about the app if no data is available
    st.markdown("### Getting Started")
    st.markdown("""
    1. Enter a valid stock symbol in the sidebar
    2. Select a time period and interval
    3. Click the "Get Stock Info" button
    """)
    
    st.markdown("### Common Stock Symbols")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**Tech:**")
        st.markdown("- AAPL (Apple)")
        st.markdown("- MSFT (Microsoft)")
        st.markdown("- GOOGL (Alphabet)")
    with col2:
        st.markdown("**Retail:**")
        st.markdown("- AMZN (Amazon)")
        st.markdown("- WMT (Walmart)")
        st.markdown("- TGT (Target)")
    with col3:
        st.markdown("**Finance:**")
        st.markdown("- JPM (JP Morgan)")
        st.markdown("- BAC (Bank of America)")
        st.markdown("- V (Visa)")
    with col4:
        st.markdown("**Entertainment:**")
        st.markdown("- NFLX (Netflix)")
        st.markdown("- DIS (Disney)")
        st.markdown("- CMCSA (Comcast)")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666;">
        Developed for CMPE 285 Assignment 2 | Data provided by Alpha Vantage API
    </div>
    """, 
    unsafe_allow_html=True
) 
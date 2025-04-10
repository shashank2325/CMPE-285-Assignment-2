# Python Stock Information Viewer

A comprehensive stock information application with CLI, GUI, and web interfaces that displays real-time stock data and visualizations.

## Features

### Command-Line Version (`finance_info.py`)
- Real-time stock information from Yahoo Finance
- Colorful terminal output with visual indicators for price changes
- ASCII chart displaying stock price trends over the last 5 days
- Key statistics presented in a clean table format
- Company business summary
- User-friendly interface with clear prompts

### GUI Version (`finance_info_gui.py`)
- Graphical user interface using Tkinter
- Interactive stock price charts with matplotlib
- Adjustable time periods (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
- Tabbed interface with key statistics and company information
- Color-coded price changes for quick visual understanding
- Responsive layout that adapts to window resizing

### Web Application Versions
#### Yahoo Finance Version (`finance_info_web.py`)
- Modern web interface using Streamlit
- Interactive candlestick charts with Plotly
- Advanced technical indicators (moving averages)
- Customizable time periods and intervals
- Responsive design that works on desktops, tablets, and mobile devices
- Beautiful styling with custom CSS
- Data caching for improved performance
- Fallback to simulated data when API is unavailable

#### Alpha Vantage Version (`finance_info_alphavantage.py`)
- Alternative API source using Alpha Vantage (more reliable)
- Real-time stock quotes and historical data
- Company fundamentals and financial metrics
- All the visualization features of the Streamlit interface
- Candlestick charts with volume indicators
- Enhanced error handling and rate limit management
- Ideal for users experiencing issues with Yahoo Finance API

## Requirements

The application requires the following Python packages:
- yfinance (Yahoo Finance version)
- alpha_vantage (Alpha Vantage version)
- colorama (CLI version)
- tabulate (CLI version)
- matplotlib
- pandas
- pytz
- tkinter (GUI version)
- streamlit (Web versions)
- plotly (Web versions)

## Installation

```bash
pip install -r requirements.txt
```

Note: Tkinter comes pre-installed with most Python distributions. If not, you may need to install it separately.

## Usage

### Command-Line Version

Run the CLI program with:

```bash
python finance_info.py
```

Enter a valid stock symbol (like AAPL, MSFT, GOOGL) when prompted.

### GUI Version

Run the GUI program with:

```bash
python finance_info_gui.py
```

1. Enter a stock symbol in the input field
2. Select a time period from the dropdown
3. Click "Get Info" or press Enter

### Web Application Versions

#### Yahoo Finance Version
```bash
streamlit run finance_info_web.py
```

#### Alpha Vantage Version (Recommended)
```bash
streamlit run finance_info_alphavantage.py
```

For the Alpha Vantage version, you should:
1. Get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Replace the `ALPHA_VANTAGE_API_KEY` variable in the code with your key
3. Follow the on-screen instructions to use the application

Both web versions will start a local web server and automatically open your browser to display the application. You can also deploy these versions to Streamlit Cloud or other hosting services for public access.

## API Keys

- The Yahoo Finance API doesn't require an API key but has reliability issues
- The Alpha Vantage API requires a free API key which you can get from their website
- The free Alpha Vantage API key allows 5 API calls per minute and 500 calls per day

## Sample Output

### Command-Line Version
```
Mon Oct 21 15:23:48 PDT 2023

Apple Inc. (AAPL)
173.44 +2.60 (+1.52%)

Key Statistics:
---------------
Previous Close    171.23
Open              172.30
Day Low           171.96
Day High          174.24
...

Price Chart for AAPL (Last 5d)
$176.23
▓▓▓▓
  ▓▓▓
   ▓▓▓
    ▓▓▓
$170.45

About Apple Inc.:
Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide...
```

### GUI Version
The GUI version displays an interactive window with:
- Stock symbol and current price at the top
- Interactive stock price chart in the middle
- Tabbed interface at the bottom with Key Statistics and About information

### Web Application Versions
Both web app versions feature:
- A clean, modern interface with sidebar navigation
- Interactive candlestick chart with volume indicator
- Detailed company information and statistics
- Color-coded price changes (green for positive, red for negative)
- Mobile-responsive design that works on any device

## Choosing Between API Options

- If you need frequent updates or large amounts of historical data, use the Alpha Vantage version
- If you need quick access without API key setup, try the Yahoo Finance version
- The Yahoo Finance version provides fallback simulated data when the API is unavailable
- The Alpha Vantage version is generally more reliable but has stricter rate limits

## Assignment Information

This program was developed as part of CMPE 285 Assignment 2, focusing on Python networking programming to retrieve and display financial data. 
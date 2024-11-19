from datetime import datetime, timedelta

# File paths
EXCEL_FILE_PATH = "Working Sheet - Shameless Cloner Strategy.xlsx"
SIMULATION_STATE_FILE = "simulation_state.json"

# Sheet names (exact matches from your Excel file)
DATA_DUMP_SHEET = "1. Data Dump"
STOCK_LIST_SHEET = "3. List of 57 High Conviction S"
ENTRY_EXIT_SHEET = "4. Entry & Exit Points"

# Trading parameters
INVESTMENT_PER_TRADE = 10000
INITIAL_CAPITAL = 300000

# Simulation settings
SIMULATION_START_DATE = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
MARKET_OPEN_TIME = timedelta(hours=9, minutes=15)
MARKET_CLOSE_TIME = timedelta(hours=15, minutes=30)
MARKET_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

# Performance metrics
METRICS_TO_TRACK = [
    'total_trades',
    'profitable_trades',
    'success_rate',
    'final_capital',
    'profit_loss',
    'max_drawdown',
    'sharpe_ratio',
    'win_loss_ratio'
]
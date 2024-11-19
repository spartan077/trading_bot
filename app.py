from flask import Flask, render_template, jsonify, request, make_response
from data_loader import DataLoader
from trading_simulator import TradingSimulator
from simulation_state import SimulationStateManager
import pandas as pd
from config import *
from datetime import datetime
import os

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)

# Initialize global objects
loader = DataLoader()
state_manager = SimulationStateManager()
simulator = TradingSimulator(state_manager)

# CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Add OPTIONS method handler for all routes
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return make_response('', 200)

def clean_price(value):
    """Convert price string to float, handling special cases"""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        if value.strip() == '-' or value.strip() == '':
            return 0.0
        return float(value.replace(',', ''))
    return 0.0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/metrics')
def get_metrics():
    return jsonify(simulator.calculate_advanced_metrics())

@app.route('/api/trades')
def get_trades():
    return jsonify(state_manager.state['trades'])

@app.route('/api/chart_data')
def get_chart_data():
    trades_df = pd.DataFrame(state_manager.state['trades'])
    data = {
        'dates': [],
        'capital': [],
        'profits': [],
        'trade_counts': []
    }
    
    if not trades_df.empty:
        daily_data = trades_df.groupby(pd.to_datetime(trades_df['date']).dt.date).agg({
            'capital_remaining': 'last',
            'profit': 'sum',
            'type': 'count'
        }).reset_index()
        
        data = {
            'dates': daily_data['date'].tolist(),
            'capital': daily_data['capital_remaining'].tolist(),
            'profits': daily_data['profit'].tolist(),
            'trade_counts': daily_data['type'].tolist()
        }
    
    return jsonify(data)

@app.route('/api/start_simulation', methods=['GET', 'POST'])
def start_simulation():
    if not loader.load_excel_data():
        return jsonify({"status": "error", "error": "Failed to load data"})
    
    try:
        stock_data = loader.get_stock_data()
        entry_exit_rules = loader.get_entry_exit_rules()
        
        for index, row in stock_data.iterrows():
            try:
                price = clean_price(row['Holding Value in crores'])
                if price <= 0:
                    continue
                    
                signal = simulator.process_trade_signal(row, entry_exit_rules)
                if signal != 'hold':
                    quantity = int(INVESTMENT_PER_TRADE/price) if price > 0 else 0
                    if quantity > 0:
                        simulator.execute_trade(
                            stock=row['Name of Company'],
                            price=price,
                            trade_type=signal,
                            quantity=quantity,
                            date=datetime.now()
                        )
            except Exception as e:
                print(f"Error processing row {index}: {str(e)}")
                continue
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/api/reset_simulation', methods=['GET', 'POST'])
def reset_simulation():
    try:
        global simulator, state_manager
        state_manager = SimulationStateManager()
        simulator = TradingSimulator(state_manager)
        
        if os.path.exists(SIMULATION_STATE_FILE):
            os.remove(SIMULATION_STATE_FILE)
        
        return jsonify({"status": "success", "message": "Simulation reset successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/set_capital', methods=['POST', 'OPTIONS'])
def set_capital():
    if request.method == 'OPTIONS':
        return make_response('', 200)
        
    try:
        data = request.get_json()
        capital = data.get('capital', INITIAL_CAPITAL)
        
        global simulator, state_manager
        state_manager = SimulationStateManager(initial_capital=capital)
        simulator = TradingSimulator(state_manager)
        
        return jsonify({"status": "success", "message": "Capital set successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}) 
from data_loader import DataLoader
from trading_simulator import TradingSimulator
import pandas as pd

def main():
    # Initialize data loader
    loader = DataLoader()
    if not loader.load_excel_data():
        print("Failed to load data. Exiting...")
        return
        
    # Initialize simulator
    simulator = TradingSimulator()
    
    # Get data
    stock_data = loader.get_stock_data()
    stock_list = loader.get_stock_list()
    entry_exit_rules = loader.get_entry_exit_rules()
    
    # Process each row in the data
    for index, row in stock_data.iterrows():
        # Get trading signal
        signal = simulator.process_trade_signal(row, entry_exit_rules)
        
        # Execute trade based on signal
        if signal != 'hold':
            simulator.execute_trade(
                stock=row['Stock'],
                price=row['Price'],
                trade_type=signal,
                quantity=int(10000/row['Price']),  # Calculate quantity based on ₹10,000 per trade
                date=row['Date']
            )
    
    # Get and display performance metrics
    metrics = simulator.get_performance_metrics()
    print("\nPerformance Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # Save trade log to Excel
    trade_log_df = pd.DataFrame(simulator.trade_log)
    trade_log_df.to_excel('trade_log.xlsx', index=False)
    print("\nTrade log saved to trade_log.xlsx")

if __name__ == "__main__":
    main() 
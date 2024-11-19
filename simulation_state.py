import json
from datetime import datetime, timedelta
import pandas as pd
from config import *

class SimulationStateManager:
    def __init__(self, initial_capital=INITIAL_CAPITAL):
        self.initial_capital = initial_capital
        self.state = self._load_state()

    def _load_state(self):
        try:
            with open(SIMULATION_STATE_FILE, 'r') as f:
                state = json.load(f)
                if isinstance(state['last_run_date'], str):
                    state['last_run_date'] = datetime.fromisoformat(state['last_run_date'])
                return state
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'last_run_date': SIMULATION_START_DATE,
                'trades': [],
                'capital': self.initial_capital,
                'positions': {}
            }

    def save_state(self):
        state_to_save = self.state.copy()
        if isinstance(state_to_save['last_run_date'], datetime):
            state_to_save['last_run_date'] = state_to_save['last_run_date'].isoformat()
        with open(SIMULATION_STATE_FILE, 'w') as f:
            json.dump(state_to_save, f, indent=4)

    def reset_state(self):
        """Reset the state to initial values"""
        self.state = {
            'last_run_date': SIMULATION_START_DATE,
            'trades': [],
            'capital': self.initial_capital,
            'positions': {}
        }
        self.save_state()

    def get_simulation_dates(self):
        """Returns dates to simulate since last run"""
        if isinstance(self.state['last_run_date'], str):
            last_run = datetime.fromisoformat(self.state['last_run_date'])
        else:
            last_run = self.state['last_run_date']
            
        current_date = datetime.now()
        
        dates_to_simulate = []
        current = last_run
        
        while current <= current_date:
            if current.strftime('%A') in MARKET_DAYS:
                dates_to_simulate.append(current)
            current += timedelta(days=1)
            
        return dates_to_simulate

    def update_state(self, date, trades, capital, positions):
        self.state['last_run_date'] = date
        self.state['trades'].extend(trades)
        self.state['capital'] = capital
        self.state['positions'] = positions
        self.save_state() 
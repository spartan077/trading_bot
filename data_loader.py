import pandas as pd
from config import *

class DataLoader:
    def __init__(self):
        self.excel_file = None
        self.data_dump = None
        self.stock_list = None
        self.entry_exit_rules = None

    def load_excel_data(self):
        try:
            print(f"Attempting to load Excel file: {EXCEL_FILE_PATH}")
            # Load all sheets
            self.excel_file = pd.ExcelFile(EXCEL_FILE_PATH)
            
            # Print available sheets for debugging
            print(f"Available sheets in Excel file: {self.excel_file.sheet_names}")
            
            # Load Data Dump sheet
            try:
                self.data_dump = pd.read_excel(
                    self.excel_file,
                    sheet_name=DATA_DUMP_SHEET
                )
                print("Successfully loaded Data Dump sheet")
            except Exception as e:
                print(f"Error loading Data Dump sheet: {str(e)}")
                return False
            
            # Load Stock List sheet
            try:
                self.stock_list = pd.read_excel(
                    self.excel_file,
                    sheet_name=STOCK_LIST_SHEET
                )
                print("Successfully loaded Stock List sheet")
            except Exception as e:
                print(f"Error loading Stock List sheet: {str(e)}")
                return False
            
            # Load Entry Exit Rules sheet
            try:
                self.entry_exit_rules = pd.read_excel(
                    self.excel_file,
                    sheet_name=ENTRY_EXIT_SHEET
                )
                print("Successfully loaded Entry Exit Rules sheet")
            except Exception as e:
                print(f"Error loading Entry Exit Rules sheet: {str(e)}")
                return False
            
            return True
            
        except FileNotFoundError:
            print(f"Excel file not found at path: {EXCEL_FILE_PATH}")
            return False
        except Exception as e:
            print(f"Error loading Excel data: {str(e)}")
            return False

    def get_stock_data(self):
        return self.data_dump

    def get_stock_list(self):
        return self.stock_list

    def get_entry_exit_rules(self):
        return self.entry_exit_rules 
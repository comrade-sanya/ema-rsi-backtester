import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
class IndicatorEngine:
    def calculate_ema(self, data: pd.Series, window: int) -> pd.Series:
        return data.ewm(span=window, adjust=False).mean()
    def calculate_rsi(self, data: pd.Series, window: int = 14) -> pd.Series:
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
class IndividualProject:
    def __init__(self, symbol: str, balance: float = 1000.0):
        self.symbol = symbol
        self.balance = balance
        self.initial_balance = balance
        self.engine = IndicatorEngine()
        self.trades = []
    def get_historical_data(self):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)
        df = yf.download(self.symbol, start=start_date, end=end_date, interval="1m")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    def find_order_blocks(self, df: pd.DataFrame):
        blocks = []
        for i in range(2, len(df) - 2):
            if df['High'].iloc[i] > df['High'].iloc[i - 1] and df['High'].iloc[i] > df['High'].iloc[i + 1]:
                blocks.append({'type': 'Supply', 'level': df['High'].iloc[i], 'index': i})
            if df['Low'].iloc[i] < df['Low'].iloc[i - 1] and df['Low'].iloc[i] < df['Low'].iloc[i + 1]:
                blocks.append({'type': 'Demand', 'level': df['Low'].iloc[i], 'index': i})
        return blocks
    def run_backtest(self, df: pd.DataFrame):
        df['ema20'] = self.engine.calculate_ema(df['Close'], 20)
        df['ema50'] = self.engine.calculate_ema(df['Close'], 50)
        df['rsi'] = self.engine.calculate_rsi(df['Close'], 14)
        active_position = None
        tp_level = 0.015
        sl_level = 0.007
        for i in range(50, len(df)):
            row = df.iloc[i]
            price = float(row['Close'])
            if active_position is None:
